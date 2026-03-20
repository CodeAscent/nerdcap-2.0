"""
FTM Council Deliberation
Aggregates all agent results and produces final composite decision via GPT-4o.
"""
import json
from app.agents.base import call_gpt
from app.agents.orchestrator import AgentResult

SYSTEM_PROMPT = """You are the Federated Thinking Model (FTM) Council of Expert AI Models for the NREDCAP Land Allocation System.
You receive findings from 5 specialist agents (Land Records, Eco-Compliance, Environment Clearance, Grid Infrastructure, Cadastral) and deliberate to produce a final composite Trust-Scored Land Allocation Report.

The Trust Score weights are:
- Clean Title: 25 points max
- No Active Disputes: 20 points max
- Environmental Clearance: 20 points max
- Grid Connectivity: 15 points max
- Satellite/Cadastral Characteristics: 10 points max
- Historical Allocation Score (baseline): 10 points (always award 5-10)

Grade: A (85-100), B (70-84), C (50-69), D (0-49)
Conflict Status: "clear" | "flagged" | "blocked"

Respond ONLY with a JSON object:
{
  "overall_trust_score": <0-100 float>,
  "grade": "A" | "B" | "C" | "D",
  "conflict_status": "clear" | "flagged" | "blocked",
  "conflict_matrix": [
    {
      "conflict_type": "<type>",
      "severity": "low" | "medium" | "high" | "critical",
      "description": "<detail>",
      "source_department": "<dept>"
    }
  ],
  "factor_breakdown": {
    "clean_title": <0-25>,
    "no_disputes": <0-20>,
    "environmental_clearance": <0-20>,
    "grid_connectivity": <0-15>,
    "satellite_characteristics": <0-10>,
    "historical_allocation": <0-10>
  },
  "recommended_actions": [<string actions for the officer>],
  "key_risk_flags": [<critical flags requiring human review>],
  "human_escalation_required": <bool>,
  "escalation_reason": "<reason if escalation required, else null>",
  "council_summary": "<4-5 sentence professional summary of the land allocation assessment for government officers>",
  "compliance_status": "compliant" | "conditional" | "non_compliant",
  "estimated_approval_timeline_months": <integer>
}"""


async def deliberate(proposal_id: str, proposal_data: dict, agent_results: list[AgentResult]) -> dict:
    """
    FTM Council deliberation over all agent findings.
    """
    agents_summary = []
    for agent in agent_results:
        agents_summary.append({
            "agent": agent.agent_name,
            "confidence": agent.confidence,
            "findings": agent.findings,
            "flags": agent.flags,
            "success": agent.success,
        })

    user_content = f"""
Proposal ID: {proposal_id}
Project: {proposal_data.get('project_type', 'solar')} | {proposal_data.get('capacity_mw', 0)}MW | District: {proposal_data.get('district', 'Unknown')}

Agent Findings:
{json.dumps(agents_summary, indent=2)}

As the FTM Council, deliberate on this proposal and produce the final Trust-Scored Land Allocation Report.
"""
    result = await call_gpt(SYSTEM_PROMPT, user_content, "ftm_council")
    # Ensure defaults
    result.setdefault("overall_trust_score", 50.0)
    result.setdefault("grade", "C")
    result.setdefault("conflict_status", "flagged")
    result.setdefault("factor_breakdown", {
        "clean_title": 15.0, "no_disputes": 12.0, "environmental_clearance": 10.0,
        "grid_connectivity": 8.0, "satellite_characteristics": 5.0, "historical_allocation": 7.0
    })
    return result
