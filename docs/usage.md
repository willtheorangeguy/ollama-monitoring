# ollama-monitoring — Dashboard Usage

Import the JSON files using **Grafana → Dashboards → New → Import**. Set the data source and variables listed in [configuration](./configuration.md).

## Ollama Models & Inference

Source: [ollama-inference-25086.json](../dashboards/ollama-inference-25086.json). Refresh: `30s`.

<!-- Screenshot: after adding ollama-inference-25086.png to .github/icons/ollama-monitoring/, replace this comment with ![Ollama Models & Inference](https://raw.githubusercontent.com/willtheorangeguy/.github/main/icons/ollama-monitoring/ollama-inference-25086.png). -->

### Panels

| Panel | Type | What it shows |
|---|---|---|
| Ollama Status | stat | See the query reference below. |
| Loaded Models | stat | See the query reference below. |
| Loaded Model VRAM (API Reported) | stat | See the query reference below. |
| Latest Native Decode TPS | stat | Latest reported native Ollama response, not current throughput. OpenAI responses do not expose engine timing. Missing data stays absent. |
| Latest Native Prefill TPS | stat | Latest reported native Ollama response, not current throughput. OpenAI responses do not expose engine timing. Missing data stays absent. |
| Observed Requests Since Proxy Start | stat | Actual observed inference attempts across selected models/endpoints; includes validation requests and failed attempts. Resets on proxy restart. |
| Latest Native Decode / Prefill TPS History | timeseries | Latest reported native Ollama response, not current throughput. OpenAI responses do not expose engine timing. Missing data stays absent. |
| Observed Request Duration Percentiles | timeseries | End-to-end complete proxied response duration, including HTTP failures. Not engine-only time. |
| Eval Duration p95 (decode phase) | timeseries | Native Ollama reported engine duration only; absent for OpenAI-compatible API requests. |
| Prompt Eval Duration p95 (prefill phase) | timeseries | Native Ollama reported engine duration only; absent for OpenAI-compatible API requests. |
| Reported Token Rate (All Supported APIs) | timeseries | Reported tokens per wall-clock second over the rate window, NOT engine decode speed. Only explicitly supplied usage is counted. |
| Observed Model Transitions Since Poller Start | timeseries | Poller-observed transitions only, excluding startup-loaded models. Resets on restart; short-lived transitions can be missed. Never-observed events stay absent. |
| Requests In Flight | timeseries | See the query reference below. |
| Request Rate | timeseries | See the query reference below. |
| Installed Models | stat | See the query reference below. |
| Proxy Scrape Health | stat | See the query reference below. |
| Inventory Collection Age | stat | See the query reference below. |
| Responses Missing Reported Usage | stat | Completed successful responses lacking explicit token usage. No series means none observed yet; it is not zero-filled. OpenAI streaming clients must request usage. |
| Last Reported Usage Age | stat | Time since latest reported usage. An old value can simply mean an idle server, not a fault. |
| Installed Model Inventory | table | Live /api/tags inventory. API-reported per-model size; shared layers mean sizes do not sum to physical disk usage. Hidden when collection fails or becomes stale. |
| Metric Coverage | text | Dashboard text and guidance. |

<!-- Screenshot: add a focused panel or section image here after uploading it to .github/icons/ollama-monitoring/. -->

### Reading the results

The proxy counts explicit usage only and does not estimate missing tokens. OpenAI streaming clients must request usage. API-reported VRAM and installed model sizes are not independent physical measurements. The dashboard adapts Grafana.com dashboard 25086 revision 1; retain attribution.

### Query reference

These expressions are copied from the dashboard JSON. Grafana substitutes the dashboard variables at runtime.

#### Ollama Status

```promql
ollama_up{job="${job_ollama}",instance="$ollama_instance"} * on(instance) up{job="${job_ollama}",instance="$ollama_instance"}
```

#### Loaded Models

```promql
ollama_inventory_loaded_models{job="${job_node_exporter}",instance="$ollama_instance"} and on(instance) ((ollama_inventory_up{job="${job_node_exporter}",instance="$ollama_instance"} == 1) and on(instance) (time() - ollama_inventory_collection_timestamp_seconds{job="${job_node_exporter}",instance="$ollama_instance"} < 90))
```

#### Loaded Model VRAM (API Reported)

```promql
ollama_inventory_loaded_vram_bytes{job="${job_node_exporter}",instance="$ollama_instance"} and on(instance) ((ollama_inventory_up{job="${job_node_exporter}",instance="$ollama_instance"} == 1) and on(instance) (time() - ollama_inventory_collection_timestamp_seconds{job="${job_node_exporter}",instance="$ollama_instance"} < 90))
```

#### Latest Native Decode TPS

```promql
ollama_proxy_tokens_per_second{job="${job_ollama_inference}",instance="$ollama_instance",model=~"$model",endpoint=~"$endpoint"}
```

#### Latest Native Prefill TPS

```promql
ollama_proxy_prompt_tokens_per_second{job="${job_ollama_inference}",instance="$ollama_instance",model=~"$model",endpoint=~"$endpoint"}
```

#### Observed Requests Since Proxy Start

```promql
sum(ollama_proxy_requests_total{job="${job_ollama_inference}",instance="$ollama_instance",model=~"$model",endpoint=~"$endpoint"})
```

#### Latest Native Decode / Prefill TPS History

```promql
ollama_proxy_tokens_per_second{job="${job_ollama_inference}",instance="$ollama_instance",model=~"$model",endpoint=~"$endpoint"}
ollama_proxy_prompt_tokens_per_second{job="${job_ollama_inference}",instance="$ollama_instance",model=~"$model",endpoint=~"$endpoint"}
```

#### Observed Request Duration Percentiles

```promql
histogram_quantile(0.5, sum by(le) (rate(ollama_proxy_request_duration_seconds_bucket{job="${job_ollama_inference}",instance="$ollama_instance",model=~"$model",endpoint=~"$endpoint"}[$__rate_interval])))
histogram_quantile(0.95, sum by(le) (rate(ollama_proxy_request_duration_seconds_bucket{job="${job_ollama_inference}",instance="$ollama_instance",model=~"$model",endpoint=~"$endpoint"}[$__rate_interval])))
histogram_quantile(0.99, sum by(le) (rate(ollama_proxy_request_duration_seconds_bucket{job="${job_ollama_inference}",instance="$ollama_instance",model=~"$model",endpoint=~"$endpoint"}[$__rate_interval])))
```

#### Eval Duration p95 (decode phase)

```promql
histogram_quantile(0.95, sum by(le,model) (rate(ollama_proxy_eval_duration_seconds_bucket{job="${job_ollama_inference}",instance="$ollama_instance",model=~"$model",endpoint=~"$endpoint"}[$__rate_interval])))
```

#### Prompt Eval Duration p95 (prefill phase)

```promql
histogram_quantile(0.95, sum by(le,model) (rate(ollama_proxy_prompt_eval_duration_seconds_bucket{job="${job_ollama_inference}",instance="$ollama_instance",model=~"$model",endpoint=~"$endpoint"}[$__rate_interval])))
```

#### Reported Token Rate (All Supported APIs)

```promql
sum by(model) (rate(ollama_proxy_prompt_tokens_total{job="${job_ollama_inference}",instance="$ollama_instance",model=~"$model",endpoint=~"$endpoint"}[$__rate_interval]))
sum by(model) (rate(ollama_proxy_generated_tokens_total{job="${job_ollama_inference}",instance="$ollama_instance",model=~"$model",endpoint=~"$endpoint"}[$__rate_interval]))
```

#### Observed Model Transitions Since Poller Start

```promql
ollama_model_load_events_total{job="${job_ollama}",instance="$ollama_instance",model=~"$model"} and on(instance) ((ollama_inventory_up{job="${job_node_exporter}",instance="$ollama_instance"} == 1) and on(instance) (time() - ollama_inventory_collection_timestamp_seconds{job="${job_node_exporter}",instance="$ollama_instance"} < 90))
ollama_model_unload_events_total{job="${job_ollama}",instance="$ollama_instance",model=~"$model"} and on(instance) ((ollama_inventory_up{job="${job_node_exporter}",instance="$ollama_instance"} == 1) and on(instance) (time() - ollama_inventory_collection_timestamp_seconds{job="${job_node_exporter}",instance="$ollama_instance"} < 90))
```

#### Requests In Flight

```promql
ollama_proxy_requests_in_flight{job="${job_ollama_inference}",instance="$ollama_instance",model=~"$model",endpoint=~"$endpoint"}
```

#### Request Rate

```promql
sum by(model,endpoint,status) (rate(ollama_proxy_requests_total{job="${job_ollama_inference}",instance="$ollama_instance",model=~"$model",endpoint=~"$endpoint"}[$__rate_interval]))
```

#### Installed Models

```promql
ollama_inventory_models{job="${job_node_exporter}",instance="$ollama_instance"} and on(instance) ((ollama_inventory_up{job="${job_node_exporter}",instance="$ollama_instance"} == 1) and on(instance) (time() - ollama_inventory_collection_timestamp_seconds{job="${job_node_exporter}",instance="$ollama_instance"} < 90))
```

#### Proxy Scrape Health

```promql
up{job="${job_ollama_inference}",instance="$ollama_instance"}
```

#### Inventory Collection Age

```promql
time() - ollama_inventory_collection_timestamp_seconds{job="${job_node_exporter}",instance="$ollama_instance"}
```

#### Responses Missing Reported Usage

```promql
sum(ollama_proxy_usage_missing_total{job="${job_ollama_inference}",instance="$ollama_instance",model=~"$model",endpoint=~"$endpoint"})
```

#### Last Reported Usage Age

```promql
time() - max(ollama_proxy_last_usage_timestamp_seconds{job="${job_ollama_inference}",instance="$ollama_instance",model=~"$model",endpoint=~"$endpoint"})
```

#### Installed Model Inventory

```promql
ollama_inventory_model_size_bytes{job="${job_node_exporter}",instance="$ollama_instance",model=~"$model"} and on(instance) ((ollama_inventory_up{job="${job_node_exporter}",instance="$ollama_instance"} == 1) and on(instance) (time() - ollama_inventory_collection_timestamp_seconds{job="${job_node_exporter}",instance="$ollama_instance"} < 90))
```
