from fastapi import APIRouter
from app.services import data_access, risk_engine, gemini_client

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary():
    """
    Powers the Community Overview Dashboard (Screen 2):
    KPI cards + locality risk overview + AI daily summary.
    """
    localities = data_access.get_localities()
    profiles = []
    for loc in localities:
        latest = data_access.get_latest_metrics(loc["locality_id"])
        overall = risk_engine.overall_risk(latest)
        profiles.append({**loc, **overall})

    high_risk = [p for p in profiles if p["overall_risk_score"] >= 65]
    high_risk.sort(key=lambda p: p["overall_risk_score"], reverse=True)

    avg_health_score = round(
        100 - (sum(p["overall_risk_score"] for p in profiles) / len(profiles)), 1
    )

    # simple pulse: worst individual locality pulse drives community pulse
    worst = max(profiles, key=lambda p: p["overall_risk_score"])
    pulse = worst["risk_level"]

    kpis = {
        "community_health_score": avg_health_score,
        "active_alerts": len(high_risk),
        "high_risk_localities": len(high_risk),
        "community_pulse": pulse,
    }

    # AI daily summary, grounded in the actual high-risk localities (no invented facts)
    if high_risk:
        names = ", ".join(p["name"] for p in high_risk)
        ai_summary = (
            f"{len(high_risk)} localit{'y requires' if len(high_risk)==1 else 'ies require'} "
            f"immediate attention today: {names}. "
            f"{worst['name']} shows the highest risk at {worst['overall_risk_score']}/100 "
            f"({worst['risk_level']})."
        )
    else:
        ai_summary = "All localities are currently within stable risk ranges. No immediate action required."

    return {
        "kpis": kpis,
        "localities": profiles,
        "high_risk_localities": high_risk,
        "ai_daily_summary": ai_summary,
    }
