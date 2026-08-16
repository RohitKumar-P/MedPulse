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

heart_model = joblib.load(
    os.path.join(MODEL_DIR, "heart_model.joblib")
)

heart_features = joblib.load(
    os.path.join(MODEL_DIR, "heart_features.joblib")
)

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


def _heart_feature_importance(model, features):

    all_importances = []

    for calibrated in model.calibrated_classifiers_:

        pipeline = getattr(
            calibrated,
            "estimator",
            None
        )

        if pipeline is None:
            continue

        classifier = _pipeline_classifier(
            calibrated
        )

        if classifier is None:
            continue

        if not hasattr(
            classifier,
            "feature_importances_"
        ):
            continue

        raw_importance = np.asarray(
            classifier.feature_importances_,
            dtype=float
        )

        preprocessor = pipeline.named_steps.get(
            "preprocessor"
        )

        if preprocessor is None:
            continue

        try:
            encoded_names = (
                preprocessor
                .get_feature_names_out()
            )
        except Exception:
            continue

        if len(encoded_names) != len(
            raw_importance
        ):
            continue

        grouped = {
            feature: 0.0
            for feature in features
        }

        for encoded_name, importance in zip(
            encoded_names,
            raw_importance
        ):

            name = str(encoded_name)

            matched = False

            for feature in features:

                if (
                    name.endswith(
                        "__" + feature
                    )
                    or name.startswith(
                        "numeric__" + feature
                    )
                    or name.startswith(
                        "categorical__" + feature
                    )
                ):
                    grouped[feature] += float(
                        importance
                    )
                    matched = True
                    break

            if not matched:

                for feature in features:

                    if (
                        f"__{feature}_"
                        in name
                        or
                        name.startswith(
                            feature + "_"
                        )
                    ):
                        grouped[feature] += float(
                            importance
                        )
                        break

        all_importances.append(
            [
                grouped[feature]
                for feature in features
            ]
        )

    if not all_importances:
        return []

    averaged = np.mean(
        np.asarray(all_importances),
        axis=0
    )

    factors = []

    for feature, impact in zip(
        features,
        averaged
    ):
        factors.append(
            {
                "factor": feature,
                "impact": round(
                    float(impact),
                    6
                )
            }
        )

    factors.sort(
        key=lambda item: item["impact"],
        reverse=True
    )

    return factors[:5]


def _standard_feature_importance(
    model,
    features
):

    all_importances = []

    for calibrated in model.calibrated_classifiers_:

        pipeline = getattr(
            calibrated,
            "estimator",
            None
        )

        if pipeline is None:
            continue

        classifier = _pipeline_classifier(
            calibrated
        )

        if classifier is None:
            continue

        if not hasattr(
            classifier,
            "feature_importances_"
        ):
            continue

        values = np.asarray(
            classifier.feature_importances_,
            dtype=float
        )

        if len(values) == len(features):
            all_importances.append(values)

    if not all_importances:
        return []

    averaged = np.mean(
        np.vstack(all_importances),
        axis=0
    )

    factors = []

    for feature, impact in zip(
        features,
        averaged
    ):
        factors.append(
            {
                "factor": feature,
                "impact": round(
                    float(impact),
                    6
                )
            }
        )

    factors.sort(
        key=lambda item: item["impact"],
        reverse=True
    )

    return factors[:5]


def get_factors(
    model,
    features,
    values=None
):

    # Heart model requires grouping of
    # one-hot encoded categorical features.
    if model is heart_model:
        factors = _heart_feature_importance(
            model,
            features
        )

        if factors:
            return factors

    # Diabetes model has one feature per
    # input column after preprocessing.
    return _standard_feature_importance(
        model,
        features
    )


def predict_heart(data):

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

    values = [
        data["age"],
        data["sex"],
        data["chest_pain"],
        data["resting_bp"],
        data["cholesterol"],
        data["fasting_blood_sugar"],
        data["resting_ecg"],
        data["max_heart_rate"],
        data["exercise_angina"],
        data["oldpeak"],
        data["slope"],
        data["vessels"],
        data["thalassemia"]
    ]

    df = pd.DataFrame(
        [values],
        columns=heart_features
    )

    probability = float(
        heart_model.predict_proba(df)[0][1]
    )

    score = round(
        probability * 100
    )

    return {
        "disease": "cardiovascular",
        "risk_score": score,
        "risk_level": risk_level(score),
        "probability": round(
            probability,
            4
        ),
        "contributing_factors": get_factors(
            heart_model,
            heart_features,
            values
        )
    }


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
