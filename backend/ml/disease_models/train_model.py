from pathlib import Path
import json
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


BASE = Path(__file__).resolve().parent


def train_model(csv_path, target_column, model_name):

    csv_path = Path(csv_path)
    df = pd.read_csv(csv_path)

    if target_column not in df.columns:
        raise ValueError(
            f"Target column '{target_column}' not found. "
            f"Available columns: {list(df.columns)}"
        )

    df = df.dropna(subset=[target_column])

    X = df.drop(columns=[target_column])
    y = df[target_column]

    X = pd.get_dummies(X, drop_first=False)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("classifier", LogisticRegression(
            max_iter=2000,
            random_state=42
        ))
    ])

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    metrics = {
        "model": model_name,
        "samples": len(df),
        "features": len(X.columns),
        "accuracy": round(
            accuracy_score(y_test, predictions), 4
        ),
        "precision": round(
            precision_score(
                y_test,
                predictions,
                average="weighted",
                zero_division=0
            ),
            4
        ),
        "recall": round(
            recall_score(
                y_test,
                predictions,
                average="weighted",
                zero_division=0
            ),
            4
        ),
        "f1": round(
            f1_score(
                y_test,
                predictions,
                average="weighted",
                zero_division=0
            ),
            4
        )
    }

    output = BASE / f"{model_name}.joblib"
    metrics_output = BASE / f"{model_name}_metrics.json"

    joblib.dump(
        {
            "model": model,
            "features": list(X.columns)
        },
        output
    )

    metrics_output.write_text(
        json.dumps(metrics, indent=2),
        encoding="utf-8"
    )

    print(json.dumps(metrics, indent=2))
    print(f"MODEL: {output}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        print(
            "Usage: python train_model.py "
            "<csv> <target_column> <model_name>"
        )
        raise SystemExit(1)

    train_model(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3]
    )
