"""Eco-Compliance Agent — queries Forest stub, reasons via GPT-4o"""
import json
from app.agents.base import call_gpt
from app.agents.orchestrator import AgentResult
from app.stubs import forest_stub

SYSTEM_PROMPT = """You are the Eco-Compliance Agent in the NREDCAP AI Land Allocation System.
You analyze forest coverage and wildlife data from the AP Forest Department to assess ecological compliance.

Respond ONLY with a JSON object:
{
  "confidence": <0-100 float>,
  "eco_risk": "low" | "medium" | "high" | "critical",
  "env_clearance_score": <0-20 float, contribution to trust score>,
  "forest_clearance_required": <bool>,
  "findings": {<key ecological facts>},
  "flags": [<risk flags like "wildlife_corridor_overlap", "protected_area_buffer", "dense_vegetation">],
  "recommendation": "<brief recommendation>",
  "summary": "<2-3 sentence summary>"
}"""


async def run(proposal_id: str, proposal_data: dict) -> AgentResult:
    stub_data = forest_stub.query(proposal_id, proposal_data.get("boundary_geojson"))

    user_content = f"""Proposal: {proposal_id} | {proposal_data.get('project_type')} {proposal_data.get('capacity_mw')}MW | {proposal_data.get('district')}
Forest Dept Data:
{json.dumps(stub_data, indent=2)}
Assess ecological compliance and forest clearance necessity."""

    result = await call_gpt(SYSTEM_PROMPT, user_content, "eco_compliance")
    return AgentResult(
        agent_name="Eco-Compliance Agent",
        confidence=result.get("confidence", 50),
        findings=result.get("findings", stub_data),
        flags=result.get("flags", []),
        raw_response=json.dumps(result),
        success="error" not in result,
        error=result.get("error"),
    )
