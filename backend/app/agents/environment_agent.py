"""
Environment Agent.
Analyzes AQI and temperature signals for a locality.
"""
from app.services import risk_engine


def analyze(latest_metrics: list) -> dict:
    domain_rows = [m for m in latest_metrics if m["domain"] == "environment"]
    risk = risk_engine.domain_risk(latest_metrics, "environment")
    findings = []

    for row in domain_rows:
        mr = risk_engine.metric_risk(row["value"], row["baseline"], row["metric_name"])
        if mr >= 65:
            findings.append({
                "metric": row["metric_name"],
                "value": row["value"],
                "baseline": row["baseline"],
                "severity": "high" if mr >= 80 else "moderate",
                "note": f"{row['metric_name'].replace('_', ' ')} is elevated versus baseline",
            })

    return {
        "domain": "environment",
        "risk_score": risk,
        "findings": findings,
    }
