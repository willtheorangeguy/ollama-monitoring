# ollama-monitoring — Troubleshooting

| Symptom | Check |
|---|---|
| Proxy metrics empty | send client inference through port 9401, not directly to Ollama. |
| Inventory age rising | inspect the timer and textfile permissions. |
| OpenAI token panels blank | request streaming usage from the client. |

## First checks

Check the selected Grafana data source and dashboard variables in [configuration](./configuration.md). For Prometheus, inspect the target state and the exact job and instance labels before changing panel queries.
