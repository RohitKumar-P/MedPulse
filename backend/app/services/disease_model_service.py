from pathlib import Path
import json
import joblib
import pandas as pd
import numpy as np


BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_DIR = (
    BASE_DIR
    / "ml"
    / "disease_models"
)


def load_artifact(name):
    path = MODEL_DIR / f"{name}.joblib"

    if not path.exists():
        raise FileNotFoundError(
            f"Model not found: {path}"
        )

    artifact = joblib.load(path)

    if not isinstance(artifact, dict):
        raise ValueError(
            f"Invalid model artifact: {name}"
        )

    if "model" not in artifact:
        raise ValueError(
            f"Model artifact missing model: {name}"
        )

    if "features" not in artifact:
        raise ValueError(
            f"Model artifact missing features: {name}"
        )

    return artifact


def risk_level(score):
    if score < 30:
        return "low"

    if score < 60:
        return "moderate"

    return "elevated"


def _prepare_input(data, expected_features):
    """
    Accept raw clinical fields and categorical values.

    Training used pd.get_dummies(), so reproduce that
    transformation and align to the saved feature columns.
    """

    if not isinstance(data, dict):
        raise ValueError(
            "Prediction input must be a JSON object."
        )

    if not data:
        raise ValueError(
            "Prediction input cannot be empty."
        )

    df = pd.DataFrame([data])

    # Convert numeric-looking values where possible.
    for column in df.columns:
        if isinstance(df[column].iloc[0], str):
            value = df[column].iloc[0].strip()

            try:
                df[column] = pd.to_numeric(
                    df[column],
                    errors="ignore"
                )
            except Exception:
                pass

    # Reproduce training-time one-hot encoding.
    df = pd.get_dummies(
        df,
        drop_first=False
    )

    # Convert boolean dummy columns to numeric.
    for column in df.columns:
        if df[column].dtype == bool:
            df[column] = df[column].astype(int)

    # Align with exactly the columns used during training.
    df = df.reindex(
        columns=expected_features,
        fill_value=0
    )

    return df


def _positive_probability(
    model,
    probability,
    positive_class=None
):
    """
    Determine the probability of the clinically
    positive/risk class.

    positive_class may be explicitly supplied by
    the saved model artifact.
    """

    classes = list(
        getattr(model, "classes_", [])
    )

    if len(classes) != 2:
        return float(
            np.max(probability)
        )

    if positive_class is not None:
        target = str(
            positive_class
        ).strip().lower()

        for index, value in enumerate(classes):
            if str(value).strip().lower() == target:
                return float(
                    probability[index]
                )

    negative_values = {
        "0",
        "0.0",
        "false",
        "no",
        "negative",
        "normal",
        "notckd",
        "not_ckd",
        "benign",
        "absent",
        "healthy"
    }

    positive_index = 1

    for index, value in enumerate(classes):
        normalized = str(value).strip().lower()

        if normalized in negative_values:
            continue

        positive_index = index
        break

    return float(
        probability[positive_index]
    )


def predict_disease(
    disease_name,
    data,
    display_name=None
):
    artifact = load_artifact(
        disease_name
    )

    model = artifact["model"]
    features = artifact["features"]

    df = _prepare_input(
        data,
        features
    )

    probabilities = model.predict_proba(df)[0]

    probability = _positive_probability(
        model,
        probabilities,
        artifact.get("positive_class")
    )

    score = round(
        probability * 100
    )

    return {
        "disease": display_name or disease_name,
        "risk_score": score,
        "risk_level": risk_level(score),
        "probability": round(
            probability,
            4
        ),
        "model": disease_name,
        "model_features": len(features),
        "disclaimer": (
            "This is an ML-based screening estimate "
            "and is not a medical diagnosis."
        )
    }


def get_model_schema(disease_name):
    artifact = load_artifact(
        disease_name
    )

    return {
        "disease": disease_name,
        "features": artifact["features"],
        "feature_count": len(
            artifact["features"]
        )
    }
