#!/usr/bin/python3
"""Read-only Ollama inventory for Node Exporter's existing textfile collector.

Each failed collection replaces old data with health=0; no stale counts survive.
No inference requests, database access, prompts, or user identities are collected.
"""
import json
import math
import os
import time
import urllib.request
from pathlib import Path

OUTPUT = Path(os.getenv('OLLAMA_INVENTORY_OUTPUT', '/var/lib/node_exporter/textfile_collector/ollama.prom'))


def fetch(path):
    with urllib.request.urlopen(os.getenv('OLLAMA_UPSTREAM_URL', 'http://127.0.0.1:11434').rstrip('/') + path, timeout=float(os.getenv('OLLAMA_TIMEOUT_SECONDS', '5'))) as response:
        return json.load(response)


def nonnegative(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError('invalid numeric field')
    if not math.isfinite(value) or value < 0:
        raise ValueError('invalid numeric field')
    return value


def label(value):
    return str(value).replace('\\', '\\\\').replace('\n', '\\n').replace('"', '\\"')


def collect():
    tags = fetch('/api/tags')['models']
    running = fetch('/api/ps')['models']
    if not isinstance(tags, list) or not isinstance(running, list):
        raise ValueError('invalid models response')
    lines = [
        '# TYPE ollama_inventory_models gauge',
        f'ollama_inventory_models {len(tags)}',
        '# TYPE ollama_inventory_loaded_models gauge',
        f'ollama_inventory_loaded_models {len(running)}',
        '# TYPE ollama_inventory_model_size_bytes gauge',
    ]
    for model in tags:
        details = model['details']
        labels = ','.join(f'{key}="{label(value)}"' for key, value in (
            ('model', model['name']), ('family', details['family']),
            ('quant', details['quantization_level']),
            ('parameters', details['parameter_size'])))
        lines.append(f'ollama_inventory_model_size_bytes{{{labels}}} {nonnegative(model["size"])}')
    # API-reported allocation, not independent hardware measurement.
    lines += ['# TYPE ollama_inventory_loaded_vram_bytes gauge',
              f'ollama_inventory_loaded_vram_bytes {sum(nonnegative(m["size_vram"]) for m in running)}']
    return lines


def main():
    try:
        lines = collect()
        healthy = 1
    except Exception as error:
        print(f'Ollama inventory collection failed: {type(error).__name__}', flush=True)
        lines, healthy = [], 0
    lines += ['# TYPE ollama_inventory_up gauge', f'ollama_inventory_up {healthy}',
              '# TYPE ollama_inventory_collection_timestamp_seconds gauge',
              f'ollama_inventory_collection_timestamp_seconds {time.time()}']
    temporary = OUTPUT.with_suffix('.prom.tmp')
    temporary.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    os.replace(temporary, OUTPUT)


if __name__ == '__main__':
    main()
