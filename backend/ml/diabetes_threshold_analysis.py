import json
import joblib
import numpy as np
import pandas as pd

from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
)

from sklearn.model_selection import train_test_split


path = "ml/datasets/diabetes.csv"

columns = [
    "pregnancies",
    "glucose",
    "blood_pressure",
    "skin_thickness",
    "insulin",
    "bmi",
    "diabetes_pedigree",
    "age",
    "outcome",
]

df = pd.read_csv(
    path,
    names=columns,
)

X = df.drop("outcome", axis=1)
y = df["outcome"].astype(int)

zero_missing = [
    "glucose",
    "blood_pressure",
    "skin_thickness",
    "insulin",
    "bmi",
]

X[zero_missing] = (
    X[zero_missing]
    .replace(0, np.nan)
)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

model = joblib.load(
    "ml/models/diabetes_model.joblib"
)

prob = model.predict_proba(X_test)[:, 1]

print()
print("=== DIABETES THRESHOLD ANALYSIS ===")
print()

rows = []

for threshold in np.arange(
    0.10,
    0.71,
    0.05,
):

    pred = (
        prob >= threshold
    ).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_test,
        pred,
        labels=[0, 1],
    ).ravel()

    sensitivity = (
        tp / (tp + fn)
        if tp + fn
        else 0
    )

    specificity = (
        tn / (tn + fp)
        if tn + fp
        else 0
    )

    precision = precision_score(
        y_test,
        pred,
        zero_division=0,
    )

    f1 = f1_score(
        y_test,
        pred,
        zero_division=0,
    )

    rows.append(
        {
            "threshold": round(
                float(threshold),
                2,
            ),
            "sensitivity": round(
                sensitivity,
                4,
            ),
            "specificity": round(
                specificity,
                4,
            ),
            "precision": round(
                precision,
                4,
            ),
            "f1": round(
                f1,
                4,
            ),
            "tp": int(tp),
            "fp": int(fp),
            "fn": int(fn),
            "tn": int(tn),
        }
    )

for row in rows:

    print(
        f"threshold={row['threshold']:.2f} "
        f"sensitivity={row['sensitivity']:.2%} "
        f"specificity={row['specificity']:.2%} "
        f"precision={row['precision']:.2%} "
        f"F1={row['f1']:.2%} "
        f"FN={row['fn']} "
        f"FP={row['fp']}"
    )

print()
print(
    "=== SCREENING CANDIDATES ==="
)

for row in rows:

    if row["sensitivity"] >= 0.90:

        print(
            row
        )
