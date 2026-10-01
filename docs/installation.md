# ollama-monitoring — Installation

## Requirements

Ollama, Python packages in requirements.txt, Node Exporter textfile collector, maravexa/ollama-exporter, Prometheus and Grafana.

## Procedure

Install requirements.txt. Copy examples/ollama-monitoring.env.example to /etc/default/ollama-monitoring, adjust example systemd unit paths and start the inference proxy. Enable examples/ollama-inventory.service and .timer with a writable textfile directory. Install the upstream model-state exporter separately, then adapt examples/prometheus-scrape.yml and import the dashboard.

The files under [examples](../examples) are reference configuration. Replace example addresses, token paths and bind addresses for your deployment.

Next, review [configuration](./configuration.md) and [dashboard usage](./usage.md).
