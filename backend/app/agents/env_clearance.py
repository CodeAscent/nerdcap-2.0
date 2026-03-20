"""Environment Clearance Agent — queries SEIAA-AP stub, reasons via GPT-4o"""
import json
from app.agents.base import call_gpt
from app.agents.orchestrator import AgentResult
from app.stubs import seiaa_stub

SYSTEM_PROMPT = """You are the Environment Clearance Agent in the NREDCAP AI Land Allocation System.
You analyze EIA zone data and CRZ boundaries from SEIAA-AP to assess environmental compliance.

Respond ONLY with a JSON object:
{
  "confidence": <0-100 float>,
  "clearance_pathway": "straightforward" | "requires_eia" | "blocked",
  "env_score": <0-20 float, contribution to trust score>,
  "estimated_clearance_months": <integer>,
  "findings": {<key EIA/CRZ facts>},
  "flags": [<e.g. "category_a_eia_required", "crz_overlap", "eco_sensitive_zone">],
  "recommendation": "<brief recommendation>",
  "summary": "<2-3 sentence summary>"
}"""


async def run(proposal_id: str, proposal_data: dict) -> AgentResult:
    stub_data = seiaa_stub.query(proposal_id, proposal_data.get("boundary_geojson"))

    user_content = f"""Proposal: {proposal_id} | {proposal_data.get('project_type')} {proposal_data.get('capacity_mw')}MW | {proposal_data.get('district')}
SEIAA-AP Data:
{json.dumps(stub_data, indent=2)}
Assess environmental clearance pathway and compliance requirements."""

    result = await call_gpt(SYSTEM_PROMPT, user_content, "env_clearance")
    return AgentResult(
        agent_name="Environment Clearance Agent",
        confidence=result.get("confidence", 50),
        findings=result.get("findings", stub_data),
        flags=result.get("flags", []),
        raw_response=json.dumps(result),
        success="error" not in result,
        error=result.get("error"),
    )
