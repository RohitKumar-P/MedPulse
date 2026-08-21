import json
import requests


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "qwen3:8b"


def verify_prediction(
    disease,
    probability,
    symptoms,
    measurements,
    model_features
):
    prompt = f"""
You are the verification layer of MedPulse.

The machine-learning model has already produced the prediction.

IMPORTANT:
- Do NOT create a diagnosis from imagination.
- Do NOT replace the machine-learning prediction without evidence.
- Do NOT invent medical measurements.
- If the available information is insufficient, say so.
- Use simple language.
- This is a screening system, not a doctor.

ML prediction:
{disease}

ML probability:
{probability}

Symptoms reported by the user:
{json.dumps(symptoms, default=str)}

Measurements:
{json.dumps(measurements, default=str)}

Features used by the ML model:
{json.dumps(model_features, default=str)}

Return ONLY valid JSON:

{{
  "verification": "supported|partially_supported|insufficient|contradicted",
  "reason": "short explanation",
  "missing_information": [],
  "possible_common_issues": [],
  "red_flags": []
}}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=45
        )

        response.raise_for_status()

        data = response.json()
        result = data.get("response", "{}")

        return json.loads(result)

    except Exception as exc:
        return {
            "verification": "unavailable",
            "reason": "AI verification is currently unavailable.",
            "missing_information": [],
            "possible_common_issues": [],
            "red_flags": [],
            "error": str(exc)
        }
