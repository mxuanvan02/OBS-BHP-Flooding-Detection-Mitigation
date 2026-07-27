"""Leakage-aware grouped ML evaluation for the network-window benchmark."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (accuracy_score, balanced_accuracy_score, f1_score,
                             matthews_corrcoef, precision_score, recall_score)
from sklearn.model_selection import GroupKFold
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

LEAKAGE_COLUMNS = {"attacker_mbps", "active_sources", "scenario"}
ID_COLUMNS = {"seed", "window_start", "window_end"}
TARGET = "attack_label"
METRICS = ("accuracy", "balanced_accuracy", "precision", "recall", "f1", "mcc")


def _models(random_state: int):
    return {
        "SVM-RBF": make_pipeline(StandardScaler(), SVC(kernel="rbf", C=1.0, gamma="scale")),
        "KNN": make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=5)),
        "DecisionTree": DecisionTreeClassifier(random_state=random_state, max_depth=None),
        "GaussianNB": GaussianNB(),
    }


def _score(y_true, y_pred):
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "mcc": matthews_corrcoef(y_true, y_pred),
    }


def _folds(df: pd.DataFrame):
    groups = df["seed"]
    n_splits = min(5, groups.nunique())
    if n_splits < 2:
        raise ValueError("window dataset needs at least two distinct seed groups")
    return GroupKFold(n_splits=n_splits).split(df, df[TARGET], groups)


def run_ml_pipeline(dataset_path: str | Path, tables_dir: str | Path, random_state: int = 1729):
    """Evaluate classifiers with seed-held-out GroupKFold; return output frames."""
    df = pd.read_csv(dataset_path)
    required = {TARGET, "seed"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"missing required columns: {sorted(missing)}")
    candidates = [c for c in df.columns if c not in LEAKAGE_COLUMNS | ID_COLUMNS | {TARGET}]
    features = [c for c in candidates if pd.api.types.is_numeric_dtype(df[c])]
    if not features:
        raise ValueError("no numeric non-leakage features available")
    clean = df.dropna(subset=features + [TARGET, "seed"]).reset_index(drop=True)
    X, y = clean[features], clean[TARGET].astype(int)
    rows = []
    for name, model in _models(random_state).items():
        for fold, (train, test) in enumerate(_folds(clean), 1):
            model.fit(X.iloc[train], y.iloc[train])
            scores = _score(y.iloc[test], model.predict(X.iloc[test]))
            rows.append({"model": name, "fold": fold, "n_train": len(train), "n_test": len(test),
                         "features": ";".join(features), **scores})
    results = pd.DataFrame(rows)
    # Audit every numeric candidate, including intentionally excluded direct leaks,
    # so the report makes the leakage decision observable rather than hiding it.
    audit_features = [c for c in df.columns if c not in ID_COLUMNS | {TARGET}
                      and pd.api.types.is_numeric_dtype(df[c])]
    audit_rows = []
    for feature in audit_features:
        for fold, (train, test) in enumerate(_folds(clean), 1):
            model = DecisionTreeClassifier(random_state=random_state, max_depth=None)
            model.fit(clean[[feature]].iloc[train], y.iloc[train])
            scores = _score(y.iloc[test], model.predict(clean[[feature]].iloc[test]))
            audit_rows.append({"feature": feature, "excluded_for_model": feature in LEAKAGE_COLUMNS,
                               "fold": fold, "n_train": len(train), "n_test": len(test), **scores})
    audit = pd.DataFrame(audit_rows)
    out = Path(tables_dir); out.mkdir(parents=True, exist_ok=True)
    results.to_csv(out / "ml_results.csv", index=False)
    audit.to_csv(out / "single_feature_audit.csv", index=False)
    return results, audit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset", nargs="?", default="results/raw/window_dataset.csv")
    ap.add_argument("--tables", default="results/tables")
    ap.add_argument("--random-state", type=int, default=1729)
    args = ap.parse_args()
    run_ml_pipeline(args.dataset, args.tables, args.random_state)


if __name__ == "__main__":
    main()
