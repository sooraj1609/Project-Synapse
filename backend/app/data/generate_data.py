"""
Generates 30 days of synthetic daily metrics for 5 localities x 4 domains.
This stands in for the BigQuery `metrics` table during local development.
Output: metrics.json in the same folder, matching the unified schema:
  { timestamp, locality_id, domain, metric_name, value, baseline }

Run: python -m app.data.generate_data
"""
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

from app.data.localities import LOCALITIES, DOMAIN_METRICS

random.seed(42)

# Baselines per metric -- "normal" values for a typical locality on a typical day.
BASELINES = {
    "congestion_index": 45,
    "avg_travel_time_min": 28,
    "aqi": 90,
    "temperature_c": 33,
    "hospital_occupancy_pct": 60,
    "respiratory_cases_index": 20,
    "complaint_count": 12,
    "complaint_sentiment": 0.1,
}

NOISE = {
    "congestion_index": 6,
    "avg_travel_time_min": 4,
    "aqi": 12,
    "temperature_c": 2,
    "hospital_occupancy_pct": 5,
    "respiratory_cases_index": 5,
    "complaint_count": 3,
    "complaint_sentiment": 0.08,
}

DAYS = 30

# Deliberate anomaly: Gachibowli trends worse over the last 7 days across
# mobility, environment and citizen_services -- this is the locality the
# demo story (Section 8 of the build prompt) singles out as "High Risk".
ANOMALY_LOCALITY = "gachibowli"
ANOMALY_METRICS = {
    "congestion_index": 1.6,       # multiplier ramp
    "aqi": 1.5,
    "complaint_count": 2.2,
    "complaint_sentiment": -0.6,   # sentiment worsens (goes negative)
}


def generate():
    records = []
    today = datetime.utcnow().date()

    for loc in LOCALITIES:
        for domain, metrics in DOMAIN_METRICS.items():
            for m in metrics:
                name = m["metric_name"]
                base = BASELINES[name]
                noise = NOISE[name]

                for day_offset in range(DAYS, -1, -1):
                    date = today - timedelta(days=day_offset)
                    value = base + random.gauss(0, noise)

                    # apply ramping anomaly for the last 7 days in the target locality
                    if loc["locality_id"] == ANOMALY_LOCALITY and name in ANOMALY_METRICS and day_offset <= 7:
                        progress = (7 - day_offset) / 7  # 0 -> 1 over the week
                        mult = ANOMALY_METRICS[name]
                        if name == "complaint_sentiment":
                            value = base + progress * mult
                        else:
                            value = base * (1 + progress * (mult - 1))
                            value += random.gauss(0, noise * 0.5)

                    records.append({
                        "timestamp": date.isoformat(),
                        "locality_id": loc["locality_id"],
                        "domain": domain,
                        "metric_name": name,
                        "value": round(value, 2),
                        "baseline": base,
                    })

    out_path = Path(__file__).parent / "metrics.json"
    with open(out_path, "w") as f:
        json.dump(records, f, indent=2)

    print(f"Generated {len(records)} metric records -> {out_path}")


if __name__ == "__main__":
    generate()
