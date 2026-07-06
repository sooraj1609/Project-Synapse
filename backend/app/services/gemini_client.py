"""
Wrapper around Vertex AI Gemini.

For hackathon/local development where Google Cloud credentials may not be
configured, this falls back to an INTENT-AWARE templated summary -- it
actually reads the question and answers the specific thing asked (why /
what action / how confident / etc), rather than repeating one fixed
paragraph. When GOOGLE_CLOUD_PROJECT + USE_VERTEX_AI=true are set, it calls
real Gemini instead, which naturally handles arbitrary phrasing.

Flip real usage on by setting env var: USE_VERTEX_AI=true
Configure the model with: GEMINI_MODEL (default: gemini-2.0-flash-001)
"""
import os
import re
import json

USE_VERTEX_AI = os.getenv("USE_VERTEX_AI", "false").lower() == "true"
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "")
LOCATION = os.getenv("VERTEX_LOCATION", "us-central1")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-001")

_model = None


def _get_model():
    global _model
    if _model is None:
        import vertexai
        from vertexai.generative_models import GenerativeModel
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        _model = GenerativeModel(MODEL_NAME)
    return _model


def generate_decision_brief_text(context: dict) -> str:
    """
    context: {
      locality_name, risk_level, overall_risk_score,
      domain_scores, evidence (list of dicts), question (optional),
      recommended_actions (optional), confidence (optional)
    }
    Returns a natural-language explanation grounded in the given evidence.
    """
    if USE_VERTEX_AI and PROJECT_ID:
        try:
            model = _get_model()
            prompt = _build_prompt(context)
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return _fallback_answer(context) + f"\n\n[Note: Vertex AI call failed, showing rule-based answer. {e}]"
    return _fallback_answer(context)


def _build_prompt(context: dict) -> str:
    question_line = f'The user specifically asked: "{context["question"]}"' if context.get("question") else \
        "The user wants a general status summary."
    return f"""You are a Decision Intelligence assistant for city officials in Hyderabad.
Using ONLY the data below (do not invent numbers or facts not present here),
answer the user's question about {context['locality_name']} directly and concretely.

{question_line}

Overall risk: {context['risk_level']} ({context['overall_risk_score']}/100)
Domain risk scores: {json.dumps(context['domain_scores'])}
Evidence (top anomalous metrics vs baseline): {json.dumps(context['evidence'])}
Recommended actions on file: {json.dumps(context.get('recommended_actions', []))}
Confidence rating: {context.get('confidence', 'N/A')}

Answer the specific question asked -- don't just restate the overall summary if
they asked something narrower (e.g. if they asked about confidence, focus on
confidence; if they asked what to do, lead with the actions). 3-5 sentences,
plain language, no markdown headers."""


# --- Intent-aware fallback (used when Vertex AI is off or unreachable) ---

_INTENT_PATTERNS = [
    ("action", re.compile(r"\b(action|do|prioriti|recommend|should we|next step)\b", re.I)),
    ("confidence", re.compile(r"\b(confiden|sure|certain|reliable)\b", re.I)),
    ("impact", re.compile(r"\b(impact|effect|outcome|result|consequen)\b", re.I)),
    ("why", re.compile(r"\b(why|reason|cause|contribut)\b", re.I)),
    ("evidence", re.compile(r"\b(evidence|data|proof|show me|metric)\b", re.I)),
]


def _detect_intent(question: str) -> str:
    if not question:
        return "general"
    for intent, pattern in _INTENT_PATTERNS:
        if pattern.search(question):
            return intent
    return "general"


def _fallback_answer(context: dict) -> str:
    """Deterministic, template-based answer that actually varies by question intent."""
    loc = context["locality_name"]
    level = context["risk_level"]
    score = context["overall_risk_score"]
    evidence = context.get("evidence", [])
    actions = context.get("recommended_actions", [])
    confidence = context.get("confidence", "N/A")
    worst_domain = max(context["domain_scores"], key=context["domain_scores"].get)
    intent = _detect_intent(context.get("question", ""))

    def evidence_strs(n=3):
        out = []
        for e in evidence[:n]:
            direction = "above" if e["value"] > e["baseline"] else "below"
            out.append(
                f"{e['metric_name'].replace('_', ' ')} is {direction} baseline "
                f"({e['value']} vs baseline {e['baseline']})"
            )
        return out

    if intent == "action":
        if actions:
            action_text = " ".join(f"({i+1}) {a}" for i, a in enumerate(actions))
            return (
                f"For {loc}, the recommended actions in priority order are: {action_text} "
                f"These target the domains currently driving risk, led by {worst_domain.replace('_', ' ')}."
            )
        return f"No specific action is recommended for {loc} right now -- it is within normal ranges ({level}, {score}/100)."

    if intent == "confidence":
        return (
            f"Confidence in this assessment for {loc} is rated {confidence}. "
            f"This is based on how many independent signals support the top contributing domain "
            f"({worst_domain.replace('_', ' ')}) -- more corroborating metrics means higher confidence, "
            f"not a subjective guess."
        )

    if intent == "impact":
        return (
            f"Acting on the current recommendations for {loc} is expected to reduce pressure on "
            f"{worst_domain.replace('_', ' ')}, which is the largest driver of the {level} risk level "
            f"({score}/100). This is a demonstration-methodology estimate, not a measured outcome, "
            f"since no intervention has been logged yet for this locality."
        )

    if intent == "why":
        ev = evidence_strs()
        ev_text = "; ".join(ev) if ev else "no single metric stands out significantly"
        return (
            f"{loc} is at {level} risk ({score}/100) mainly because of the {worst_domain.replace('_', ' ')} "
            f"domain. Specifically: {ev_text}."
        )

    if intent == "evidence":
        ev = evidence_strs(4)
        if not ev:
            return f"No metrics in {loc} are currently far enough from baseline to flag as evidence."
        return f"The data behind this assessment for {loc}: " + "; ".join(ev) + "."

    # general / status
    ev = evidence_strs(2)
    ev_text = (" Key signals: " + "; ".join(ev) + ".") if ev else ""
    return (
        f"{loc} currently shows a {level} risk level with an overall score of {score}/100. "
        f"The {worst_domain.replace('_', ' ')} domain is the largest contributor.{ev_text}"
    )
