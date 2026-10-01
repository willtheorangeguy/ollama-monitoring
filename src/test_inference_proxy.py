import asyncio
import unittest

from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
from inference_proxy import Observations, Proxy


class ParserTests(unittest.TestCase):
    def test_native_split_chunks(self):
        p = Observations(True)
        p.feed(b'{"done":false,"message":{"content":"not a metric"}}\n{"do')
        p.feed(b'ne":true,"eval_count":3,"eval_duration":1000000000}\n')
        p.finish()
        self.assertEqual(p.final, {'eval_count': 3, 'eval_duration': 1000000000})

    def test_sse_usage(self):
        p = Observations(False)
        p.feed(b'data: {"usage":{"prompt_tokens":2,"completion_tokens":4}}\n\ndata: [DONE]\n\n')
        p.finish()
        self.assertEqual(p.final, {'prompt_tokens': 2, 'completion_tokens': 4})

    def test_missing_usage_is_absent(self):
        p = Observations(False)
        p.feed(b'data: {"choices":[{"delta":{"content":"hello"}}]}\n\n')
        p.finish()
        self.assertIsNone(p.final)

    def test_invalid_fields_and_bounded_parser(self):
        p = Observations(True)
        p.feed(b'x' * (1024 * 1024 + 1) + b'\n{"done":true,"eval_count":-1,"prompt_eval_count":true}\n')
        p.finish()
        self.assertEqual(p.final, {})


class StreamingTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.release = asyncio.Event()
        self.first = b'{"done":false,"response":"first"}\n'
        self.final = b'{"done":true,"eval_count":3,"prompt_eval_count":2,"eval_duration":1000000000}\n'
        async def handle(request):
            body = await request.read()
            if request.path == '/api/chat':
                response = web.StreamResponse(headers={'Content-Type': 'application/x-ndjson'})
                await response.prepare(request)
                await response.write(self.first)
                await self.release.wait()
                await response.write(self.final)
                await response.write_eof()
                return response
            if request.path == '/v1/chat/completions':
                if b'"stream": true' in body:
                    response = web.StreamResponse(headers={'Content-Type': 'text/event-stream'})
                    await response.prepare(request)
                    await response.write(b'data: {"choices":[{"delta":{"content":"first"}}]}\n\n')
                    await self.release.wait()
                    await response.write(b'data: {"usage":{"prompt_tokens":7,"completion_tokens":9}}\n\ndata: [DONE]\n\n')
                    await response.write_eof()
                    return response
                return web.json_response({'usage': {'prompt_tokens': 7, 'completion_tokens': 9}})
            return web.Response(status=418, body=body, headers={'X-Test-Query': request.query_string})
        app = web.Application()
        app.router.add_route('*', '/{path:.*}', handle)
        self.upstream = TestServer(app)
        await self.upstream.start_server()
        self.proxy = Proxy(str(self.upstream.make_url('/')).rstrip('/'))
        self.client = TestClient(TestServer(self.proxy.application()))
        await self.client.start_server()

    async def asyncTearDown(self):
        self.release.set()
        await self.client.close()
        await self.upstream.close()

    async def test_stream_arrives_before_final_and_matches_bytes(self):
        response = await self.client.post('/api/chat', json={'model': 'test-model'})
        first = await asyncio.wait_for(response.content.readline(), 1)
        self.assertEqual(first, self.first)
        self.assertFalse(self.release.is_set())
        self.release.set()
        rest = await response.read()
        self.assertEqual(first + rest, self.first + self.final)
        await asyncio.sleep(.02)
        self.assertEqual(self.proxy.registry.get_sample_value('ollama_proxy_generated_tokens_total',
                         {'model': 'test-model', 'endpoint': '/api/chat'}), 3)

    async def test_openai_usage(self):
        r = await self.client.post('/v1/chat/completions', json={'model': 'test-model'})
        self.assertEqual((await r.json())['usage']['completion_tokens'], 9)
        await asyncio.sleep(.02)
        self.assertEqual(self.proxy.registry.get_sample_value('ollama_proxy_prompt_tokens_total',
                         {'model': 'test-model', 'endpoint': '/v1/chat/completions'}), 7)
        self.assertIsNone(self.proxy.registry.get_sample_value('ollama_proxy_tokens_per_second',
                         {'model': 'test-model', 'endpoint': '/v1/chat/completions'}))

    async def test_error_passthrough_and_query_preserved(self):
        r = await self.client.post('/other?one=1&two=2', data=b'unchanged-body')
        self.assertEqual(r.status, 418)
        self.assertEqual(await r.read(), b'unchanged-body')
        self.assertEqual(r.headers['X-Test-Query'], 'one=1&two=2')
        self.assertIsNone(self.proxy.registry.get_sample_value('ollama_proxy_requests_total',
                         {'model': 'unknown', 'endpoint': '/other', 'status': '418'}))

    async def test_sse_is_streamed_not_buffered(self):
        r = await self.client.post('/v1/chat/completions', json={'model': 'test-model', 'stream': True})
        first = await asyncio.wait_for(r.content.readline(), 1)
        self.assertTrue(first.startswith(b'data:'))
        self.assertFalse(self.release.is_set())
        self.release.set()
        self.assertIn(b'[DONE]', await r.read())
        await asyncio.sleep(.02)
        self.assertEqual(self.proxy.registry.get_sample_value('ollama_proxy_generated_tokens_total',
                         {'model': 'test-model', 'endpoint': '/v1/chat/completions'}), 9)

    async def test_disconnect_does_not_invent_usage(self):
        r = await self.client.post('/api/chat', json={'model': 'test-model'})
        await r.content.readline()
        r.close()
        self.release.set()
        await asyncio.sleep(.05)
        self.assertEqual(self.proxy.registry.get_sample_value('ollama_proxy_requests_in_flight',
                         {'model': 'test-model', 'endpoint': '/api/chat'}), 0)
        self.assertIsNone(self.proxy.registry.get_sample_value('ollama_proxy_generated_tokens_total',
                         {'model': 'test-model', 'endpoint': '/api/chat'}))


if __name__ == '__main__':
    unittest.main()
