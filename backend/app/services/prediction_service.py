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


def _patient_shap_explanation(model, values, feature_names):
    """
    Generate patient-specific SHAP explanations.

    The calibrated model contains multiple fitted estimators.
    SHAP is calculated independently for each fitted estimator
    and then averaged across them.

    Returns factors ordered by absolute contribution.

    Positive SHAP:
        pushes the prediction toward class 1.

    Negative SHAP:
        pushes the prediction toward class 0.
    """

    try:
        import numpy as np
        import pandas as pd
        import shap

        # Ensure feature order exactly matches training order.
        row = {
            feature: values.get(feature)
            for feature in feature_names
        }

        df = pd.DataFrame([row], columns=feature_names)

        all_values = []

        # Use the FIVE FITTED calibrated estimators.
        for calibrated in getattr(
            model,
            "calibrated_classifiers_",
            []
        ):

            pipeline = calibrated.estimator

            preprocessor = pipeline.named_steps[
                "preprocessor"
            ]

            classifier = pipeline.named_steps[
                "classifier"
            ]

            # Apply exactly the same preprocessing
            # used during model training.
            transformed = preprocessor.transform(df)

            explainer = shap.TreeExplainer(
                classifier
            )

            shap_values = explainer.shap_values(
                transformed
            )

            shap_values = np.asarray(
                shap_values
            )

            # Binary classifier:
            # shape = (samples, features, classes)
            if shap_values.ndim == 3:

                if shap_values.shape[-1] >= 2:
                    current = shap_values[
                        0,
                        :,
                        1
                    ]
                else:
                    current = shap_values[
                        0,
                        :,
                        0
                    ]

            # Older SHAP format:
            # shape = (samples, features)
            elif shap_values.ndim == 2:

                current = shap_values[0]

            else:
                continue

            all_values.append(
                np.asarray(
                    current,
                    dtype=float
                )
            )

        if not all_values:
            return []

        # Average explanation across calibrated models.
        avg_values = np.mean(
            np.vstack(all_values),
            axis=0
        )

        avg_values = np.nan_to_num(
            avg_values,
            nan=0.0,
            posinf=0.0,
            neginf=0.0
        )

        results = []

        for feature, contribution in zip(
            feature_names,
            avg_values
        ):

            value = values.get(feature)

            results.append({
                "feature": str(feature),
                "value": value,
                "shap_value": round(
                    float(contribution),
                    6
                ),
                "direction": (
                    "increases_risk"
                    if contribution > 0
                    else "decreases_risk"
                    if contribution < 0
                    else "neutral"
                ),
                "absolute_contribution": round(
                    float(abs(contribution)),
                    6
                )
            })

        # Strongest patient-specific factors first.
        results.sort(
            key=lambda x: x[
                "absolute_contribution"
            ],
            reverse=True
        )

        return results

    except Exception as exc:

        # Explanation failure must NEVER
        # break the medical prediction.
        print(
            f"SHAP explanation warning: {exc}"
        )

        return []

def _standard_feature_importance(model, feature_names):
    """
    Extract feature importance from:
      - normal sklearn estimators
      - Pipelines
      - CalibratedClassifierCV
      - calibrated Pipeline estimators

    Returns a list of:
      {"feature": name, "importance": value}
    """

    import numpy as np

    def extract_estimator(obj):
        # Pipeline -> final estimator
        if hasattr(obj, "steps"):
            try:
                return obj.steps[-1][1]
            except Exception:
                return obj

        return obj

    def extract_values(obj):
        # Direct feature_importances_
        if hasattr(obj, "feature_importances_"):
            return np.asarray(
                obj.feature_importances_,
                dtype=float
            )

        # Direct coefficients
        if hasattr(obj, "coef_"):
            coef = np.asarray(
                obj.coef_,
                dtype=float
            )

            if coef.ndim > 1:
                coef = np.mean(np.abs(coef), axis=0)
            else:
                coef = np.abs(coef)

            return coef

        return None

    candidates = []

    # Normal estimator
    candidates.append(model)

    # CalibratedClassifierCV
    if hasattr(model, "estimator"):
        candidates.append(model.estimator)

    if hasattr(model, "calibrated_classifiers_"):
        for calibrated in model.calibrated_classifiers_:
            if hasattr(calibrated, "estimator"):
                candidates.append(calibrated.estimator)

    for candidate in candidates:
        estimator = extract_estimator(candidate)
        values = extract_values(estimator)

        if values is None:
            continue

        if len(values) != len(feature_names):
            continue

        values = np.nan_to_num(
            values,
            nan=0.0,
            posinf=0.0,
            neginf=0.0
        )

        results = []

        for name, value in zip(feature_names, values):
            results.append({
                "feature": str(name),
                "importance": float(abs(value))
            })

        results.sort(
            key=lambda x: x["importance"],
            reverse=True
        )

        return results

    return []

def get_factors(model, features, values=None):
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

    # -------------------------------------------------
    # PRIMARY ML PREDICTION
    # -------------------------------------------------

    probability = float(
        diabetes_model.predict_proba(df)[0][1]
    )

    score = round(
        probability * 100
    )

    # -------------------------------------------------
    # PATIENT-SPECIFIC SHAP EXPLANATION
    # -------------------------------------------------

    patient_data = {
        feature: value
        for feature, value in zip(
            diabetes_features,
            values
        )
    }

    patient_factors = _patient_shap_explanation(
        diabetes_model,
        patient_data,
        diabetes_features
    )

    # Keep the strongest clinically relevant
    # patient-specific factors.
    patient_factors = patient_factors[:5]

    # -------------------------------------------------
    # RESULT
    # -------------------------------------------------

    return {
        "disease": "diabetes",

        "risk_score": score,

        "risk_level": risk_level(score),

        "probability": round(
            probability,
            4
        ),

        # Backward-compatible field.
        "contributing_factors": get_factors(
            diabetes_model,
            diabetes_features,
            values
        ),

        # New patient-specific explanation.
        "patient_factors": patient_factors,

        # Explicitly identify what generated
        # the numerical prediction.
        "prediction_source": "calibrated_ml_model",

        # Prevent frontend/AI from treating this
        # as a confirmed medical diagnosis.
        "is_diagnosis": False,

        "screening_result": True
    }


