import os
import urllib.request
import joblib
import pandas as pd
import numpy as np

from sklearn.ensemble import (
    ExtraTreesClassifier,
    RandomForestClassifier,
    HistGradientBoostingClassifier,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_val_score,
)
from sklearn.pipeline import Pipeline
from sklearn.calibration import CalibratedClassifierCV

from ml.model_evaluation import evaluate_model


os.makedirs(
    "ml/models",
    exist_ok=True,
)

os.makedirs(
    "ml/datasets",
    exist_ok=True,
)

os.makedirs(
    "ml/evaluation",
    exist_ok=True,
)


url = (
    "https://raw.githubusercontent.com/"
    "jbrownlee/Datasets/master/"
    "pima-indians-diabetes.data.csv"
)

path = (
    "ml/datasets/diabetes.csv"
)


if not os.path.exists(path):

    print(
        "Downloading diabetes dataset..."
    )

    urllib.request.urlretrieve(
        url,
        path,
    )


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


print()
print(
    "=== DIABETES DATA AUDIT ==="
)

print(
    "Samples:",
    len(df),
)

print(
    "Features:",
    len(columns) - 1,
)

print(
    "Positive cases:",
    int(df.outcome.sum()),
)

print(
    "Negative cases:",
    int(
        (df.outcome == 0).sum()
    ),
)


X = df.drop(
    "outcome",
    axis=1,
)

y = df["outcome"].astype(int)


# In this dataset, zero is biologically
# implausible for these measurements and
# represents missingness.
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


preprocessor = Pipeline(
    [
        (
            "imputer",
            SimpleImputer(
                strategy="median"
            ),
        ),
    ]
)


candidates = {

    "logistic_regression":
        LogisticRegression(
            max_iter=3000,
            class_weight="balanced",
            C=0.5,
        ),

    "random_forest":
        RandomForestClassifier(
            n_estimators=600,
            max_depth=7,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),

    "extra_trees":
        ExtraTreesClassifier(
            n_estimators=600,
            max_depth=8,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),

    "hist_gradient_boosting":
        HistGradientBoostingClassifier(
            max_iter=300,
            learning_rate=0.04,
            max_leaf_nodes=15,
            l2_regularization=1.0,
            random_state=42,
        ),
}


cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42,
)


scores = {}


print()
print(
    "=== DIABETES MODEL SELECTION ==="
)


for name, classifier in candidates.items():

    pipeline = Pipeline(
        [
            (
                "preprocessor",
                preprocessor,
            ),
            (
                "classifier",
                classifier,
            ),
        ]
    )

    score = cross_val_score(
        pipeline,
        X_train,
        y_train,
        cv=cv,
        scoring="roc_auc",
        n_jobs=-1,
    )

    scores[name] = score.mean()

    print(
        f"{name}: "
        f"ROC-AUC="
        f"{score.mean():.4f} "
        f"+/- "
        f"{score.std():.4f}"
    )


best_name = max(
    scores,
    key=scores.get,
)


print()
print(
    "Selected:",
    best_name,
)


best_pipeline = Pipeline(
    [
        (
            "preprocessor",
            preprocessor,
        ),
        (
            "classifier",
            candidates[best_name],
        ),
    ]
)


calibrated_model = CalibratedClassifierCV(
    estimator=best_pipeline,
    method="sigmoid",
    cv=5,
)


metrics = evaluate_model(
    calibrated_model,
    X_train,
    y_train,
    X_test,
    y_test,
    "diabetes",
    "ml/evaluation/diabetes_metrics.json",
)


joblib.dump(
    calibrated_model,
    "ml/models/diabetes_model.joblib",
)


joblib.dump(
    list(X.columns),
    "ml/models/diabetes_features.joblib",
)


joblib.dump(
    {
        "features":
            list(X.columns),

        "missing_as_zero":
            zero_missing,

        "selected_model":
            best_name,

        "cv_scores":
            {
                k: float(v)
                for k, v in scores.items()
            },

        "metrics":
            metrics,
    },
    "ml/models/diabetes_metadata.joblib",
)


print()
print(
    "Diabetes production model saved."
)

