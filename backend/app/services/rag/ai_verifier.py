import os
import requests


OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://127.0.0.1:11434"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "gemma3:4b"
)


def verify_prediction(
    disease: str,
    probability: float,
    risk_level: str,
    factors,
    evidence: list[str] | None = None,
    patient_context: dict | None = None,
    symptoms: list[str] | None = None,
    screening_answers: dict | None = None,
):
    evidence = evidence or []
    patient_context = patient_context or {}
    symptoms = symptoms or []
    screening_answers = screening_answers or []

    prompt = f"""
You are MedPulse's AI explanation layer.

You are NOT a doctor and you do NOT diagnose patients.

Your task is to explain an existing machine-learning screening result.

========================
NON-NEGOTIABLE RULES
========================

1. The ML result is authoritative for the numerical prediction.
2. NEVER change the probability.
3. NEVER change the risk level.
4. NEVER say the patient definitely has the disease.
5. NEVER invent patient information.
6. NEVER infer a patient fact that was not explicitly supplied.
7. NEVER claim that a factor influenced the ML result unless that
   factor appears in PATIENT MODEL FACTORS.
8. Patient MODEL FACTORS are model explanations, NOT proof of disease.
9. Do not treat global feature importance as patient-specific evidence.
10. Use MEDICAL EVIDENCE only for general medical explanations.
11. Do not use medical evidence to invent patient facts.
12. If information is missing, say that it is missing.
13. Use simple everyday language.
14. Avoid complicated medical terminology.
15. Do not prescribe medication or dosage.
16. Do not tell the user to stop prescribed treatment.
17. If symptoms appear urgent, recommend prompt professional care.
18. Do not fabricate tests, symptoms, history, medications or reports.
19. Always complete ALL required sections.
20. Keep the answer concise.

========================
ML SCREENING RESULT
========================

Condition:
{disease}

Probability:
{probability:.4f}

Risk level:
{risk_level}

========================
PATIENT MODEL FACTORS
========================

{factors}

IMPORTANT:
These are the only patient-specific model factors you may discuss
as reasons for the prediction.

========================
PATIENT CONTEXT
========================

{patient_context}

========================
REPORTED SYMPTOMS
========================

{symptoms}

========================
SCREENING ANSWERS
========================

{screening_answers}

========================
MEDICAL EVIDENCE
========================

{evidence}

========================
REQUIRED RESPONSE
========================

Use EXACTLY these headings:

WHAT THIS MEANS

Explain the ML screening result in simple language.
Include the probability and risk level.
Clearly state that this is NOT a confirmed diagnosis.

WHY THE MODEL GAVE THIS RESULT

Mention only the supplied PATIENT MODEL FACTORS.
Do not invent additional factors.
Do not claim that a factor caused the condition.

WHAT WE KNOW

Mention only information explicitly supplied in:
- patient context
- reported symptoms
- screening answers
- patient model factors

If none is supplied, say that.

WHAT IS STILL MISSING

Identify information that could improve the screening assessment.
Do not invent a specific test unless supported by the supplied
medical evidence.

WHAT TO DO NEXT

Give safe, practical next steps.
Do not prescribe medication.
If appropriate, recommend discussing the result with a healthcare
professional.

FINAL SAFETY NOTE

State clearly:

"This is a screening estimate, not a confirmed diagnosis."

========================
FINAL CHECK
========================

Before responding, verify:

- Probability unchanged: YES
- Risk level unchanged: YES
- No invented patient facts: YES
- No invented symptoms: YES
- No invented medical history: YES
- No invented model factors: YES
- All six sections completed: YES

Return only the patient-facing explanation.
"""

    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.0,
                "num_ctx": 8192,
            },
        },
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    return {
        "model": OLLAMA_MODEL,
        "verification": data.get("response", "").strip(),
        "ml_probability": probability,
        "ml_risk_level": risk_level,
        "verified_by_ai": True,
        "is_diagnosis": False,
        "evidence_count": len(evidence),
    }
