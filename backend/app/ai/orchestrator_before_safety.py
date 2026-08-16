from app.ai.ollama_provider import OllamaProvider
from app.ai.verifier import validate_extraction
from app.ai.critical_symptoms import detect_critical_symptoms
from app.ai.config import AI_ALLOW_ONLINE, OPENAI_API_KEY


class AegisAIOrchestrator:

    def __init__(self):
        self.local = OllamaProvider()

    async def extract(self, text: str):

        safety_matches = detect_critical_symptoms(text)

        local_result = None
        local_error = None

        try:
            local_raw = await self.local.extract(text)

            local_result = validate_extraction(
                local_raw,
                text
            )

        except Exception as exc:
            local_error = str(exc)

        if local_result:
            result = local_result.model_dump()

            symptoms = result.setdefault("symptoms", [])

            existing = {
                item.get("name")
                for item in symptoms
            }

            for match in safety_matches:
                symptom = match["symptom"]

                if symptom not in existing:
                    symptoms.append({
                        "name": symptom,
                        "confidence": 1.0,
                        "severity": "severe",
                        "onset": None,
                        "duration": None,
                        "current": True,
                        "negated": False
                    })

                    existing.add(symptom)

            return {
                "status": "success",
                "provider": "local",
                "model": "ollama",
                "validated": True,
                "result": result,
                "fallback_used": False,
                "local_error": None,
                "safety_matches": safety_matches
            }

        if AI_ALLOW_ONLINE and OPENAI_API_KEY:

            try:
                from app.ai.openai_provider import OpenAIProvider

                online = OpenAIProvider()

                online_raw = await online.extract(text)

                online_result = validate_extraction(
                    online_raw,
                    text
                )

                result = online_result.model_dump()

                symptoms = result.setdefault("symptoms", [])

                existing = {
                    item.get("name")
                    for item in symptoms
                }

                for match in safety_matches:
                    symptom = match["symptom"]

                    if symptom not in existing:
                        symptoms.append({
                            "name": symptom,
                            "confidence": 1.0,
                            "severity": "severe",
                            "onset": None,
                            "duration": None,
                            "current": True,
                            "negated": False
                        })

                        existing.add(symptom)

                return {
                    "status": "success",
                    "provider": "online",
                    "model": "openai",
                    "validated": True,
                    "result": result,
                    "fallback_used": True,
                    "local_error": local_error,
                    "safety_matches": safety_matches
                }

            except Exception as exc:

                return {
                    "status": "failed",
                    "provider": None,
                    "validated": False,
                    "result": None,
                    "error": str(exc),
                    "local_error": local_error,
                    "safety_matches": safety_matches
                }

        return {
            "status": "failed",
            "provider": None,
            "validated": False,
            "result": None,
            "error": "No AI provider available",
            "local_error": local_error,
            "safety_matches": safety_matches
        }


orchestrator = AegisAIOrchestrator()
