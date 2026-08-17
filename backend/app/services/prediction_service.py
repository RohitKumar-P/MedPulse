import os
import joblib
import numpy as np
import pandas as pd


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

MODEL_DIR = os.path.join(BASE_DIR, "ml", "models")


diabetes_model = joblib.load(
    os.path.join(MODEL_DIR, "diabetes_model.joblib")
)

diabetes_features = joblib.load(
    os.path.join(MODEL_DIR, "diabetes_features.joblib")
)


def _require_features(data, required, model_name):
    missing = [
        feature
        for feature in required
        if feature not in data or data[feature] is None
    ]

    if missing:
        raise ValueError(
            f"{model_name} missing required features: "
            + ", ".join(missing)
        )


def risk_level(score):
    if score < 30:
        return "low"

    if score < 60:
        return "moderate"

    return "elevated"


def _pipeline_classifier(calibrated):
    estimator = getattr(
        calibrated,
        "estimator",
        None
    )

    if estimator is None:
        return None

    if hasattr(estimator, "named_steps"):
        return estimator.named_steps.get(
            "classifier"
        )

    return None


def get_factors(
    model,
    features,
    values=None
):
    return _standard_feature_importance(
        model,
        features
    )


def predict_heart(data):
    """
    Adapter for the new UCI Cleveland heart-disease model.

    Keeps the existing MedPulse frontend field names while
    translating them into the feature names expected by
    heart_disease.joblib.
    """

    from app.services.disease_model_service import predict_disease

    required = [
        "age",
        "sex",
        "chest_pain",
        "resting_bp",
        "cholesterol",
        "fasting_blood_sugar",
        "resting_ecg",
        "max_heart_rate",
        "exercise_angina",
        "oldpeak",
        "slope",
        "vessels",
        "thalassemia"
    ]

    _require_features(
        data,
        required,
        "heart"
    )

    model_input = {
        "age": data["age"],
        "sex": data["sex"],
        "cp": data["chest_pain"],
        "trestbps": data["resting_bp"],
        "chol": data["cholesterol"],
        "fbs": data["fasting_blood_sugar"],
        "restecg": data["resting_ecg"],
        "thalach": data["max_heart_rate"],
        "exang": data["exercise_angina"],
        "oldpeak": data["oldpeak"],
        "slope": data["slope"],
        "ca": data["vessels"],
        "thal": data["thalassemia"]
    }

    result = predict_disease(
        "heart_disease",
        model_input,
        "cardiovascular"
    )

    return result


def predict_diabetes(data):

    required = [
        "pregnancies",
        "glucose",
        "blood_pressure",
        "skin_thickness",
        "insulin",
        "bmi",
        "diabetes_pedigree",
        "age"
    ]

    _require_features(
        data,
        required,
        "diabetes"
    )

    values = [
        data["pregnancies"],
        data["glucose"],
        data["blood_pressure"],
        data["skin_thickness"],
        data["insulin"],
        data["bmi"],
        data["diabetes_pedigree"],
        data["age"]
    ]

    df = pd.DataFrame(
        [values],
        columns=diabetes_features
    )

    probability = float(
        diabetes_model.predict_proba(df)[0][1]
    )

    score = round(
        probability * 100
    )

    return {
        "disease": "diabetes",
        "risk_score": score,
        "risk_level": risk_level(score),
        "probability": round(
            probability,
            4
        ),
        "contributing_factors": get_factors(
            diabetes_model,
            diabetes_features,
            values
        )
    }
