# API

Client -> streaming inference proxy -> Ollama. Proxy metrics -> Prometheus. Ollama /api/tags and /api/ps -> inventory textfile -> Node Exporter -> Prometheus. Upstream model-state exporter -> Prometheus -> Grafana.

## Interfaces

- The inference proxy forwards `/api/chat`, `/api/generate`, `/v1/chat/completions`, `/v1/completions` and serves `/metrics` on a separate listener.
- The inventory collector reads Ollama `/api/tags` and `/api/ps` and writes a Node Exporter textfile.

## Prometheus scrape reference

See [examples/prometheus-scrape.yml](https://github.com/willtheorangeguy/ollama-monitoring/blob/HEAD/examples/prometheus-scrape.yml) for the target, job name and authorization settings.

## Proxy observations

The proxy records request counts by model, endpoint and status; request duration and in-flight requests; explicitly reported prompt and generated tokens; and missing usage. Native Ollama responses can also provide decode and prefill timing. Those gauges describe the latest reported response, so they are not live engine telemetry. The proxy forwards request and response bytes without writing prompts or replies to disk. See [inference_proxy.py](https://github.com/willtheorangeguy/ollama-monitoring/blob/HEAD/src/inference_proxy.py).

## Inventory textfile

The collector writes installed model count, loaded model count, per-model API-reported size and total API-reported loaded VRAM. On a failed collection it replaces the old textfile with `ollama_inventory_up 0` and a fresh collection timestamp, so stale inventory values do not survive. See [inventory.py](https://github.com/willtheorangeguy/ollama-monitoring/blob/HEAD/src/inventory.py).
