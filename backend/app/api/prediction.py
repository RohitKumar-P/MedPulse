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
