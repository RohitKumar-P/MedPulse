from fastapi import (
    APIRouter,
    HTTPException
)

from app.services.prediction_service import (
    predict_heart,
    predict_diabetes
)

from app.services.disease_model_service import (
    predict_disease,
    get_model_schema
)


router = APIRouter(
    prefix="/predict",
    tags=["Prediction"]
)


@router.post("/heart")
def heart_prediction(data: dict):
    try:
        return predict_heart(data)

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post("/diabetes")
def diabetes_prediction(data: dict):
    try:
        return predict_diabetes(data)

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get("/heart/schema")
def heart_schema():
    try:
        from app.services.disease_model_service import get_model_schema
        return get_model_schema("heart_disease")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/diabetes/schema")
def diabetes_schema():
    try:
        from app.services.disease_model_service import get_model_schema
        return get_model_schema("diabetes")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/liver")
def liver_prediction(data: dict):
    try:
        return predict_disease(
            "liver_disease",
            data,
            "liver_disease"
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post("/ckd")
def ckd_prediction(data: dict):
    try:
        return predict_disease(
            "chronic_kidney_disease",
            data,
            "chronic_kidney_disease"
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get("/liver/schema")
def liver_schema():
    try:
        return get_model_schema(
            "liver_disease"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/ckd/schema")
def ckd_schema():
    try:
        return get_model_schema(
            "chronic_kidney_disease"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/breast-cancer")
def breast_cancer_prediction(data: dict):
    try:
        return predict_disease(
            "breast_cancer",
            data,
            "breast_cancer"
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get("/breast-cancer/schema")
def breast_cancer_schema():
    try:
        return get_model_schema(
            "breast_cancer"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/parkinsons")
def parkinsons_prediction(data: dict):
    try:
        return predict_disease(
            "parkinsons",
            data,
            "parkinsons"
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get("/parkinsons/schema")
def parkinsons_schema():
    try:
        return get_model_schema(
            "parkinsons"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/thyroid")
def thyroid_prediction(data: dict):
    try:
        return predict_disease(
            "thyroid",
            data,
            "thyroid_disorder"
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get("/thyroid/schema")
def thyroid_schema():
    try:
        return get_model_schema(
            "thyroid"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/stroke")
def stroke_prediction(data: dict):
    try:
        return predict_disease(
            "stroke_risk",
            data,
            "stroke_risk"
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get("/stroke/schema")
def stroke_schema():
    try:
        return get_model_schema(
            "stroke_risk"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/anemia")
def anemia_prediction(data: dict):
    try:
        return predict_disease(
            "anemia",
            data,
            "anemia"
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get("/anemia/schema")
def anemia_schema():
    try:
        return get_model_schema(
            "anemia"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )



@router.post("/hypertension")
def hypertension_prediction(data: dict):
    try:
        return predict_disease(
            "hypertension",
            data,
            "hypertension"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get("/hypertension/schema")
def hypertension_schema():
    try:
        return get_model_schema(
            "hypertension"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/explain")
async def explain_prediction(data: dict):

    from app.ai.orchestrator import orchestrator

    required = [
        "disease",
        "risk_level",
        "risk_score"
    ]

    missing = [
        key for key in required
        if key not in data
    ]

    if missing:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Incomplete screening result",
                "missing": missing
            }
        )

    probability = data.get("probability")
    factors = data.get("contributing_factors", [])
    context = data.get("user_context", {})

    prompt = f"""
Explain this MedPulse screening result to a normal person.

Disease/condition:
{data["disease"]}

Risk level:
{data["risk_level"]}

Risk score:
{data["risk_score"]}

Probability:
{probability}

Contributing factors:
{factors}

User context:
{context}

Rules:
- Screening only, never confirmed diagnosis.
- Use simple language.
- Explain medical terminology.
- Never invent information.
- If a blood test, scan, or medical report is required, say so.
- Do not prescribe medication.
- Give clear next steps.
- Mention urgent professional care only when appropriate.

Return:
1. What this means
2. Why this result occurred
3. What information may still be needed
4. What to do next
"""

    try:
        response = await orchestrator.local.generate(prompt)

        return {
            "status": "success",
            "provider": "ollama",
            "response": response
        }

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc)
        )
