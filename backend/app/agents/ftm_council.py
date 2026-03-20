"""
FTM Council Deliberation
Aggregates all agent results and produces final composite decision via GPT-4o.
Includes spatial conflict analysis in the deliberation context.
"""
import json
from typing import Any
from app.agents.base import call_gpt
from app.agents.orchestrator import AgentResult

SYSTEM_PROMPT = """You are the Federated Thinking Model (FTM) Council of Expert AI Models for the NREDCAP Land Allocation System.
You receive findings from 5 specialist agents (Land Records, Eco-Compliance, Environment Clearance, Grid Infrastructure, Cadastral) and GIS spatial analysis results, then deliberate to produce a final composite Trust-Scored Land Allocation Report.

The Trust Score weights are:
- Clean Title: 25 points max
- No Active Disputes: 20 points max
- Environmental Clearance: 20 points max
- Grid Connectivity: 15 points max
- Satellite/Cadastral Characteristics: 10 points max
- Historical Allocation Score (baseline): 10 points (always award 5-10)

IMPORTANT: Pay special attention to SPATIAL CONFLICTS from GIS analysis:
- existing_project_overlap: Proposal overlaps with already approved projects
- transmission_line_overlap: Proposal encroaches on transmission corridor buffer zones
- protected_area_overlap: Proposal overlaps with national parks, wildlife sanctuaries, or tiger reserves

Spatial conflicts should significantly impact the conflict_status and overall_trust_score:
- Critical spatial conflicts should result in conflict_status: "blocked" and reduced score
- High severity conflicts should result in conflict_status: "flagged"
- Multiple overlapping conflicts should escalate human_escalation_required to true

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
      "source_department": "<dept>",
      "overlap_area_ha": <float>
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


async def deliberate(
    proposal_id: str,
    proposal_data: dict,
    agent_results: list[AgentResult],
    spatial_conflicts: dict[str, Any] | None = None,
) -> dict:
    """
    FTM Council deliberation over all agent findings and spatial analysis.
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

    spatial_summary = _format_spatial_conflicts(spatial_conflicts)

    user_content = f"""
Proposal ID: {proposal_id}
Project: {proposal_data.get('project_type', 'solar')} | {proposal_data.get('capacity_mw', 0)}MW | District: {proposal_data.get('district', 'Unknown')}

Agent Findings:
{json.dumps(agents_summary, indent=2)}

GIS Spatial Analysis Results:
{spatial_summary}

As the FTM Council, deliberate on this proposal considering all agent findings and spatial conflicts, then produce the final Trust-Scored Land Allocation Report.
"""
    result = await call_gpt(SYSTEM_PROMPT, user_content, "ftm_council")
    result.setdefault("overall_trust_score", 50.0)
    result.setdefault("grade", "C")
    result.setdefault("conflict_status", "flagged")
    result.setdefault("factor_breakdown", {
        "clean_title": 15.0, "no_disputes": 12.0, "environmental_clearance": 10.0,
        "grid_connectivity": 8.0, "satellite_characteristics": 5.0, "historical_allocation": 7.0
    })
    return result


def _format_spatial_conflicts(spatial_conflicts: dict[str, Any] | None) -> str:
    if not spatial_conflicts:
        return "No spatial analysis performed."

    if not spatial_conflicts.get("has_spatial_conflicts"):
        return f"No spatial conflicts detected. Analysis completed successfully."

    parts = []
    parts.append(f"Overall Severity: {spatial_conflicts.get('overall_severity', 'unknown')}")
    parts.append(f"Total Conflict Count: {spatial_conflicts.get('conflict_count', 0)}")
    parts.append(f"Total Overlap Area: {spatial_conflicts.get('total_overlap_area_ha', 0):.2f} hectares")
    parts.append("")

    proposal_overlaps = spatial_conflicts.get("proposal_overlaps", [])
    if proposal_overlaps:
        parts.append("=== Existing Project Overlaps ===")
        for overlap in proposal_overlaps:
            parts.append(
                f"- {overlap.get('project_type', 'Unknown')} project ({overlap.get('capacity_mw', 0)}MW) "
                f"by {overlap.get('developer_name', 'Unknown')} in {overlap.get('district', 'Unknown')}"
            )
            parts.append(f"  Overlap: {overlap.get('overlap_area_ha', 0):.2f} ha | Severity: {overlap.get('severity', 'low')}")
        parts.append("")

    transmission_conflicts = spatial_conflicts.get("transmission_conflicts", [])
    if transmission_conflicts:
        parts.append("=== Transmission Line Conflicts ===")
        for conflict in transmission_conflicts:
            parts.append(
                f"- {conflict.get('line_name', 'Unknown')} ({conflict.get('voltage_kv', 0)}kV)"
            )
            parts.append(f"  Buffer: {conflict.get('buffer_m', 0)}m | Overlap: {conflict.get('overlap_area_ha', 0):.2f} ha | Severity: {conflict.get('severity', 'low')}")
        parts.append("")

    protected_area_conflicts = spatial_conflicts.get("protected_area_conflicts", [])
    if protected_area_conflicts:
        parts.append("=== Protected Area Conflicts ===")
        for conflict in protected_area_conflicts:
            parts.append(
                f"- {conflict.get('area_name', 'Unknown')} ({conflict.get('protection_type', 'Protected Area')})"
            )
            parts.append(f"  Overlap: {conflict.get('overlap_percentage', 0):.1f}% ({conflict.get('overlap_area_ha', 0):.2f} ha) | Severity: {conflict.get('severity', 'low')}")
        parts.append("")

    if spatial_conflicts.get("error"):
        parts.append(f"Note: Spatial analysis encountered an error: {spatial_conflicts.get('error')}")

    return "\n".join(parts)
