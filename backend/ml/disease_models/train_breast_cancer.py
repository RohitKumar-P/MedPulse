from pathlib import Path
import json
import joblib

from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)


BASE = Path(__file__).resolve().parent

data = load_breast_cancer()

X = data.data
y = data.target

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


model = Pipeline([
    (
        "imputer",
        SimpleImputer(strategy="median")
    ),
    (
        "scaler",
        StandardScaler()
    ),
    (
        "classifier",
        LogisticRegression(
            max_iter=5000,
            random_state=42
        )
    )
])


model.fit(
    X_train,
    y_train
)


predictions = model.predict(
    X_test
)


metrics = {
    "model": "breast_cancer",
    "dataset": "Wisconsin Diagnostic Breast Cancer",
    "samples": len(X),
    "features": X.shape[1],
    "accuracy": round(
        accuracy_score(
            y_test,
            predictions
        ),
        4
    ),
    "precision": round(
        precision_score(
            y_test,
            predictions,
            zero_division=0
        ),
        4
    ),
    "recall": round(
        recall_score(
            y_test,
            predictions,
            zero_division=0
        ),
        4
    ),
    "f1": round(
        f1_score(
            y_test,
            predictions,
            zero_division=0
        ),
        4
    )
}


artifact = {
    "model": model,
    "features": list(
        data.feature_names
    ),
    "positive_class": (
        "malignant"
    )
}


joblib.dump(
    artifact,
    BASE / "breast_cancer.joblib"
)


(
    BASE
    / "breast_cancer_metrics.json"
).write_text(
    json.dumps(
        metrics,
        indent=2
    ),
    encoding="utf-8"
)


print(
    json.dumps(
        metrics,
        indent=2
    )
)

print(
    "MODEL:",
    BASE / "breast_cancer.joblib"
)
