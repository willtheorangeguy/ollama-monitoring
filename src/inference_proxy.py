#!/usr/bin/python3
"""Streaming Ollama/OpenAI proxy. Never persists prompts, replies, or credentials."""
import asyncio
import json
import math
import signal
import time

from aiohttp import ClientSession, ClientTimeout, web
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest
from yarl import URL

ENDPOINTS = {'/api/chat', '/api/generate', '/v1/chat/completions', '/v1/completions'}
HOP = {'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
       'te', 'trailer', 'transfer-encoding', 'upgrade'}


def headers(source):
    excluded = HOP | {v.strip().lower() for v in source.get('Connection', '').split(',')}
    return [(k, v) for k, v in source.items() if k.lower() not in excluded]


def number(value):
    return not isinstance(value, bool) and isinstance(value, (float, int)) and math.isfinite(value) and value >= 0


class Observations:
    """Bounded line parser; missing usage stays missing, never estimated."""
    def __init__(self, native):
        self.native = native
        self.buffer = b''
        self.skipping = False
        self.final = None

    def line(self, raw):
        raw = raw.strip()
        if raw.startswith(b'data:'):
            raw = raw[5:].strip()
        if not raw or raw == b'[DONE]':
            return
        try:
            obj = json.loads(raw)
            if not isinstance(obj, dict):
                return
            if self.native and obj.get('done') is True:
                self.final = {k: v for k, v in obj.items() if k in (
                    'prompt_eval_count', 'eval_count', 'load_duration',
                    'prompt_eval_duration', 'eval_duration') and number(v)}
            elif not self.native and isinstance(obj.get('usage'), dict):
                self.final = {k: v for k, v in obj['usage'].items()
                              if k in ('prompt_tokens', 'completion_tokens') and number(v)}
        except (ValueError, UnicodeError):
            pass

    def feed(self, chunk):
        for index, part in enumerate(chunk.split(b'\n')):
            if index:
                if not self.skipping:
                    self.line(self.buffer)
                self.buffer, self.skipping = b'', False
            if not self.skipping:
                if len(self.buffer) + len(part) > 1024 * 1024:
                    self.buffer, self.skipping = b'', True
                else:
                    self.buffer += part

    def finish(self):
        if not self.skipping:
            self.line(self.buffer)
        self.buffer = b''


class Proxy:
    def __init__(self, upstream='http://127.0.0.1:11434'):
        self.upstream = upstream
        self.registry = CollectorRegistry()
        labels = ['model', 'endpoint']
        self.requests = Counter('ollama_proxy_requests_total', 'Observed inference requests by outcome',
                                labels + ['status'], registry=self.registry)
        self.duration = Histogram('ollama_proxy_request_duration_seconds', 'Observed end-to-end inference duration',
                                  labels, buckets=(.1, .5, 1, 2, 5, 10, 30, 60, 120, 300, 600), registry=self.registry)
        self.inflight = Gauge('ollama_proxy_requests_in_flight', 'Current inference requests', labels, registry=self.registry)
        self.prompt = Counter('ollama_proxy_prompt_tokens_total', 'Prompt tokens explicitly reported by upstream', labels, registry=self.registry)
        self.generated = Counter('ollama_proxy_generated_tokens_total', 'Generated tokens explicitly reported by upstream', labels, registry=self.registry)
        self.missing = Counter('ollama_proxy_usage_missing_total', 'Completed successful responses without reported token usage', labels, registry=self.registry)
        self.decode = Gauge('ollama_proxy_tokens_per_second', 'Latest native response eval_count / eval_duration; not OpenAI estimated throughput', labels, registry=self.registry)
        self.prefill = Gauge('ollama_proxy_prompt_tokens_per_second', 'Latest native response prompt_eval_count / prompt_eval_duration', labels, registry=self.registry)
        self.last_usage = Gauge('ollama_proxy_last_usage_timestamp_seconds', 'Time of last explicitly reported usage', labels, registry=self.registry)
        self.timings = {k: Histogram('ollama_proxy_' + k + '_seconds', 'Native Ollama reported ' + k,
                                   labels, registry=self.registry) for k in (
                                       'load_duration', 'prompt_eval_duration', 'eval_duration')}

    def record(self, parser, labels):
        data = parser.final
        if data is None:
            self.missing.labels(*labels).inc()
            return
        prompt_key, generated_key = ('prompt_eval_count', 'eval_count') if parser.native else ('prompt_tokens', 'completion_tokens')
        any_usage = False
        for key, metric in ((prompt_key, self.prompt), (generated_key, self.generated)):
            if key in data:
                metric.labels(*labels).inc(data[key])
                any_usage = True
        if any_usage:
            self.last_usage.labels(*labels).set(time.time())
        else:
            self.missing.labels(*labels).inc()
        if parser.native:
            for key, metric in self.timings.items():
                if key in data:
                    metric.labels(*labels).observe(data[key] / 1e9)
            for count, duration, metric in (
                    ('eval_count', 'eval_duration', self.decode),
                    ('prompt_eval_count', 'prompt_eval_duration', self.prefill)):
                if count in data and data.get(duration, 0) > 0:
                    metric.labels(*labels).set(data[count] * 1e9 / data[duration])

    async def startup(self, app):
        self.session = ClientSession(timeout=ClientTimeout(total=None, sock_connect=10),
                                     auto_decompress=False, trust_env=False)

    async def cleanup(self, app):
        await self.session.close()

    async def handle(self, request):
        # Preserve request bytes. Model is the only request value retained for metrics.
        body = await request.read()
        tracked = request.method == 'POST' and request.path in ENDPOINTS
        model = 'unknown'
        if tracked:
            try:
                candidate = json.loads(body).get('model')
                if isinstance(candidate, str) and 0 < len(candidate) <= 200:
                    model = candidate
            except (ValueError, AttributeError):
                pass
        labels = (model, request.path)
        parser = Observations(request.path.startswith('/api/'))
        start, status = time.monotonic(), 'transport_error'
        response = None
        completed = False
        if tracked:
            self.inflight.labels(*labels).inc()
        try:
            outgoing = [(k, v) for k, v in headers(request.headers)
                        if k.lower() not in ('host', 'content-length', 'accept-encoding')]
            outgoing.append(('Accept-Encoding', 'identity'))
            async with self.session.request(request.method,
                    URL(self.upstream + request.raw_path, encoded=True), data=body,
                    headers=outgoing, allow_redirects=False) as upstream:
                status = str(upstream.status)
                response = web.StreamResponse(status=upstream.status, headers=headers(upstream.headers))
                await response.prepare(request)
                parse = tracked and upstream.status < 300 and not upstream.headers.get('Content-Encoding')
                async for chunk in upstream.content.iter_any():
                    await response.write(chunk)
                    if parse:
                        parser.feed(chunk)
                await response.write_eof()
                completed = True
                if tracked and 200 <= upstream.status < 300:
                    parser.finish()
                    self.record(parser, labels)
                return response
        except asyncio.CancelledError:
            status = 'cancelled'
            raise
        except Exception:
            # Avoid logging response bodies, Authorization headers, query strings, or prompts.
            status = 'transport_error'
            if response is not None and response.prepared:
                response.force_close()
                if request.transport is not None:
                    request.transport.close()
                return response
            return web.Response(status=502, text='Ollama upstream unavailable')
        finally:
            if tracked:
                self.inflight.labels(*labels).dec()
                self.requests.labels(*labels, status).inc()
                if completed:
                    self.duration.labels(*labels).observe(time.monotonic() - start)

    async def metrics(self, request):
        return web.Response(body=generate_latest(self.registry),
                            headers={'Content-Type': 'text/plain; version=0.0.4; charset=utf-8'})

    def application(self):
        app = web.Application(client_max_size=64 * 1024 * 1024)
        app.on_startup.append(self.startup)
        app.on_cleanup.append(self.cleanup)
        app.router.add_route('*', '/{path:.*}', self.handle)
        return app


async def main():
    proxy = Proxy(os.getenv('OLLAMA_UPSTREAM_URL', 'http://127.0.0.1:11434'))
    runner = web.AppRunner(proxy.application(), access_log=None, shutdown_timeout=60,
                           auto_decompress=False)
    metrics = web.Application()
    metrics.router.add_get('/metrics', proxy.metrics)
    metrics_runner = web.AppRunner(metrics, access_log=None)
    await runner.setup()
    await metrics_runner.setup()
    await web.TCPSite(runner, os.getenv('OLLAMA_PROXY_BIND_ADDRESS', '127.0.0.1'), int(os.getenv('OLLAMA_PROXY_PORT', '9401'))).start()
    await web.TCPSite(metrics_runner, os.getenv('OLLAMA_METRICS_BIND_ADDRESS', '127.0.0.1'), int(os.getenv('OLLAMA_METRICS_PORT', '9402'))).start()
    stop = asyncio.Event()
    for sig in (signal.SIGINT, signal.SIGTERM):
        asyncio.get_running_loop().add_signal_handler(sig, stop.set)
    try:
        await stop.wait()
    finally:
        await runner.cleanup()
        await metrics_runner.cleanup()


if __name__ == '__main__':
    asyncio.run(main())
