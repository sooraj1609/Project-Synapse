from fastapi import APIRouter, HTTPException
from app.services import data_access, risk_engine

router = APIRouter(prefix="/api/localities", tags=["localities"])


@router.get("")
def list_localities():
    """List all localities with their current overall risk score (for map/list views)."""
    out = []
    for loc in data_access.get_localities():
        latest = data_access.get_latest_metrics(loc["locality_id"])
        overall = risk_engine.overall_risk(latest)
        out.append({**loc, **overall})
    return out


@router.get("/{locality_id}")
def get_locality_profile(locality_id: str):
    """Full risk profile for one locality: scores + latest metrics per domain."""
    loc = data_access.get_locality(locality_id)
    if not loc:
        raise HTTPException(status_code=404, detail="Locality not found")

    latest = data_access.get_latest_metrics(locality_id)
    overall = risk_engine.overall_risk(latest)

    return {
        **loc,
        **overall,
        "metrics": latest,
    }


@router.get("/{locality_id}/history/{metric_name}")
def get_metric_history(locality_id: str, metric_name: str, days: int = 30):
    if not data_access.get_locality(locality_id):
        raise HTTPException(status_code=404, detail="Locality not found")
    return data_access.get_metric_history(locality_id, metric_name, days)
