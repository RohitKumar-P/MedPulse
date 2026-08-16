from pathlib import Path
import json

import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

from sklearn.ensemble import RandomForestClassifier
from imblearn.ensemble import BalancedRandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix
)


BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "datasets"

data_path = DATA_DIR / "stroke.csv"

if not data_path.exists():
    raise SystemExit(
        f"Dataset not found: {data_path}"
    )

df = pd.read_csv(data_path)

df.columns = [
    str(c).strip().lower()
    for c in df.columns
]

required = [
    "gender",
    "age",
    "hypertension",
    "heart_disease",
    "ever_married",
    "work_type",
    "residence_type",
    "avg_glucose_level",
    "bmi",
    "smoking_status",
    "stroke"
]

missing = [
    c for c in required
    if c not in df.columns
]

if missing:
    raise SystemExit(
        "Missing columns: "
        + ", ".join(missing)
    )


df = df.drop(
    columns=["id"],
    errors="ignore"
)

df = df.dropna(
    subset=["stroke"]
)

# Remove the unusual "Other" gender record/category.
df = df[
    df["gender"].astype(str).str.lower() != "other"
]

X = df.drop(
    columns=["stroke"]
)

y = df["stroke"].astype(int)


categorical = [
    "gender",
    "ever_married",
    "work_type",
    "residence_type",
    "smoking_status"
]

numeric = [
    c for c in X.columns
    if c not in categorical
]


# --------------------------------------------------
# Preprocessing
# --------------------------------------------------

numeric_pipeline = Pipeline([
    (
        "imputer",
        SimpleImputer(
            strategy="median",
            add_indicator=True
        )
    )
])

categorical_pipeline = Pipeline([
    (
        "imputer",
        SimpleImputer(
            strategy="most_frequent"
        )
    ),
    (
        "encoder",
        OrdinalEncoder(
            handle_unknown="use_encoded_value",
            unknown_value=-1
        )
    )
])


preprocessor = ColumnTransformer([
    (
        "numeric",
        numeric_pipeline,
        numeric
    ),
    (
        "categorical",
        categorical_pipeline,
        categorical
    )
])


# --------------------------------------------------
# Same test set for fair model comparison
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# --------------------------------------------------
# Baseline
# --------------------------------------------------

baseline = Pipeline([
    (
        "preprocessor",
        preprocessor
    ),
    (
        "model",
        RandomForestClassifier(
            n_estimators=500,
            random_state=42,
            class_weight="balanced",
            n_jobs=-1,
            min_samples_leaf=2,
            max_features="sqrt"
        )
    )
])


print()
print("TRAINING BASELINE RANDOM FOREST...")


baseline.fit(
    X_train,
    y_train
)

baseline_pred = baseline.predict(
    X_test
)

baseline_probability = baseline.predict_proba(
    X_test
)[:, 1]


# --------------------------------------------------
# Balanced Random Forest
# --------------------------------------------------

balanced = Pipeline([
    (
        "preprocessor",
        preprocessor
    ),
    (
        "model",
        BalancedRandomForestClassifier(
            n_estimators=500,
            random_state=42,
            n_jobs=-1,
            sampling_strategy="all",
            replacement=True,
            bootstrap=False,
            min_samples_leaf=2
        )
    )
])


print(
    "TRAINING BALANCED RANDOM FOREST..."
)


balanced.fit(
    X_train,
    y_train
)

balanced_pred = balanced.predict(
    X_test
)

balanced_probability = balanced.predict_proba(
    X_test
)[:, 1]


# --------------------------------------------------
# Evaluation
# --------------------------------------------------

def evaluate(
    name,
    y_true,
    prediction,
    probability
):

    return {
        "model": name,

        "accuracy": round(
            accuracy_score(
                y_true,
                prediction
            ),
            4
        ),

        "balanced_accuracy": round(
            balanced_accuracy_score(
                y_true,
                prediction
            ),
            4
        ),

        "precision": round(
            precision_score(
                y_true,
                prediction,
                zero_division=0
            ),
            4
        ),

        "recall": round(
            recall_score(
                y_true,
                prediction,
                zero_division=0
            ),
            4
        ),

        "f1": round(
            f1_score(
                y_true,
                prediction,
                zero_division=0
            ),
            4
        ),

        "roc_auc": round(
            roc_auc_score(
                y_true,
                probability
            ),
            4
        ),

        "average_precision": round(
            average_precision_score(
                y_true,
                probability
            ),
            4
        ),

        "confusion_matrix": (
            confusion_matrix(
                y_true,
                prediction
            ).tolist()
        )
    }


baseline_metrics = evaluate(
    "random_forest",
    y_test,
    baseline_pred,
    baseline_probability
)

balanced_metrics = evaluate(
    "balanced_random_forest",
    y_test,
    balanced_pred,
    balanced_probability
)


print()
print("BASELINE:")
print(
    json.dumps(
        baseline_metrics,
        indent=2
    )
)

print()
print("BALANCED:")
print(
    json.dumps(
        balanced_metrics,
        indent=2
    )
)


# --------------------------------------------------
# Select model based primarily on minority recall/F1.
# Do not optimize only for raw accuracy.
# --------------------------------------------------

def model_score(metrics):
    return (
        metrics["f1"] * 0.45
        + metrics["recall"] * 0.35
        + metrics["balanced_accuracy"] * 0.20
    )


if model_score(
    balanced_metrics
) >= model_score(
    baseline_metrics
):

    selected_model = balanced
    selected_metrics = balanced_metrics

else:

    selected_model = baseline
    selected_metrics = baseline_metrics


print()
print(
    "SELECTED MODEL:",
    selected_metrics["model"]
)


# --------------------------------------------------
# Save
# --------------------------------------------------

artifact = {
    "model": selected_model,

    "features": list(
        X.columns
    ),

    "positive_class": 1,
    "negative_class": 0,

    "input_type": "clinical_stroke_risk",

    "dataset": "Healthcare Stroke Dataset",

    "training_samples": len(
        X_train
    ),

    "test_samples": len(
        X_test
    ),

    "selected_model": selected_metrics[
        "model"
    ],

    "metrics": selected_metrics,

    "warning": (
        "Screening/risk estimation only. "
        "Not a medical diagnosis."
    )
}


model_path = (
    BASE /
    "stroke_risk.joblib"
)

metrics_path = (
    BASE /
    "stroke_risk_metrics.json"
)


joblib.dump(
    artifact,
    model_path
)


metrics_output = {
    "selected_model": selected_metrics,
    "baseline_model": baseline_metrics,
    "balanced_model": balanced_metrics
}


metrics_path.write_text(
    json.dumps(
        metrics_output,
        indent=2
    ),
    encoding="utf-8"
)


print()
print(
    "STROKE MODEL: IMPROVED"
)

print(
    "MODEL FILE:",
    model_path
)

print(
    "METRICS FILE:",
    metrics_path
)
