# Development guide

The implementation and dashboard definitions are in the repository root. Client -> streaming inference proxy -> Ollama. Proxy metrics -> Prometheus. Ollama /api/tags and /api/ps -> inventory textfile -> Node Exporter -> Prometheus. Upstream model-state exporter -> Prometheus -> Grafana.

## Local checks

The repository CI workflow runs `python -m unittest discover -s src -p test_*.py -v`. Run it from the repository root after changing the relevant source or dashboard JSON.

When editing dashboards, export the final JSON from Grafana and keep data source variables, job names and panel descriptions in sync with [configuration](configuration.md).

[src/inference_proxy.py](https://github.com/willtheorangeguy/ollama-monitoring/blob/HEAD/src/inference_proxy.py) streams requests and responses and records only explicit upstream usage. [src/inventory.py](https://github.com/willtheorangeguy/ollama-monitoring/blob/HEAD/src/inventory.py) writes a Node Exporter textfile atomically and publishes a health metric when collection fails. The two test modules in [src/](https://github.com/willtheorangeguy/ollama-monitoring/tree/HEAD/src) cover these paths. When changing proxy parsing, preserve response bytes and keep prompts, replies and credentials out of metrics and logs.
