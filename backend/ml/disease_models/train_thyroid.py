from pathlib import Path
import json
import urllib.request

import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    f1_score
)


BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "datasets"

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

data_path = DATA_DIR / "new-thyroid.data"

# Direct UCI file.
URLS = [
    "https://archive.ics.uci.edu/ml/machine-learning-databases/thyroid-disease/new-thyroid.data",
    "https://archive.ics.uci.edu/static/public/102/new-thyroid.data",
]

if not data_path.exists():

    downloaded = False

    for url in URLS:
        try:
            print(
                f"Downloading thyroid dataset: {url}"
            )

            urllib.request.urlretrieve(
                url,
                data_path
            )

            downloaded = True
            break

        except Exception as e:
            print(
                f"Download failed: {e}"
            )

    if not downloaded:
        raise SystemExit(
            "Unable to download new-thyroid.data"
        )


# The dataset contains:
#
# class
# RT3U
# T4
# T3
# TSH
# DTSH
#
# UCI documents this as the Stefan Aeberhard
# thyroid dataset: 3 classes, 215 instances,
# 5 attributes. The first column is the class.
#
# 1 = normal
# 2 = hyperthyroid
# 3 = hypothyroid

columns = [
    "class",
    "T3_resin_uptake",
    "total_serum_thyroxin",
    "total_serum_triiodothyronine",
    "basal_TSH",
    "max_TSH_after_TRH"
]


df = pd.read_csv(
    data_path,
    sep=",",
    header=None,
    names=columns
)


print("RAW THYROID SHAPE:")
print(df.shape)

print("RAW THYROID HEAD:")
print(df.head())


# Force numeric values.
for column in columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


df = df.dropna()


X = df[
    [
        "T3_resin_uptake",
        "total_serum_thyroxin",
        "total_serum_triiodothyronine",
        "basal_TSH",
        "max_TSH_after_TRH"
    ]
]

y = df["class"].astype(int)


print("THYROID CLASSES:")
print(
    sorted(
        y.unique().tolist()
    )
)

print("CLASS COUNTS:")
print(
    y.value_counts().sort_index()
)


X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    class_weight="balanced"
)


model.fit(
    X_train,
    y_train
)


pred = model.predict(
    X_test
)


metrics = {
    "model": "thyroid",
    "dataset": "UCI New Thyroid",
    "samples": len(df),
    "features": len(X.columns),

    "accuracy": round(
        accuracy_score(
            y_test,
            pred
        ),
        4
    ),

    "f1_macro": round(
        f1_score(
            y_test,
            pred,
            average="macro"
        ),
        4
    )
}


artifact = {
    "model": model,

    "features": list(
        X.columns
    ),

    "normal_class": 1,

    "class_names": {
        "1": "normal",
        "2": "hyperthyroid",
        "3": "hypothyroid"
    },

    "input_type": "thyroid_blood_measurements",

    "dataset": "UCI New Thyroid"
}


joblib.dump(
    artifact,
    BASE / "thyroid.joblib"
)


(
    BASE / "thyroid_metrics.json"
).write_text(
    json.dumps(
        metrics,
        indent=2
    ),
    encoding="utf-8"
)


print()
print(
    json.dumps(
        metrics,
        indent=2
    )
)

print(
    "THYROID MODEL: CREATED"
)

print(
    f"MODEL FILE: {BASE / 'thyroid.joblib'}"
)
