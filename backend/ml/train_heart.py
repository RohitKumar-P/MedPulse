import os
import joblib

from ucimlrepo import fetch_ucirepo

from sklearn.compose import ColumnTransformer
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
from sklearn.preprocessing import OneHotEncoder
from sklearn.calibration import CalibratedClassifierCV

from ml.model_evaluation import evaluate_model


os.makedirs(
    "ml/models",
    exist_ok=True,
)

os.makedirs(
    "ml/evaluation",
    exist_ok=True,
)


print(
    "Loading UCI Heart Disease dataset..."
)

data = fetch_ucirepo(
    id=45
)

X = data.data.features.copy()

y = (
    data.data.targets
    .iloc[:, 0]
    .astype(int)
)

y = (
    y > 0
).astype(int)


# Known categorical-coded clinical variables.
categorical_candidates = [
    "cp",
    "restecg",
    "slope",
    "ca",
    "thal",
]

categorical = [
    column
    for column in categorical_candidates
    if column in X.columns
]

numeric = [
    column
    for column in X.columns
    if column not in categorical
]


numeric_pipeline = Pipeline(
    [
        (
            "imputer",
            SimpleImputer(
                strategy="median"
            ),
        ),
    ]
)


categorical_pipeline = Pipeline(
    [
        (
            "imputer",
            SimpleImputer(
                strategy="most_frequent"
            ),
        ),

        (
            "onehot",
            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False,
            ),
        ),
    ]
)


preprocessor = ColumnTransformer(
    [
        (
            "numeric",
            numeric_pipeline,
            numeric,
        ),

        (
            "categorical",
            categorical_pipeline,
            categorical,
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
            max_depth=8,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),

    "extra_trees":
        ExtraTreesClassifier(
            n_estimators=600,
            max_depth=10,
            min_samples_leaf=2,
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


X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)


cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42,
)


scores = {}


print()
print(
    "=== HEART MODEL SELECTION ==="
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


# Calibration is performed only after
# model selection.
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
    "heart_disease",
    "ml/evaluation/heart_metrics.json",
)


joblib.dump(
    calibrated_model,
    "ml/models/heart_model.joblib",
)


joblib.dump(
    list(X.columns),
    "ml/models/heart_features.joblib",
)


joblib.dump(
    {
        "features":
            list(X.columns),

        "categorical_features":
            categorical,

        "numeric_features":
            numeric,

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
    "ml/models/heart_metadata.joblib",
)


print()
print(
    "Heart production model saved."
)
