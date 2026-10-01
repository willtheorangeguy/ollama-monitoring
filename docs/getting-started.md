# Getting started

## Prerequisites

Ollama, Python packages in requirements.txt, Node Exporter textfile collector, maravexa/ollama-exporter, Prometheus and Grafana.

## Set up

Install requirements.txt. Copy examples/ollama-monitoring.env.example to /etc/default/ollama-monitoring, adjust example systemd unit paths and start the inference proxy. Enable examples/ollama-inventory.service and .timer with a writable textfile directory. Install the upstream model-state exporter separately, then adapt examples/prometheus-scrape.yml and import the dashboard.

The example Prometheus scrape job names are `ollama`, `ollama-inference`, `node-exporter`.

## Confirm data

In Prometheus, check `up{job="ollama"}`, `up{job="ollama-inference"}`, `up{job="node-exporter"}` and inspect a panel query in Grafana.
For missing data, see [Troubleshooting](troubleshooting.md).
