"""
Data access layer.

IMPORTANT: This is the ONLY file that should change when you migrate from
local JSON files to real BigQuery. Every router/agent calls functions in
this module -- none of them touch storage directly.

To migrate to BigQuery later:
  1. pip install google-cloud-bigquery
  2. Replace the body of each function below with a `client.query(...)` call
  3. Keep the same function signatures and return shapes
"""
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

from app.data.localities import LOCALITIES, DOMAINS, DOMAIN_METRICS

_DATA_DIR = Path(__file__).parent.parent / "data"
_metrics_cache = None


def _load_metrics():
    global _metrics_cache
    if _metrics_cache is None:
        path = _DATA_DIR / "metrics.json"
        if not path.exists():
            raise FileNotFoundError(
                "metrics.json not found. Run: python -m app.data.generate_data"
            )
        with open(path) as f:
            _metrics_cache = json.load(f)
    return _metrics_cache


def get_localities():
    return LOCALITIES


def get_locality(locality_id: str):
    return next((l for l in LOCALITIES if l["locality_id"] == locality_id), None)


def get_latest_metrics(locality_id: str):
    """Return the most recent value + baseline for every metric in a locality."""
    metrics = _load_metrics()
    latest = {}
    for row in metrics:
        if row["locality_id"] != locality_id:
            continue
        key = (row["domain"], row["metric_name"])
        if key not in latest or row["timestamp"] > latest[key]["timestamp"]:
            latest[key] = row
    return list(latest.values())


def get_metric_history(locality_id: str, metric_name: str, days: int = 30):
    metrics = _load_metrics()
    rows = [
        r for r in metrics
        if r["locality_id"] == locality_id and r["metric_name"] == metric_name
    ]
    rows.sort(key=lambda r: r["timestamp"])
    return rows[-days:]


def get_all_latest_by_locality():
    """Latest metrics for every locality, grouped -- used by the dashboard."""
    result = {}
    for loc in LOCALITIES:
        result[loc["locality_id"]] = get_latest_metrics(loc["locality_id"])
    return result
