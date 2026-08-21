import json
import httpx

from app.ai.config import (
    OLLAMA_URL,
    OLLAMA_MODEL,
    AI_LOCAL_TIMEOUT
)


SYSTEM_PROMPT = """
You are the structured information extraction
component of Aegis Health AI.

You are NOT a diagnostician.

Extract ONLY information explicitly reported
by the user.

Return JSON ONLY.

Use exactly this structure:

{
  "symptoms": [
    {
      "name": "controlled symptom name",
      "confidence": 0.0,
      "severity": "mild|moderate|severe|unknown",
      "onset": "text or null",
      "duration": "text or null",
      "current": true,
      "negated": false
    }
  ],
  "medications": [],
  "diagnoses": [],
  "allergies": [],
  "laboratory_results": [],
  "missing_information": [],
  "uncertainty": []
}

Rules:

- confidence MUST be a number from 0 to 1.
- Never use words such as "high" for confidence.
- Never invent symptoms.
- Never diagnose.
- Never recommend treatment.
- Never recommend medication.
- Preserve negation.
- Preserve uncertainty.
- Preserve time information.
- If something is not stated, use null or an empty list.
- Do not infer laboratory values.
- Do not infer a disease from symptoms.
"""


class OllamaProvider:

    name = "ollama"

    async def extract(
        self,
        text: str
    ):

        payload = {

            "model":
                OLLAMA_MODEL,

            "stream":
                False,

            "format":
                "json",

            "options": {

                "temperature":
                    0,

                "top_p":
                    0.1,

                "num_predict":
                    1200
            },

            "system":
                SYSTEM_PROMPT,

            "prompt":
                text
        }

        async with httpx.AsyncClient(
            timeout=AI_LOCAL_TIMEOUT
        ) as client:

            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json=payload
            )

            response.raise_for_status()

            data = response.json()

        raw = data.get(
            "response",
            "{}"
        )

        return json.loads(
            raw
        )

    async def generate(self, prompt: str):
        import httpx

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                "http://127.0.0.1:11434/api/generate",
                json={
                    "model": "qwen3:8b",
                    "prompt": prompt,
                    "stream": False
                }
            )

            response.raise_for_status()

            data = response.json()

            return data.get("response", "").strip()
