from .retriever import retrieve_evidence
from .ai_verifier import verify_prediction


def build_ai_verification(
    disease: str,
    probability: float,
    risk_level: str,
    factors,
    query: str = "",
    patient_context: dict | None = None,
    symptoms: list[str] | None = None,
    screening_answers: dict | None = None,
):

    patient_context = patient_context or {}
    symptoms = symptoms or []
    screening_answers = screening_answers or {}

    evidence_query = query.strip()

    if not evidence_query:
        evidence_query = (
            f"{disease} health screening "
            f"symptoms risk factors evaluation"
        )

    evidence = retrieve_evidence(
        disease=disease,
        query=evidence_query,
    )

    result = verify_prediction(
        disease=disease,
        probability=probability,
        risk_level=risk_level,
        factors=factors,
        evidence=evidence,
        patient_context=patient_context,
        symptoms=symptoms,
        screening_answers=screening_answers,
    )

    result["evidence_count"] = len(evidence)

    return result
