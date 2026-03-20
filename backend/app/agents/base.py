"""
Shared base for all AI agents.
Each agent:
1. Queries its stub service
2. Formats context into a GPT-4o prompt
3. Parses structured JSON response
"""
import json
from openai import AsyncOpenAI
from app.config import get_settings

settings = get_settings()
_client: AsyncOpenAI | None = None


def get_openai_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


async def call_gpt(system_prompt: str, user_content: str, agent_name: str) -> dict:
    """
    Call GPT-4o and return parsed JSON. Falls back to a default dict on error.
    """
    client = get_openai_client()
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=0.2,
            max_tokens=1500,
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(content)
    except Exception as e:
        return {
            "error": str(e),
            "confidence": 30,
            "findings": {},
            "flags": [f"{agent_name}_gpt_error"],
            "summary": f"GPT call failed: {str(e)}",
        }
