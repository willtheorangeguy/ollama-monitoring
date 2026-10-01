<h1 align="center">ollama-monitoring</h1>
<h4 align="center">A streaming inference proxy, a Node Exporter inventory collector, an upstream model-state exporter configuration, and an adapted Grafana dashboard.</h4>

<div align="center">
  <img alt="GitHub Issues" src="https://img.shields.io/github/issues/willtheorangeguy/ollama-monitoring">
  <img alt="GitHub Pull Requests" src="https://img.shields.io/github/issues-pr/willtheorangeguy/ollama-monitoring">
  <img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-blue">
  <img alt="gitleaks workflow" src="https://github.com/willtheorangeguy/ollama-monitoring/actions/workflows/gitleaks.yml/badge.svg">
  <img alt="testing workflow" src="https://github.com/willtheorangeguy/ollama-monitoring/actions/workflows/testing.yml/badge.svg">
</div>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#documentation">Documentation</a> •
  <a href="#support">Support</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#license">License</a>
</p>

<!-- Screenshot: after adding ollama-monitoring/overview.png to .github/icons/, replace this comment with ![Dashboard overview](https://raw.githubusercontent.com/willtheorangeguy/.github/main/icons/ollama-monitoring/overview.png). -->

A streaming inference proxy, a Node Exporter inventory collector, an upstream model-state exporter configuration, and an adapted Grafana dashboard.

## Key Features

- Streaming inference proxy with request and explicit usage metrics.
- Installed and loaded model inventory from Ollama APIs.
- Model state exporter and Node Exporter integration.
- Adapted inference Grafana dashboard.

## Installation

Ollama, Python packages in requirements.txt, Node Exporter textfile collector, maravexa/ollama-exporter, Prometheus and Grafana. Install requirements.txt. Copy examples/ollama-monitoring.env.example to /etc/default/ollama-monitoring, adjust example systemd unit paths and start the inference proxy. Enable examples/ollama-inventory.service and .timer with a writable textfile directory. Install the upstream model-state exporter separately, then adapt examples/prometheus-scrape.yml and import the dashboard. See [installation](docs/installation.md) for more detail.

## Usage

Import [ollama-inference-25086.json](dashboards/ollama-inference-25086.json) in Grafana using **Dashboards → New → Import**. Choose the data source and match the dashboard variables to your monitoring labels. See [dashboard usage](docs/usage.md).

## Documentation

Full documentation lives in [docs/](docs/index.md): [Quickstart](docs/getting-started.md) · [Configuration](docs/configuration.md) · [Architecture](docs/architecture.md) · [Dashboard usage](docs/usage.md) · [Troubleshooting](docs/troubleshooting.md).

## Support

Open a [GitHub Discussion](https://github.com/willtheorangeguy/ollama-monitoring/discussions/new) or file an [issue](https://github.com/willtheorangeguy/ollama-monitoring/issues/new/choose).

## Contributing

Contributions welcome. See the org-wide [Contributing Guide](https://github.com/willtheorangeguy/.github/blob/main/CONTRIBUTING.md) and [Code of Conduct](https://github.com/willtheorangeguy/.github/blob/main/CODE_OF_CONDUCT.md).

## License

MIT — see [LICENSE.md](LICENSE.md).
