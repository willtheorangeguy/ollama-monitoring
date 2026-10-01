# Configuration

## Precedence

This repository combines dashboard defaults with settings for external services. It defines no shared command-line, environment variable and configuration-file override order; each external service resolves its own settings.

## Integration settings

The proxy listens on 127.0.0.1:9401 for inference traffic and 127.0.0.1:9402 for metrics by default; OLLAMA_UPSTREAM_URL points to Ollama. The inventory writes to OLLAMA_INVENTORY_OUTPUT. The upstream exporter config uses 127.0.0.1:9400. Bind addresses and ports are set in examples/ollama-monitoring.env.example.

## Dashboard variables

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `ollama-inference-25086.json / prometheus_ds` | datasource | `prometheus` | Grafana data source selected by the dashboard. |
| `ollama-inference-25086.json / job_node_exporter` | textbox | `node-exporter` | Dashboard variable whose value selects a scrape job, instance or endpoint. |
| `ollama-inference-25086.json / job_ollama` | textbox | `ollama` | Dashboard variable whose value selects a scrape job, instance or endpoint. |
| `ollama-inference-25086.json / job_ollama_inference` | textbox | `ollama-inference` | Dashboard variable whose value selects a scrape job, instance or endpoint. |
| `ollama-inference-25086.json / ollama_instance` | query | `label_values(up{job="${job_ollama}"}, instance)` | Queries the data source for available values. |
| `ollama-inference-25086.json / model` | query | `label_values(ollama_inventory_model_size_bytes{job="${job_node_exporter}",instance="$ollama_instance"}, model)` | Queries the data source for available values. |
| `ollama-inference-25086.json / endpoint` | custom | `/api/chat,/api/generate,/v1/chat/completions,/v1/completions` | Fixed list of endpoint values used by dashboard panels. |

## Prometheus jobs

The supplied [scrape example](https://github.com/willtheorangeguy/ollama-monitoring/blob/HEAD/examples/prometheus-scrape.yml) defines `ollama`, `ollama-inference`, `node-exporter`. Copy its entries into your own scrape_configs and replace documentation hostnames. Job names can change if the dashboard variables change with them.

The sample scrape jobs all use `instance: ollama`. Give the model exporter, proxy and Node Exporter the same logical `instance` label for each Ollama installation. The dashboard's `ollama_instance` variable now selects that label across all panels.

## Examples

The complete scrape job examples are in [`examples/prometheus-scrape.yml`](https://github.com/willtheorangeguy/ollama-monitoring/blob/HEAD/examples/prometheus-scrape.yml). Copy the relevant job into your Prometheus configuration and replace the example targets.
