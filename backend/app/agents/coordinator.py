"""
Decision Coordinator.

This is the "synthesis" step of the multi-agent workflow:
  domain agents produce findings -> coordinator combines them into one
  explainable Decision Brief matching the schema from the build prompt:

{
  "summary": "",
  "risk_level": "",
  "evidence": [],
  "contributing_factors": [],
  "recommended_actions": [],
  "expected_impact": "",
  "confidence": "",
  "limitations": ""
}
"""
from app.agents import mobility_agent, environment_agent, health_agent, citizen_agent
from app.services import risk_engine, gemini_client, data_access

AGENTS = {
    "mobility": mobility_agent,
    "environment": environment_agent,
    "health": health_agent,
    "citizen_services": citizen_agent,
}

# Simple, documented action rules keyed by which domain(s) are driving the risk.
# This keeps recommendations grounded instead of letting the LLM invent actions.
ACTION_RULES = {
    "mobility": "Increase public transport frequency during peak hours and review signal timing on congested corridors.",
    "environment": "Initiate targeted air-quality monitoring and issue a public advisory for sensitive groups.",
    "health": "Alert nearby healthcare facilities to prepare additional capacity and monitor admission trends.",
    "citizen_services": "Prioritize response to the recent complaint category and assign a dedicated resolution team.",
}


def compare_localities(locality_id_a: str, locality_id_b: str) -> dict:
    """
    Answers: 'Compare two localities.'
    Returns both localities' scores side by side plus a short, grounded
    comparison sentence -- no LLM required, this is pure data comparison.
    """
    loc_a = data_access.get_locality(locality_id_a)
    loc_b = data_access.get_locality(locality_id_b)
    if not loc_a or not loc_b:
        return {"error": "One or both localities not found"}

    metrics_a = data_access.get_latest_metrics(locality_id_a)
    metrics_b = data_access.get_latest_metrics(locality_id_b)
    overall_a = risk_engine.overall_risk(metrics_a)
    overall_b = risk_engine.overall_risk(metrics_b)

    higher = loc_a["name"] if overall_a["overall_risk_score"] > overall_b["overall_risk_score"] else loc_b["name"]
    diff = round(abs(overall_a["overall_risk_score"] - overall_b["overall_risk_score"]), 1)

    domain_comparison = {}
    for domain in overall_a["domain_scores"]:
        domain_comparison[domain] = {
            loc_a["name"]: overall_a["domain_scores"][domain],
            loc_b["name"]: overall_b["domain_scores"][domain],
        }

    summary = (
        f"{higher} currently has the higher overall risk, by {diff} points "
        f"({loc_a['name']}: {overall_a['overall_risk_score']}/100 [{overall_a['risk_level']}] vs "
        f"{loc_b['name']}: {overall_b['overall_risk_score']}/100 [{overall_b['risk_level']}])."
    )

    return {
        "localities": [
            {"name": loc_a["name"], "locality_id": locality_id_a, **overall_a},
            {"name": loc_b["name"], "locality_id": locality_id_b, **overall_b},
        ],
        "domain_comparison": domain_comparison,
        "summary": summary,
    }


def build_decision_brief(locality_id: str, question: str = None) -> dict:
    locality = data_access.get_locality(locality_id)
    if not locality:
        return {"error": f"Unknown locality '{locality_id}'"}

    latest_metrics = data_access.get_latest_metrics(locality_id)
    overall = risk_engine.overall_risk(latest_metrics)

    # 1. Each domain agent analyzes its slice of the data
    agent_results = {name: agent.analyze(latest_metrics) for name, agent in AGENTS.items()}

    # 2. Coordinator gathers evidence: top anomalous metrics across all domains
    evidence = risk_engine.top_contributing_metrics(latest_metrics, n=4)

    # 3. Contributing factors = domains with risk_score >= 65, sorted worst first
    contributing_domains = sorted(
        [d for d, r in agent_results.items() if r["risk_score"] >= 65],
        key=lambda d: agent_results[d]["risk_score"],
        reverse=True,
    )
    if not contributing_domains:
        # nothing above the "Warning" threshold -- use the single worst domain instead
        contributing_domains = [max(agent_results, key=lambda d: agent_results[d]["risk_score"])]

    contributing_factors = [
        f"{d.replace('_', ' ').title()} risk score is {agent_results[d]['risk_score']}/100"
        for d in contributing_domains
    ]

    # 4. Recommended actions from the rule table, one per contributing domain
    recommended_actions = [ACTION_RULES[d] for d in contributing_domains]

    # 5. Confidence: defined method, not arbitrary --
    #    based on how many findings support the top domain (more evidence = higher confidence)
    top_domain = contributing_domains[0]
    n_findings = len(agent_results[top_domain]["findings"])
    confidence = "High" if n_findings >= 2 else ("Medium" if n_findings == 1 else "Low")

    # 6. Natural-language summary, grounded in the evidence above.
    # recommended_actions and confidence are computed above but the summary
    # needs them too so it can answer action/confidence-specific questions.
    summary_text = gemini_client.generate_decision_brief_text({
        "locality_name": locality["name"],
        "risk_level": overall["risk_level"],
        "overall_risk_score": overall["overall_risk_score"],
        "domain_scores": overall["domain_scores"],
        "evidence": evidence,
        "question": question,
        "recommended_actions": recommended_actions,
        "confidence": confidence,
    })

    return {
        "locality": locality["name"],
        "summary": summary_text,
        "risk_level": overall["risk_level"],
        "overall_risk_score": overall["overall_risk_score"],
        "domain_scores": overall["domain_scores"],
        "evidence": evidence,
        "contributing_factors": contributing_factors,
        "recommended_actions": recommended_actions,
        "expected_impact": "Reduced pressure on the highlighted domain(s) and improved monitoring response, "
                            "based on the rule-based action mapping (demonstration methodology).",
        "confidence": confidence,
        "limitations": "Generated from synthetic demonstration data and a transparent rule-based scoring "
                        "model. Not based on live government data sources.",
        "agent_findings": agent_results,
    }
