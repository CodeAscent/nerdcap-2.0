"""Cadastral Verification Agent — queries Cadastral stub, reasons via GPT-4o"""
import json
from app.agents.base import call_gpt
from app.agents.orchestrator import AgentResult
from app.stubs import cadastral_stub

SYSTEM_PROMPT = """You are the Cadastral Verification Agent in the NREDCAP AI Land Allocation System.
You analyze cadastral survey records to verify submitted boundary accuracy.

Respond ONLY with a JSON object:
{
  "confidence": <0-100 float>,
  "boundary_validity": "valid" | "minor_discrepancy" | "major_discrepancy" | "disputed",
  "satellite_score": <0-10 float, contribution to trust score>,
  "area_discrepancy_pct": <float>,
  "findings": {<key survey facts>},
  "flags": [<e.g. "boundary_dispute", "major_area_discrepancy", "survey_outdated">],
  "recommendation": "<brief recommendation>",
  "summary": "<2-3 sentence summary>"
}"""


async def run(proposal_id: str, proposal_data: dict) -> AgentResult:
    stub_data = cadastral_stub.query(proposal_id, proposal_data.get("boundary_geojson"))

    user_content = f"""Proposal: {proposal_id} | {proposal_data.get('project_type')} | District: {proposal_data.get('district')}
Cadastral Survey Data:
{json.dumps(stub_data, indent=2)}
Verify boundary accuracy and assess any land record discrepancies."""

    result = await call_gpt(SYSTEM_PROMPT, user_content, "cadastral")
    return AgentResult(
        agent_name="Cadastral Verification Agent",
        confidence=result.get("confidence", 50),
        findings=result.get("findings", stub_data),
        flags=result.get("flags", []),
        raw_response=json.dumps(result),
        success="error" not in result,
        error=result.get("error"),
    )
