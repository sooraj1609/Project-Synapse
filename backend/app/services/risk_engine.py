"""
Risk scoring engine.

Method (documented, not a black box -- important for the demo Q&A):

1. For each metric, compute an anomaly ratio vs its baseline:
       ratio = (value - baseline) / baseline        [inverted if higher_is_worse=False]
2. Convert the ratio into a 0-100 "metric risk" via clipping:
       metric_risk = clip(50 + ratio * 100, 0, 100)
   (0 ratio -> 50 = neutral; positive ratio -> pushes toward 100 = worse)
3. Domain risk = average of its metrics' risk scores.
4. Overall locality risk = weighted sum of domain risks using DOMAIN_WEIGHTS
   (currently equal 25% weights, see app/data/localities.py).
5. Risk level bucket:
     0-30   Stable
     30-50  Improving / Watch
     50-65  Warning
     65-85  At Risk
     85-100 Critical
"""
from app.data.localities import DOMAIN_METRICS, DOMAIN_WEIGHTS

_HIGHER_IS_WORSE = {
    m["metric_name"]: m["higher_is_worse"]
    for metrics in DOMAIN_METRICS.values()
    for m in metrics
}


def _clip(x, lo=0, hi=100):
    return max(lo, min(hi, x))


def metric_risk(value: float, baseline: float, metric_name: str) -> float:
    if baseline == 0:
        return 50.0
    ratio = (value - baseline) / abs(baseline)
    if not _HIGHER_IS_WORSE.get(metric_name, True):
        ratio = -ratio
    return round(_clip(50 + ratio * 100), 1)


def domain_risk(latest_metrics: list, domain: str) -> float:
    rows = [m for m in latest_metrics if m["domain"] == domain]
    if not rows:
        return 0.0
    scores = [metric_risk(r["value"], r["baseline"], r["metric_name"]) for r in rows]
    return round(sum(scores) / len(scores), 1)


def overall_risk(latest_metrics: list) -> dict:
    domain_scores = {d: domain_risk(latest_metrics, d) for d in DOMAIN_WEIGHTS}
    overall = sum(domain_scores[d] * w for d, w in DOMAIN_WEIGHTS.items())
    overall = round(overall, 1)
    return {
        "overall_risk_score": overall,
        "risk_level": risk_level(overall),
        "domain_scores": domain_scores,
        "weights_used": DOMAIN_WEIGHTS,
    }


def risk_level(score: float) -> str:
    if score < 30:
        return "Stable"
    if score < 50:
        return "Improving"
    if score < 65:
        return "Warning"
    if score < 85:
        return "At Risk"
    return "Critical"


def top_contributing_metrics(latest_metrics: list, n: int = 3) -> list:
    """Highest-risk individual metrics, for evidence in the Decision Brief."""
    scored = [
        {
            **r,
            "metric_risk": metric_risk(r["value"], r["baseline"], r["metric_name"]),
        }
        for r in latest_metrics
    ]
    scored.sort(key=lambda r: r["metric_risk"], reverse=True)
    return scored[:n]
