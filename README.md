# Ollama inference proxy, inventory collector, and adapted dashboard

Portable monitoring bundle with example configuration. Replace example addresses and token paths for your installation; no live credentials are included.

## Requirements

Ollama, the upstream maravexa/ollama-exporter for model state, the included inference proxy, and Node Exporter's textfile collector for inventory.

## Dashboards

- `dashboards/ollama-inference-25086.json`

Import the JSON in Grafana using **Dashboards > New > Import**. Select your data source from the dashboard variable(s) at the top. Update the Prometheus job variables to match your `scrape_configs` job names; use the Instance selector when present. The dashboard's JSON is also suitable for file provisioning after you have selected or provisioned data source UIDs.

Expected default job labels:

- `ollama-inference-25086.json`: node-exporter, ollama, ollama-inference

The dashboard adapts Grafana.com dashboard 25086 revision 1. Keep attribution and check its upstream license before publication. The upstream model-state exporter is a separate project; it is not copied here.

## Monitoring code

See the code and example configuration in this folder, if present. Keep API keys and metrics bearer tokens in local secret files or another secret manager; never commit them. Scrape examples use documentation addresses and must be edited for your network.

## Before publishing

Test against the application and Grafana versions you intend to support. Add a license you choose and check attribution for upstream components. No release or Grafana catalog upload has been performed.


## Run the collectors

Install the packages in `requirements.txt` for the original streaming proxy in `src/inference_proxy.py`. It forwards native Ollama and OpenAI-compatible streaming response bytes while counting only explicit usage. Set the bind and upstream addresses in `examples/ollama-monitoring.env.example`, copy it to `/etc/default/ollama-monitoring`, and adapt the example systemd unit paths to your installation. The proxy accepts client traffic on the configured proxy port and exposes metrics separately on the metrics port. Keep both on trusted interfaces.

`src/inventory.py` polls `/api/tags` and `/api/ps` and writes a Node Exporter textfile. Enable Node Exporter's textfile collector, set its output directory in `OLLAMA_INVENTORY_OUTPUT`, and run the provided oneshot/timer units with a user that can write there. The model-state exporter in `examples/ollama-exporter.yml` is upstream `maravexa/ollama-exporter`; obtain its binary separately. Scrape the model-state exporter as job `ollama`, the proxy as `ollama-inference`, and Node Exporter as `node-exporter`, or change the dashboard job variables.

Run `python -m unittest discover -s src -p 'test_*.py'` before release. The adapted dashboard came from Grafana.com dashboard 25086 revision 1; preserve attribution and check its license.

A sample `scrape_configs` fragment is in `examples/prometheus-scrape.yml`; replace the example hosts and token paths.
