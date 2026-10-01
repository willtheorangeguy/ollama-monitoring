# Ollama Monitoring

A streaming inference proxy, a Node Exporter inventory collector, an upstream model-state exporter configuration, and an adapted Grafana dashboard.

## Key features

- Streaming inference proxy with request and explicit usage metrics.
- Installed and loaded model inventory from Ollama APIs.
- Model state exporter and Node Exporter integration.
- Adapted inference Grafana dashboard.

## Quick start

Open Grafana and import `dashboards/ollama-inference-25086.json` through **Dashboards → New → Import**. Select the configured data source and match the dashboard variables to your labels. See [Getting started](getting-started.md) for prerequisites and setup.

## Where to next

<div class="wt-grid" markdown>

[:material-rocket-launch: **Getting started**<br>Set up the required integrations](getting-started.md){ .wt-card }

[:material-download: **Installation**<br>Install and connect the required services](installation.md){ .wt-card }

[:material-tune: **Configuration**<br>Review scrape examples and dashboard variables](configuration.md){ .wt-card }

[:material-sitemap: **Architecture**<br>Follow metrics from source to dashboard](architecture.md){ .wt-card }

[:material-view-dashboard: **Dashboard usage**<br>Import and use the dashboard](usage.md){ .wt-card }

</div>

## Support

{{ support() }}
