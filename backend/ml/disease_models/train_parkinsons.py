from pathlib import Path
import json
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import GroupShuffleSplit


BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "datasets"

url = "https://archive.ics.uci.edu/static/public/174/data.csv"
data_path = DATA_DIR / "parkinsons.csv"

if not data_path.exists():
    df = pd.read_csv(url)
    df.to_csv(data_path, index=False)
else:
    df = pd.read_csv(data_path)

df = df.dropna()

# UCI Parkinson's uses status:
# 0 = healthy
# 1 = Parkinson's disease
#
# The "name" field contains the subject/recording identifier.
# Split by subject to avoid having recordings from the same
# person in both train and test sets.

groups = (
    df["name"]
    .astype(str)
    .str.extract(r"(S\d+)", expand=False)
)

feature_columns = [
    c for c in df.columns
    if c not in ["name", "status"]
]

X = df[feature_columns]
y = df["status"]

splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.2,
    random_state=42
)

train_idx, test_idx = next(
    splitter.split(
        X,
        y,
        groups=groups
    )
)

X_train = X.iloc[train_idx]
X_test = X.iloc[test_idx]

y_train = y.iloc[train_idx]
y_test = y.iloc[test_idx]

model = RandomForestClassifier(
    n_estimators=400,
    random_state=42,
    class_weight="balanced"
)

model.fit(
    X_train,
    y_train
)

pred = model.predict(X_test)

metrics = {
    "model": "parkinsons",
    "dataset": "UCI Parkinsons",
    "samples": len(df),
    "features": len(feature_columns),
    "subjects": int(groups.nunique()),
    "accuracy": round(
        accuracy_score(y_test, pred),
        4
    ),
    "precision": round(
        precision_score(
            y_test,
            pred,
            zero_division=0
        ),
        4
    ),
    "recall": round(
        recall_score(
            y_test,
            pred,
            zero_division=0
        ),
        4
    ),
    "f1": round(
        f1_score(
            y_test,
            pred,
            zero_division=0
        ),
        4
    )
}

artifact = {
    "model": model,
    "features": feature_columns,
    "positive_class": 1,
    "negative_class": 0,
    "input_type": "voice_biomarkers"
}

joblib.dump(
    artifact,
    BASE / "parkinsons.joblib"
)

(
    BASE / "parkinsons_metrics.json"
).write_text(
    json.dumps(
        metrics,
        indent=2
    ),
    encoding="utf-8"
)

print(json.dumps(metrics, indent=2))
print("PARKINSONS MODEL: CREATED")
