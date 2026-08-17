from pathlib import Path
import json
import pandas as pd
import joblib

from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_validate
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
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


BASE = Path(__file__).resolve().parent
DATA = BASE / "datasets" / "anemia" / "anemia.csv"

df = pd.read_csv(DATA)

features = [
    "Gender",
    "Hemoglobin",
    "MCH",
    "MCHC",
    "MCV"
]

df = df[features + ["Result"]].drop_duplicates().reset_index(drop=True)

X = df[features]
y = df["Result"].astype(int)

print()
print("=== DEDUPLICATED ANEMIA DATASET ===")
print("Samples:", len(df))
print("Features:", features)
print()
print("CLASS DISTRIBUTION:")
print(y.value_counts().sort_index())


X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


models = {

    "logistic_regression": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(
            max_iter=3000,
            class_weight="balanced",
            random_state=42
        ))
    ]),

    "random_forest": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", RandomForestClassifier(
            n_estimators=500,
            class_weight="balanced",
            min_samples_leaf=3,
            max_features="sqrt",
            random_state=42,
            n_jobs=-1
        ))
    ]),

    "svm": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", SVC(
            probability=True,
            class_weight="balanced",
            random_state=42
        ))
    ]),

    "hist_gradient_boosting": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", HistGradientBoostingClassifier(
            max_iter=250,
            learning_rate=0.05,
            max_leaf_nodes=12,
            random_state=42
        ))
    ])
}


cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)


results = {}

print()
print("=== 5-FOLD CROSS VALIDATION ===")

for name, model in models.items():

    scores = cross_validate(
        model,
        X_train,
        y_train,
        cv=cv,
        scoring={
            "accuracy": "accuracy",
            "balanced_accuracy": "balanced_accuracy",
            "precision": "precision",
            "recall": "recall",
            "f1": "f1",
            "roc_auc": "roc_auc",
            "average_precision": "average_precision"
        },
        n_jobs=-1
    )

    results[name] = {
        metric: round(
            float(scores[f"test_{metric}"].mean()),
            4
        )
        for metric in [
            "accuracy",
            "balanced_accuracy",
            "precision",
            "recall",
            "f1",
            "roc_auc",
            "average_precision"
        ]
    }

    print()
    print(name)
    print(json.dumps(results[name], indent=2))


# Prefer clinically useful recall/F1,
# then balanced accuracy and ROC-AUC.
def score(m):

    return (
        m["recall"] * 0.30
        + m["f1"] * 0.30
        + m["balanced_accuracy"] * 0.20
        + m["roc_auc"] * 0.20
    )


best_name = max(
    results,
    key=lambda name: (
        score(results[name]),
        results[name]["recall"],
        results[name]["f1"],
        results[name]["roc_auc"]
    )
)

best_model = models[best_name]

print()
print("SELECTED MODEL:", best_name)

best_model.fit(X_train, y_train)

prediction = best_model.predict(X_test)
probability = best_model.predict_proba(X_test)[:, 1]


test_metrics = {
    "accuracy": round(
        accuracy_score(y_test, prediction), 4
    ),

    "balanced_accuracy": round(
        balanced_accuracy_score(y_test, prediction), 4
    ),

    "precision": round(
        precision_score(
            y_test,
            prediction,
            zero_division=0
        ), 4
    ),

    "recall": round(
        recall_score(
            y_test,
            prediction,
            zero_division=0
        ), 4
    ),

    "f1": round(
        f1_score(
            y_test,
            prediction,
            zero_division=0
        ), 4
    ),

    "roc_auc": round(
        roc_auc_score(
            y_test,
            probability
        ), 4
    ),

    "average_precision": round(
        average_precision_score(
            y_test,
            probability
        ), 4
    ),

    "confusion_matrix":
        confusion_matrix(
            y_test,
            prediction
        ).tolist()
}


print()
print("=== FINAL HELD-OUT TEST ===")
print(
    json.dumps(
        test_metrics,
        indent=2
    )
)


artifact = {

    "model": best_model,

    "features": features,

    "positive_class": 1,
    "negative_class": 0,

    "class_names": {
        "0": "non_anemia",
        "1": "anemia"
    },

    "input_type": "hematology_screening",

    "dataset": "Anemia Dataset",

    "original_samples": 1421,
    "unique_samples": len(df),

    "selected_model": best_name,

    "cross_validation": results,

    "test_metrics": test_metrics,

    "warning": (
        "Screening estimate only. "
        "Not a medical diagnosis."
    )
}


model_path = BASE / "anemia.joblib"
metrics_path = BASE / "anemia_metrics.json"


joblib.dump(
    artifact,
    model_path
)


metrics_path.write_text(
    json.dumps(
        {
            "original_samples": 1421,
            "unique_samples": len(df),
            "duplicates_removed": 887,
            "selected_model": best_name,
            "cross_validation": results,
            "test_metrics": test_metrics
        },
        indent=2
    ),
    encoding="utf-8"
)


print()
print("ANEMIA MODEL: RETRAINED")
print("MODEL:", model_path)
print("METRICS:", metrics_path)
