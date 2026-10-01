# Architecture

This project connects its data source to its Grafana dashboard through the components shown below.

## Overview

This diagram shows the data path for this project.

```mermaid
graph LR
  A[Ollama API] -->|streams through| B[Inference proxy]
  A -->|polled by| C[Inventory collector]
  C -->|writes metrics for| D[Node Exporter]
  B -->|exposes metrics to| E[Prometheus]
  D -->|scraped by| E
  F[Model state exporter] -->|scraped by| E
  E -->|queried by| G[Grafana dashboard]
```

## Components

### Data source

Ollama API -> inference proxy -> Prometheus; inventory timer writes textfile metrics for Node Exporter; upstream model exporter -> Prometheus -> Grafana.

### Dashboard

`dashboards/ollama-inference-25086.json` contains the Grafana dashboard definition.

## Data flow

Ollama API -> inference proxy -> Prometheus; inventory timer writes textfile metrics for Node Exporter; upstream model exporter -> Prometheus -> Grafana. Grafana evaluates dashboard queries against the selected data source and label values.

## Directory layout

```text
.
├── dashboards/  Grafana dashboard JSON files
├── src/  Python services and collectors
├── examples/  Scrape and deployment examples
├── docs/        Documentation source
└── README.md    Project overview and quick links
```
