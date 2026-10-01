# ollama-monitoring — Architecture

Client -> streaming inference proxy -> Ollama. Proxy metrics -> Prometheus. Ollama /api/tags and /api/ps -> inventory textfile -> Node Exporter -> Prometheus. Upstream model-state exporter -> Prometheus -> Grafana.

## Components

- [dashboards/](../dashboards): Grafana dashboard definitions
- [examples/](../examples): deployment and scrape examples
- [src/](../src): collector or proxy implementation

## Data interpretation

The proxy counts explicit usage only and does not estimate missing tokens. OpenAI streaming clients must request usage. API-reported VRAM and installed model sizes are not independent physical measurements. The dashboard adapts Grafana.com dashboard 25086 revision 1; retain attribution.
