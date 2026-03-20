"""Grid Infrastructure Agent — queries APTRANSCO stub, reasons via GPT-4o"""
import json
from app.agents.base import call_gpt
from app.agents.orchestrator import AgentResult
from app.stubs import aptransco_stub

SYSTEM_PROMPT = """You are the Grid Infrastructure Agent in the NREDCAP AI Land Allocation System.
You analyze grid connectivity data from APTRANSCO to assess power evacuation feasibility.

Respond ONLY with a JSON object:
{
  "confidence": <0-100 float>,
  "grid_feasibility": "excellent" | "good" | "moderate" | "poor",
  "grid_score": <0-15 float, contribution to trust score>,
  "transmission_conflict": <bool>,
  "findings": {<key grid infrastructure facts>},
  "flags": [<e.g. "transmission_line_conflict", "low_evacuation_capacity", "distant_substation">],
  "recommendation": "<brief recommendation>",
  "summary": "<2-3 sentence summary>"
}"""


async def run(proposal_id: str, proposal_data: dict) -> AgentResult:
    stub_data = aptransco_stub.query(proposal_id, proposal_data.get("boundary_geojson"))

    user_content = f"""Proposal: {proposal_id} | {proposal_data.get('project_type')} {proposal_data.get('capacity_mw')}MW | {proposal_data.get('district')}
APTRANSCO Data:
{json.dumps(stub_data, indent=2)}
Project capacity is {proposal_data.get('capacity_mw')} MW. Assess if grid evacuation capacity is sufficient."""

    result = await call_gpt(SYSTEM_PROMPT, user_content, "grid_infrastructure")
    return AgentResult(
        agent_name="Grid Infrastructure Agent",
        confidence=result.get("confidence", 50),
        findings=result.get("findings", stub_data),
        flags=result.get("flags", []),
        raw_response=json.dumps(result),
        success="error" not in result,
        error=result.get("error"),
    )
