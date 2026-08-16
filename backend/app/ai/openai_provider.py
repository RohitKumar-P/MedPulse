import json

from openai import AsyncOpenAI

from app.ai.config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    AI_ONLINE_TIMEOUT
)


SYSTEM_PROMPT = """
You are a structured medical-information
extraction component.

You are NOT a diagnostician.

Extract only information explicitly present
in the supplied text.

Never invent:
- symptoms
- diagnoses
- medications
- laboratory values
- severity
- dates

Preserve:
- negation
- uncertainty
- temporal information

Return JSON matching the requested schema.
"""


class OpenAIProvider:

    name = "openai"

    def __init__(self):

        if not OPENAI_API_KEY:

            raise RuntimeError(
                "OPENAI_API_KEY is not configured"
            )

        self.client = AsyncOpenAI(
            api_key=OPENAI_API_KEY,
            timeout=AI_ONLINE_TIMEOUT
        )

    async def extract(
        self,
        text: str
    ):

        response = await self.client.responses.create(

            model=OPENAI_MODEL,

            instructions=SYSTEM_PROMPT,

            input=text,

            temperature=0,

            max_output_tokens=1200
        )

        return json.loads(
            response.output_text
        )
