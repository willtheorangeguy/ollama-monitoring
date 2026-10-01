# Installation

## Requirements

Ollama, Python packages in requirements.txt, Node Exporter textfile collector, maravexa/ollama-exporter, Prometheus and Grafana.

## Procedure

Install requirements.txt. Copy examples/ollama-monitoring.env.example to /etc/default/ollama-monitoring, adjust example systemd unit paths and start the inference proxy. Enable examples/ollama-inventory.service and .timer with a writable textfile directory. Install the upstream model-state exporter separately, then adapt examples/prometheus-scrape.yml and import the dashboard.

The files under [examples](https://github.com/willtheorangeguy/ollama-monitoring/tree/HEAD/examples) are reference configuration. Replace example addresses, token paths and bind addresses for your deployment.

Next, review [configuration](configuration.md) and [dashboard usage](usage.md).

## Verify the installation

Check that the configured scrape target is healthy in Prometheus, then import the dashboard in Grafana and confirm its panels return data. Use the target and label names documented in [Getting started](getting-started.md).

## Upgrading

Update the dashboard JSON from this repository when you adopt a newer version. Update any exporter or monitored service using that project's upgrade instructions.

## Uninstalling

Remove the dashboard from Grafana and remove only the scrape or deployment entries you added for this project. Keep shared monitoring services that other dashboards use.
