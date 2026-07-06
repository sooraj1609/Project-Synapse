"""
Lightweight, transparent intent classification for the AI Decision Assistant.

This is deliberately rule-based (keyword matching), not another LLM call --
it's fast, free, fully explainable, and good enough to make the assistant
feel responsive to what was actually asked instead of returning the same
canned summary regardless of the question.

If you later wire real Gemini in (USE_VERTEX_AI=true), this still runs
first to pick which grounded data to hand to the model as context --
so the LLM call itself stays cheap and focused instead of guessing.
"""
import re
from app.data.localities import LOCALITIES

LOCALITY_NAMES = {loc["name"].lower(): loc["locality_id"] for loc in LOCALITIES}

# Order matters: checked top to bottom, first match wins.
# "why" is checked early so phrasing like "why does X need immediate
# attention" (which also contains a 'priority'-ish phrase) still gets
# treated as a why-question, since that's the dominant intent.
INTENT_KEYWORDS = [
    ("compare", ["compare", "versus", " vs ", "vs.", "difference between"]),
    ("why", ["why"]),
    ("confidence", ["confidence", "confident", "how sure", "how certain", "reliable"]),
    ("evidence", ["evidence", "data point", "show me the data", "proof", "what data"]),
    ("factors", ["factor", "contribut", "driving", "causing", "root cause"]),
    ("recommend", ["recommend", "should we do", "should i do", "prioritize the action", "what to do", "next step"]),
    ("impact", ["impact", "effect", "consequence", "result of"]),
    ("priority", ["which locality", "most at risk", "highest risk", "worst locality", "requires immediate attention"]),
]


def classify(question: str) -> str:
    q = question.lower()
    for label, keywords in INTENT_KEYWORDS:
        if any(kw in q for kw in keywords):
            return label
    return "summary"


def find_other_locality(question: str, exclude_id: str = None):
    """Find a locality name mentioned in the question, other than the current one."""
    q = question.lower()
    for name, loc_id in LOCALITY_NAMES.items():
        if name in q and loc_id != exclude_id:
            return loc_id
    return None
