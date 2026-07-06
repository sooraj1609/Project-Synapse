"""
Health Agent.
Analyzes hospital occupancy and respiratory case indicators for a locality.
"""
from app.services import risk_engine


def analyze(latest_metrics: list) -> dict:
    domain_rows = [m for m in latest_metrics if m["domain"] == "health"]
    risk = risk_engine.domain_risk(latest_metrics, "health")
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
        "domain": "health",
        "risk_score": risk,
        "findings": findings,
    }
