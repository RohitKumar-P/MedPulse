import json
from pathlib import Path

import joblib
import pandas as pd

from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_validate
)

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (
    RandomForestClassifier,
    HistGradientBoostingClassifier
)
from sklearn.svm import SVC

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


# ============================================================
# PATH
# ============================================================

BASE = Path(
    "ml/disease_models"
)

DATASET = Path(
    "ml/disease_models/datasets/"
    "heart/extracted/processed.cleveland.data"
)

MODEL_PATH = (
    BASE / "heart_disease.joblib"
)

METRICS_PATH = (
    BASE / "heart_disease_metrics.json"
)


# ============================================================
# LOAD UCI CLEVELAND DATASET
# ============================================================

columns = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
    "target"
]

df = pd.read_csv(
    DATASET,
    header=None,
    names=columns,
    na_values="?"
)


print()
print("=== UCI CLEVELAND HEART DISEASE ===")
print("Original samples:", len(df))


# ============================================================
# REMOVE EXACT DUPLICATES
# ============================================================

df = (
    df
    .drop_duplicates()
    .reset_index(drop=True)
)

print(
    "Unique samples:",
    len(df)
)


# ============================================================
# CONVERT TARGET
#
# UCI:
# 0 = no disease
# 1-4 = presence of disease
# ============================================================

df["heart_disease"] = (
    df["target"] > 0
).astype(int)

df = df.drop(
    columns=["target"]
)


# ============================================================
# FEATURES
# ============================================================

features = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal"
]

X = df[features]
y = df["heart_disease"]


print()
print("FEATURES:", features)

print()
print("MISSING VALUES:")
print(
    X.isnull()
    .sum()
    .to_string()
)

print()
print("BINARY CLASS DISTRIBUTION:")
print(
    y.value_counts()
    .sort_index()
)

print()
print(
    "0 = no heart disease"
)

print(
    "1 = heart disease"
)


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print()
print("TRAINING SAMPLES:", len(X_train))
print("TEST SAMPLES:", len(X_test))


# ============================================================
# COMMON PREPROCESSOR
# ============================================================

preprocessor = Pipeline([
    (
        "imputer",
        SimpleImputer(
            strategy="median"
        )
    ),
    (
        "scaler",
        StandardScaler()
    )
])


# ============================================================
# MODELS
# ============================================================

models = {

    "logistic_regression": Pipeline([
        (
            "preprocessor",
            preprocessor
        ),
        (
            "model",
            LogisticRegression(
                max_iter=3000,
                class_weight="balanced",
                random_state=42
            )
        )
    ]),

    "random_forest": Pipeline([
        (
            "preprocessor",
            preprocessor
        ),
        (
            "model",
            RandomForestClassifier(
                n_estimators=500,
                min_samples_leaf=2,
                class_weight="balanced",
                random_state=42,
                n_jobs=-1
            )
        )
    ]),

    "hist_gradient_boosting": Pipeline([
        (
            "preprocessor",
            preprocessor
        ),
        (
            "model",
            HistGradientBoostingClassifier(
                max_iter=200,
                learning_rate=0.05,
                max_leaf_nodes=15,
                l2_regularization=1.0,
                random_state=42
            )
        )
    ]),

    "svm": Pipeline([
        (
            "preprocessor",
            preprocessor
        ),
        (
            "model",
            SVC(
                probability=True,
                class_weight="balanced",
                random_state=42
            )
        )
    ])
}


# ============================================================
# CROSS VALIDATION
# ============================================================

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

scoring = {
    "accuracy": "accuracy",
    "balanced_accuracy": "balanced_accuracy",
    "precision": "precision",
    "recall": "recall",
    "f1": "f1",
    "roc_auc": "roc_auc",
    "average_precision": "average_precision"
}


results = {}


print()
print("=== 5-FOLD CROSS VALIDATION ===")


for name, model in models.items():

    scores = cross_validate(
        model,
        X_train,
        y_train,
        cv=cv,
        scoring=scoring,
        n_jobs=-1
    )

    metrics = {}

    for metric in scoring:

        values = scores[
            "test_" + metric
        ]

        metrics[metric] = round(
            float(values.mean()),
            4
        )

    results[name] = metrics

    print()
    print(name)
    print(
        json.dumps(
            metrics,
            indent=2
        )
    )


# ============================================================
# MODEL SELECTION
#
# Don't optimize raw accuracy alone.
# ============================================================

def model_score(metrics):

    return (
        metrics["f1"] * 0.35
        + metrics["recall"] * 0.25
        + metrics["balanced_accuracy"] * 0.20
        + metrics["roc_auc"] * 0.20
    )


best_name = max(
    results,
    key=lambda name:
        model_score(
            results[name]
        )
)


print()
print(
    "SELECTED MODEL:",
    best_name
)


# ============================================================
# FINAL TRAINING
# ============================================================

best_model = models[
    best_name
]

best_model.fit(
    X_train,
    y_train
)


# ============================================================
# HELD-OUT TEST
# ============================================================

prediction = best_model.predict(
    X_test
)

probability = best_model.predict_proba(
    X_test
)[:, 1]


test_metrics = {

    "accuracy": round(
        accuracy_score(
            y_test,
            prediction
        ),
        4
    ),

    "balanced_accuracy": round(
        balanced_accuracy_score(
            y_test,
            prediction
        ),
        4
    ),

    "precision": round(
        precision_score(
            y_test,
            prediction,
            zero_division=0
        ),
        4
    ),

    "recall": round(
        recall_score(
            y_test,
            prediction,
            zero_division=0
        ),
        4
    ),

    "f1": round(
        f1_score(
            y_test,
            prediction,
            zero_division=0
        ),
        4
    ),

    "roc_auc": round(
        roc_auc_score(
            y_test,
            probability
        ),
        4
    ),

    "average_precision": round(
        average_precision_score(
            y_test,
            probability
        ),
        4
    ),

    "confusion_matrix": (
        confusion_matrix(
            y_test,
            prediction
        ).tolist()
    )
}


print()
print("=== HELD-OUT TEST ===")

print(
    json.dumps(
        test_metrics,
        indent=2
    )
)


# ============================================================
# SAVE ARTIFACT
# ============================================================

artifact = {

    "model": best_model,

    "features": features,

    "positive_class": 1,

    "negative_class": 0,

    "class_names": {
        "0": "no_heart_disease",
        "1": "heart_disease"
    },

    "input_type": (
        "clinical_heart_disease_screening"
    ),

    "dataset": (
        "UCI Heart Disease "
        "Cleveland processed"
    ),

    "samples": len(df),

    "training_samples": len(
        X_train
    ),

    "test_samples": len(
        X_test
    ),

    "selected_model": best_name,

    "cross_validation": results,

    "test_metrics": test_metrics,

    "warning": (
        "Screening/risk estimation only. "
        "Not a medical diagnosis."
    )
}


joblib.dump(
    artifact,
    MODEL_PATH
)


# ============================================================
# SAVE METRICS
# ============================================================

metrics_output = {

    "dataset": (
        "UCI Heart Disease "
        "Cleveland processed"
    ),

    "samples": len(df),

    "features": len(features),

    "selected_model": best_name,

    "cross_validation": results,

    "test_metrics": test_metrics
}


METRICS_PATH.write_text(
    json.dumps(
        metrics_output,
        indent=2
    ),
    encoding="utf-8"
)


print()
print("HEART DISEASE MODEL: CREATED")
print(
    "MODEL:",
    MODEL_PATH
)

print(
    "METRICS:",
    METRICS_PATH
)

