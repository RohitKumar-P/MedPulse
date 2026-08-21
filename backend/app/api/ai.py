from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.ai.orchestrator import orchestrator
from app.services.rag.pipeline import build_ai_verification


router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


class AIInput(BaseModel):
    text: str = Field(
        min_length=1,
        max_length=12000
    )


class ScreeningExplanation(BaseModel):

    disease: str

    risk_level: str

    risk_score: float

    probability: float | None = None

    # General model factors / backwards compatibility
    factors: list = Field(
        default_factory=list
    )

    # Patient-specific SHAP factors
    patient_factors: list = Field(
        default_factory=list
    )

    user_context: dict = Field(
        default_factory=dict
    )

    symptoms: list[str] = Field(
        default_factory=list
    )

    screening_answers: dict = Field(
        default_factory=dict
    )

    query: str = ""


@router.post("/extract")
async def extract(payload: AIInput):

    try:
        return await orchestrator.extract(
            payload.text
        )

    except Exception as exc:

        raise HTTPException(
            status_code=503,
            detail=f"AI extraction unavailable: {exc}"
        )


@router.post("/explain-screening")
async def explain_screening(
    payload: ScreeningExplanation
):

    try:

        # Prefer patient-specific SHAP factors.
        # Fall back to the old factors field so
        # existing frontend code does not break.

        model_factors = (
            payload.patient_factors
            if payload.patient_factors
            else payload.factors
        )

        probability = (
            payload.probability
            if payload.probability is not None
            else payload.risk_score / 100.0
        )

        result = build_ai_verification(

            disease=payload.disease,

            probability=probability,

            risk_level=payload.risk_level,

            factors=model_factors,

            query=payload.query,

            patient_context=payload.user_context,

            symptoms=payload.symptoms,

            screening_answers=payload.screening_answers,
        )

        return {

            "status": "success",

            "provider": "ollama",

            "model": result.get(
                "model"
            ),

            "response": result.get(
                "verification",
                ""
            ),

            "ml_probability": probability,

            "ml_risk_level": payload.risk_level,

            "risk_score": payload.risk_score,

            "verified_by_ai": True,

            "is_diagnosis": False,

            "prediction_source": "calibrated_ml_model",

            "rag_enabled": True,

            "evidence_count": result.get(
                "evidence_count",
                0
            ),

            "patient_factors": model_factors,

        }

    except Exception as exc:

        raise HTTPException(

            status_code=503,

            detail={
                "message":
                    "AI/RAG verification unavailable",

                "error": str(exc)
            }
        )
