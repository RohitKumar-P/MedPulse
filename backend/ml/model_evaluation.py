import json
import os
from pathlib import Path

import joblib
import numpy as np

from sklearn.base import clone
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    classification_report,
)
from sklearn.model_selection import (
    StratifiedKFold,
    cross_val_predict,
)


def evaluate_model(
    model,
    X_train,
    y_train,
    X_test,
    y_test,
    name,
    output_path,
):

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42,
    )

    cv_prob = cross_val_predict(
        model,
        X_train,
        y_train,
        cv=cv,
        method="predict_proba",
        n_jobs=-1,
    )[:, 1]

    cv_pred = (
        cv_prob >= 0.5
    ).astype(int)

    model.fit(
        X_train,
        y_train,
    )

    test_prob = model.predict_proba(
        X_test
    )[:, 1]

    test_pred = (
        test_prob >= 0.5
    ).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_test,
        test_pred,
        labels=[0, 1],
    ).ravel()

    specificity = (
        tn / (tn + fp)
        if tn + fp
        else 0.0
    )

    sensitivity = (
        tp / (tp + fn)
        if tp + fn
        else 0.0
    )

    metrics = {

        "model":
            name,

        "dataset": {
            "train_samples":
                int(len(y_train)),
            "test_samples":
                int(len(y_test)),
            "positive_train":
                int(y_train.sum()),
            "positive_test":
                int(y_test.sum()),
        },

        "cross_validation": {

            "folds": 5,

            "roc_auc":
                float(
                    roc_auc_score(
                        y_train,
                        cv_prob,
                    )
                ),

            "pr_auc":
                float(
                    average_precision_score(
                        y_train,
                        cv_prob,
                    )
                ),

            "sensitivity":
                float(
                    recall_score(
                        y_train,
                        cv_pred,
                        zero_division=0,
                    )
                ),

            "specificity":
                float(
                    (
                        (cv_pred == 0)
                        & (y_train == 0)
                    ).sum()
                    / max(
                        1,
                        (y_train == 0).sum(),
                    )
                ),

            "precision":
                float(
                    precision_score(
                        y_train,
                        cv_pred,
                        zero_division=0,
                    )
                ),

            "f1":
                float(
                    f1_score(
                        y_train,
                        cv_pred,
                        zero_division=0,
                    )
                ),

        },

        "held_out_test": {

            "accuracy":
                float(
                    accuracy_score(
                        y_test,
                        test_pred,
                    )
                ),

            "balanced_accuracy":
                float(
                    balanced_accuracy_score(
                        y_test,
                        test_pred,
                    )
                ),

            "roc_auc":
                float(
                    roc_auc_score(
                        y_test,
                        test_prob,
                    )
                ),

            "pr_auc":
                float(
                    average_precision_score(
                        y_test,
                        test_prob,
                    )
                ),

            "sensitivity":
                float(
                    sensitivity
                ),

            "specificity":
                float(
                    specificity
                ),

            "precision":
                float(
                    precision_score(
                        y_test,
                        test_pred,
                        zero_division=0,
                    )
                ),

            "f1":
                float(
                    f1_score(
                        y_test,
                        test_pred,
                        zero_division=0,
                    )
                ),

            "brier_score":
                float(
                    brier_score_loss(
                        y_test,
                        test_prob,
                    )
                ),

            "confusion_matrix": {
                "tn": int(tn),
                "fp": int(fp),
                "fn": int(fn),
                "tp": int(tp),
            },

            "classification_report":
                classification_report(
                    y_test,
                    test_pred,
                    output_dict=True,
                    zero_division=0,
                ),
        },
    }

    os.makedirs(
        Path(output_path).parent,
        exist_ok=True,
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            metrics,
            f,
            indent=2,
        )

    print()
    print(
        f"=== {name.upper()} ==="
    )

    print(
        "Test ROC-AUC:",
        round(
            metrics[
                "held_out_test"
            ]["roc_auc"],
            4,
        ),
    )

    print(
        "Test PR-AUC:",
        round(
            metrics[
                "held_out_test"
            ]["pr_auc"],
            4,
        ),
    )

    print(
        "Sensitivity:",
        round(
            sensitivity,
            4,
        ),
    )

    print(
        "Specificity:",
        round(
            specificity,
            4,
        ),
    )

    print(
        "Precision:",
        round(
            metrics[
                "held_out_test"
            ]["precision"],
            4,
        ),
    )

    print(
        "F1:",
        round(
            metrics[
                "held_out_test"
            ]["f1"],
            4,
        ),
    )

    print(
        "Brier:",
        round(
            metrics[
                "held_out_test"
            ]["brier_score"],
            4,
        ),
    )

    print()
    print(
        "Confusion matrix:",
        metrics[
            "held_out_test"
        ]["confusion_matrix"],
    )

    return metrics
