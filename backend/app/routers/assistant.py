from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agents import coordinator
from app.services import data_access, risk_engine, intent

router = APIRouter(prefix="/api/assistant", tags=["assistant"])


class QuestionRequest(BaseModel):
    locality_id: str
    question: str


def _all_locality_profiles():
    profiles = []
    for loc in data_access.get_localities():
        latest = data_access.get_latest_metrics(loc["locality_id"])
        overall = risk_engine.overall_risk(latest)
        profiles.append({**loc, **overall})
    return profiles


def _answer_for_intent(detected_intent: str, question: str, locality_id: str, brief: dict) -> str:
    """Builds a tailored answer from the SAME grounded brief data, shaped by
    what was actually asked -- this is what makes the assistant feel
    responsive instead of returning one canned paragraph every time."""

    if detected_intent == "compare":
        other_id = intent.find_other_locality(question, exclude_id=locality_id)
        if not other_id:
            return (
                f"{brief['locality']} scores {brief['overall_risk_score']}/100 ({brief['risk_level']}). "
                "Mention another locality by name (e.g. 'compare with Kukatpally') for a direct comparison."
            )
        other_loc = data_access.get_locality(other_id)
        other_latest = data_access.get_latest_metrics(other_id)
        other_overall = risk_engine.overall_risk(other_latest)
        diff = round(brief["overall_risk_score"] - other_overall["overall_risk_score"], 1)
        direction = "higher than" if diff > 0 else ("lower than" if diff < 0 else "the same as")
        return (
            f"{brief['locality']} is at {brief['overall_risk_score']}/100 ({brief['risk_level']}), "
            f"{other_loc['name']} is at {other_overall['overall_risk_score']}/100 ({other_overall['risk_level']}). "
            f"{brief['locality']}'s risk is {abs(diff)} points {direction} {other_loc['name']}'s."
        )

    if detected_intent == "priority":
        profiles = _all_locality_profiles()
        worst = max(profiles, key=lambda p: p["overall_risk_score"])
        return (
            f"{worst['name']} currently requires the most immediate attention, "
            f"with an overall risk score of {worst['overall_risk_score']}/100 ({worst['risk_level']})."
        )

    if detected_intent == "confidence":
        return (
            f"Confidence in this assessment is {brief['confidence']}. This is based on how many "
            f"corroborating signals support the top contributing domain -- more independent findings "
            f"pointing the same direction means higher confidence. It is not a probability estimate."
        )

    if detected_intent == "evidence":
        lines = [
            f"{e['metric_name'].replace('_', ' ')}: {e['value']} (baseline {e['baseline']})"
            for e in brief["evidence"]
        ]
        return "Supporting data points: " + "; ".join(lines) + "."

    if detected_intent == "factors":
        return "Contributing factors: " + "; ".join(brief["contributing_factors"]) + "."

    if detected_intent == "recommend":
        actions = brief["recommended_actions"]
        numbered = "; ".join(f"({i+1}) {a}" for i, a in enumerate(actions))
        return f"Recommended actions, in priority order: {numbered}"

    if detected_intent == "impact":
        return brief["expected_impact"]

    # "why" and default "summary" both use the full grounded explanation
    return brief["summary"]


@router.post("/ask")
def ask_assistant(req: QuestionRequest):
    """
    Screen 4: AI Decision Assistant.
    Grounded Q&A -- always routes through the same coordinator/agent
    pipeline used for the Decision Brief, so answers are backed by
    the same evidence (no free-floating chatbot answers). Intent
    detection shapes WHICH part of that grounded data gets surfaced.
    """
    if not data_access.get_locality(req.locality_id):
        raise HTTPException(status_code=404, detail="Locality not found")

    brief = coordinator.build_decision_brief(req.locality_id, question=req.question)
    detected_intent = intent.classify(req.question)
    answer = _answer_for_intent(detected_intent, req.question, req.locality_id, brief)

    return {
        "question": req.question,
        "answer": answer,
        "detected_intent": detected_intent,
        "grounded_evidence": brief["evidence"],
        "risk_level": brief["risk_level"],
    }


@router.get("/priority-locality")
def priority_locality():
    """Answers: 'Which locality requires immediate attention?'"""
    localities = data_access.get_localities()
    scored = []
    for loc in localities:
        latest = data_access.get_latest_metrics(loc["locality_id"])
        overall = risk_engine.overall_risk(latest)
        scored.append({**loc, **overall})
    scored.sort(key=lambda p: p["overall_risk_score"], reverse=True)
    return scored[0]


@router.get("/decision-brief/{locality_id}")
def decision_brief(locality_id: str):
    """Screen 6: full Decision Brief for a locality."""
    if not data_access.get_locality(locality_id):
        raise HTTPException(status_code=404, detail="Locality not found")
    return coordinator.build_decision_brief(locality_id)


@router.get("/compare/{locality_id_a}/{locality_id_b}")
def compare_localities(locality_id_a: str, locality_id_b: str):
    """
    Direct comparison endpoint -- lets the frontend show a side-by-side
    comparison view without needing to parse natural language first.
    """
    if not data_access.get_locality(locality_id_a) or not data_access.get_locality(locality_id_b):
        raise HTTPException(status_code=404, detail="Locality not found")
    return coordinator.compare_localities(locality_id_a, locality_id_b)
