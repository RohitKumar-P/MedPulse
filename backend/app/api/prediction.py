from fastapi import APIRouter, HTTPException
from app.services.prediction_service import predict_heart, predict_diabetes

router = APIRouter(prefix="/predict", tags=["Prediction"])


@router.post("/heart")
def heart_prediction(data: dict):
    try:
        return predict_heart(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/diabetes")
def diabetes_prediction(data: dict):
    try:
        return predict_diabetes(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
