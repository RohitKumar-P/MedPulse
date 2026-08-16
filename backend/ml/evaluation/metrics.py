import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import (
    StratifiedKFold,
    cross_validate
)

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)


def evaluate_binary_model(
    model,
    X,
    y,
    name
):

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42
    )

    scores = cross_validate(
        model,
        X,
        y,
        cv=cv,
        scoring=[
            "accuracy",
            "balanced_accuracy",
            "precision",
            "recall",
            "f1",
            "roc_auc"
        ],
        return_train_score=False
    )

    metrics = {

        "model":
            name,

        "accuracy_mean":
            float(
                scores[
                    "test_accuracy"
                ].mean()
            ),

        "balanced_accuracy_mean":
            float(
                scores[
                    "test_balanced_accuracy"
                ].mean()
            ),

        "precision_mean":
            float(
                scores[
                    "test_precision"
                ].mean()
            ),

        "recall_mean":
            float(
                scores[
                    "test_recall"
                ].mean()
            ),

        "f1_mean":
            float(
                scores[
                    "test_f1"
                ].mean()
            ),

        "roc_auc_mean":
            float(
                scores[
                    "test_roc_auc"
                ].mean()
            )
    }

    return metrics


def save_metrics(
    metrics,
    filename
):

    path = Path(
        "ml/evaluation"
    )

    path.mkdir(
        parents=True,
        exist_ok=True
    )

    (
        path / filename
    ).write_text(
        json.dumps(
            metrics,
            indent=2
        ),
        encoding="utf-8"
    )
