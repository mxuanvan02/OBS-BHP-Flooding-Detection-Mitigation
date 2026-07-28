#!/usr/bin/env python3
"""Reproducible, source-only benchmark for official UCI dataset 404.

This module reads only the original ARFF configured in config.json. It does not
import or invoke the repository simulator or generated window_dataset.csv.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
from scipy.io import arff
import sklearn
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG = HERE / "config.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_config(path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def resolve_dataset_path(config: dict[str, Any], config_path: Path = DEFAULT_CONFIG) -> Path:
    path = Path(config["dataset"]["path"])
    return path if path.is_absolute() else (config_path.resolve().parent / path).resolve()


def load_arff_dataset(path: Path, expected_sha256: str | None = None):
    actual_hash = sha256_file(path)
    if expected_sha256 and actual_hash != expected_sha256:
        raise ValueError(f"ARFF SHA-256 mismatch: expected {expected_sha256}, got {actual_hash}")
    records, metadata = arff.loadarff(path)
    frame = pd.DataFrame(records)
    for name in frame.columns:
        if frame[name].dtype == object:
            frame[name] = frame[name].map(lambda value: value.decode("utf-8") if isinstance(value, bytes) else value)
    return frame, metadata, actual_hash


def schema_rows(metadata) -> list[dict[str, Any]]:
    rows = []
    for position, name in enumerate(metadata.names(), start=1):
        kind, domain = metadata[name]
        rows.append({
            "position": position,
            "name": name,
            "arff_type": kind,
            "nominal_values": "|".join(domain) if domain else "",
            "role": "target" if name == metadata.names()[-1] else "predictor",
        })
    return rows


def feature_types(frame: pd.DataFrame, target: str):
    predictors = [c for c in frame.columns if c != target]
    categorical = [c for c in predictors if not pd.api.types.is_numeric_dtype(frame[c])]
    numeric = [c for c in predictors if c not in categorical]
    return predictors, numeric, categorical


def make_preprocessor(numeric: list[str], categorical: list[str], scale: bool) -> ColumnTransformer:
    numeric_steps: list[tuple[str, Any]] = [("impute", SimpleImputer(strategy="median"))]
    if scale:
        numeric_steps.append(("scale", StandardScaler()))
    transformers: list[tuple[str, Any, list[str]]] = [
        ("numeric", Pipeline(numeric_steps), numeric)
    ]
    if categorical:
        transformers.append((
            "categorical",
            Pipeline([
                ("impute", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
            ]),
            categorical,
        ))
    return ColumnTransformer(transformers, remainder="drop", verbose_feature_names_out=False)


def build_models(config: dict[str, Any], numeric: list[str], categorical: list[str], seed: int):
    m = config["models"]
    dt_cfg = {k: v for k, v in m["DecisionTree"].items() if k != "random_state"}
    models = {
        "DecisionTree": DecisionTreeClassifier(**dt_cfg, random_state=seed),
        "SVM-RBF": SVC(**m["SVM-RBF"]),
        "KNN": KNeighborsClassifier(**m["KNN"]),
        "GaussianNB": GaussianNB(**m["GaussianNB"]),
    }
    return {
        name: Pipeline([
            ("preprocess", make_preprocessor(numeric, categorical, scale=name in {"SVM-RBF", "KNN", "GaussianNB"})),
            ("model", model),
        ])
        for name, model in models.items()
    }


def make_groups(frame: pd.DataFrame, predictors: list[str]) -> np.ndarray:
    """Group identical predictor vectors so repeated ARFF copies cannot leak."""
    return pd.util.hash_pandas_object(frame[predictors], index=False).to_numpy()


def splitter(config: dict[str, Any], y: pd.Series, groups: np.ndarray, seed: int):
    if config["evaluation"].get("splitter") != "StratifiedGroupKFold":
        raise ValueError("Only the configured duplicate-group-aware splitter is supported")
    return StratifiedGroupKFold(
        n_splits=config["evaluation"]["n_splits"], shuffle=True, random_state=seed
    ).split(np.zeros(len(y)), y, groups)


def metric_row(y_true, y_pred, zero_division: int = 0) -> dict[str, float]:
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
        "precision_macro": precision_score(y_true, y_pred, average="macro", zero_division=zero_division),
        "recall_macro": recall_score(y_true, y_pred, average="macro", zero_division=zero_division),
        "f1_macro": f1_score(y_true, y_pred, average="macro", zero_division=zero_division),
        "mcc": matthews_corrcoef(y_true, y_pred),
    }


def evaluate_models(frame: pd.DataFrame, target: str, config: dict[str, Any]) -> pd.DataFrame:
    predictors, numeric, categorical = feature_types(frame, target)
    X, y = frame[predictors], frame[target]
    groups = make_groups(frame, predictors)
    rows = []
    for seed in config["evaluation"]["seeds"]:
        for fold, (train, test) in enumerate(splitter(config, y, groups, seed), start=1):
            for name, estimator in build_models(config, numeric, categorical, seed).items():
                fitted = clone(estimator).fit(X.iloc[train], y.iloc[train])
                pred = fitted.predict(X.iloc[test])
                rows.append({"model": name, "seed": seed, "fold": fold,
                             "train_size": len(train), "test_size": len(test),
                             **metric_row(y.iloc[test], pred, config["evaluation"]["zero_division"])})
    return pd.DataFrame(rows)


def single_feature_audit(frame: pd.DataFrame, target: str, config: dict[str, Any]) -> pd.DataFrame:
    predictors, _, _ = feature_types(frame, target)
    y = frame[target]
    groups = make_groups(frame, predictors)
    rows = []
    dt_cfg = {k: v for k, v in config["models"]["DecisionTree"].items() if k != "random_state"}
    for seed in config["evaluation"]["seeds"]:
        splits = list(splitter(config, y, groups, seed))
        for feature in predictors:
            one = frame[[feature]]
            numeric = [feature] if pd.api.types.is_numeric_dtype(one[feature]) else []
            categorical = [] if numeric else [feature]
            estimator = Pipeline([
                ("preprocess", make_preprocessor(numeric, categorical, scale=False)),
                ("model", DecisionTreeClassifier(**dt_cfg, random_state=seed)),
            ])
            for fold, (train, test) in enumerate(splits, start=1):
                fitted = clone(estimator).fit(one.iloc[train], y.iloc[train])
                pred = fitted.predict(one.iloc[test])
                rows.append({"feature": feature, "seed": seed, "fold": fold,
                             "train_size": len(train), "test_size": len(test),
                             **metric_row(y.iloc[test], pred, config["evaluation"]["zero_division"])})
    return pd.DataFrame(rows)


def rf_oof_permutation(frame: pd.DataFrame, target: str, config: dict[str, Any]) -> pd.DataFrame:
    """Compute test-fold permutation importance on each unseen fold.

    permutation_importance receives the fitted full pipeline and original test
    DataFrame, so one output value corresponds to one original ARFF predictor
    (rather than to individual one-hot columns).
    """
    spec = config["random_forest_importance"]
    predictors, numeric, categorical = feature_types(frame, target)
    X, y = frame[predictors], frame[target]
    groups = make_groups(frame, predictors)
    estimator = Pipeline([
        ("preprocess", make_preprocessor(numeric, categorical, scale=False)),
        ("model", RandomForestClassifier(
            n_estimators=spec["n_estimators"], criterion=spec["criterion"],
            max_features=spec["max_features"], random_state=spec["random_state"], n_jobs=spec["n_jobs"])),
    ])
    rows = []
    for fold, (train, test) in enumerate(splitter(config, y, groups, spec["cv_seed"]), start=1):
        fitted = clone(estimator).fit(X.iloc[train], y.iloc[train])
        baseline_pred = fitted.predict(X.iloc[test])
        baseline = f1_score(y.iloc[test], baseline_pred, average="macro", zero_division=0)
        result = permutation_importance(
            fitted, X.iloc[test], y.iloc[test], scoring=spec["scoring"],
            n_repeats=spec["permutation_repeats"], random_state=spec["random_state"] + fold,
            n_jobs=spec["n_jobs"],
        )
        for index, feature in enumerate(predictors):
            rows.append({
                "feature": feature, "cv_seed": spec["cv_seed"], "fold": fold,
                "train_size": len(train), "test_size": len(test),
                "baseline_f1_macro": baseline,
                "importance_mean": result.importances_mean[index],
                "importance_std_within_fold": result.importances_std[index],
                "permutation_repeats": spec["permutation_repeats"],
            })
    return pd.DataFrame(rows)


def summarize(raw: pd.DataFrame, group: str) -> pd.DataFrame:
    metrics = ["accuracy", "balanced_accuracy", "precision_macro", "recall_macro", "f1_macro", "mcc"]
    grouped = raw.groupby(group, sort=False)[metrics].agg(["mean", "std", "min", "max"])
    grouped.columns = [f"{metric}_{stat}" for metric, stat in grouped.columns]
    output = grouped.reset_index()
    output.insert(1, "n_fold_evaluations", raw.groupby(group).size().reindex(output[group]).to_numpy())
    return output


def importance_summary(raw: pd.DataFrame) -> pd.DataFrame:
    output = raw.groupby("feature", sort=False).agg(
        importance_mean=("importance_mean", "mean"),
        importance_sd_across_folds=("importance_mean", "std"),
        importance_min=("importance_mean", "min"),
        importance_max=("importance_mean", "max"),
        baseline_f1_macro_mean=("baseline_f1_macro", "mean"),
        n_folds=("fold", "count"),
    ).reset_index()
    return output.sort_values("importance_mean", ascending=False, ignore_index=True)


def save_figures(model_summary: pd.DataFrame, audit_summary: pd.DataFrame,
                 importance: pd.DataFrame, figures: Path) -> None:
    figures.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(7.2, 4.4))
    x = np.arange(len(model_summary))
    plt.bar(x, model_summary["f1_macro_mean"], yerr=model_summary["f1_macro_std"], capsize=4, color="#4472C4")
    plt.xticks(x, model_summary["model"], rotation=20, ha="right")
    plt.ylabel("Macro F1 (mean ± SD over 25 folds)")
    plt.ylim(0, 1.05)
    plt.tight_layout()
    plt.savefig(figures / "model_macro_f1.png", dpi=180)
    plt.close()

    audit = audit_summary.sort_values("f1_macro_mean", ascending=True)
    plt.figure(figsize=(8.2, 7.0))
    plt.barh(audit["feature"], audit["f1_macro_mean"], xerr=audit["f1_macro_std"], color="#70AD47")
    plt.xlabel("Single-feature DecisionTree macro F1 (mean ± SD)")
    plt.xlim(0, 1.05)
    plt.tight_layout()
    plt.savefig(figures / "single_feature_audit.png", dpi=180)
    plt.close()

    imp = importance.sort_values("importance_mean", ascending=True)
    plt.figure(figsize=(8.2, 7.0))
    plt.barh(imp["feature"], imp["importance_mean"], xerr=imp["importance_sd_across_folds"], color="#ED7D31")
    plt.xlabel("OOF permutation importance (macro-F1 decrease)")
    plt.axvline(0, color="black", linewidth=0.7)
    plt.tight_layout()
    plt.savefig(figures / "rf_oof_permutation_importance.png", dpi=180)
    plt.close()


def output_hashes(root: Path) -> list[dict[str, Any]]:
    rows = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name != "output_manifest.json":
            rows.append({"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return rows


def run(config_path: Path = DEFAULT_CONFIG, output_dir: Path | None = None) -> Path:
    config_path = config_path.resolve()
    config = load_config(config_path)
    dataset_path = resolve_dataset_path(config, config_path)
    frame, metadata, dataset_hash = load_arff_dataset(dataset_path, config["dataset"]["expected_sha256"])
    target = config["dataset"]["target"]
    if target not in frame.columns:
        raise ValueError(f"Configured target {target!r} not present")

    output_dir = (output_dir or HERE / "outputs").resolve()
    raw_dir, summary_dir, figures_dir = output_dir / "raw", output_dir / "summary", output_dir / "figures"
    for directory in (raw_dir, summary_dir, figures_dir):
        directory.mkdir(parents=True, exist_ok=True)

    main_raw = evaluate_models(frame, target, config)
    audit_raw = single_feature_audit(frame, target, config)
    importance_raw = rf_oof_permutation(frame, target, config)
    main_summary = summarize(main_raw, "model")
    audit_summary = summarize(audit_raw, "feature").sort_values("f1_macro_mean", ascending=False, ignore_index=True)
    rf_summary = importance_summary(importance_raw)

    main_raw.to_csv(raw_dir / "fold_metrics.csv", index=False, float_format="%.10g")
    audit_raw.to_csv(raw_dir / "single_feature_fold_metrics.csv", index=False, float_format="%.10g")
    importance_raw.to_csv(raw_dir / "rf_oof_permutation_fold.csv", index=False, float_format="%.10g")
    main_summary.to_csv(summary_dir / "model_summary.csv", index=False, float_format="%.10g")
    audit_summary.to_csv(summary_dir / "single_feature_summary.csv", index=False, float_format="%.10g")
    rf_summary.to_csv(summary_dir / "rf_permutation_importance_summary.csv", index=False, float_format="%.10g")
    pd.DataFrame(schema_rows(metadata)).to_csv(output_dir / "dataset_schema.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    save_figures(main_summary, audit_summary, rf_summary, figures_dir)

    provenance = {
        "source_only_guarantee": "Reads the configured official ARFF directly; does not use results/window_dataset.csv or simulator.py.",
        "dataset": {
            **config["dataset"],
            # Keep provenance portable across clones; never serialize the
            # machine-specific absolute checkout path.
            "resolved_path": str(dataset_path.relative_to(config_path.parents[2])),
            "sha256": dataset_hash,
            "bytes": dataset_path.stat().st_size, "relation": metadata.name,
            "rows": len(frame), "attributes_total_including_target": len(frame.columns),
            "predictors": len(frame.columns) - 1, "target_class_counts": dict(Counter(frame[target])),
            "missing_cells": int(frame.isna().sum().sum()),
            "missing_by_column": {
                name: int(count) for name, count in frame.isna().sum().items() if count
            },
            "exact_duplicate_rows": int(frame.duplicated().sum()),
            "unique_rows": int(len(frame.drop_duplicates())),
            "unique_predictor_vectors": int(len(np.unique(make_groups(frame, [c for c in frame.columns if c != target])))),
        },
        "evaluation": config["evaluation"],
        "models": config["models"],
        "single_feature_audit": config["single_feature_audit"],
        "random_forest_importance": config["random_forest_importance"],
        "versions": {
            "python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__,
            "scipy": scipy.__version__, "scikit_learn": sklearn.__version__, "matplotlib": matplotlib.__version__,
            "platform": platform.platform(),
        },
        "limitations": [
            "The UCI target is a four-class policy label, not an independently observed physical attack ground truth.",
            "Node Status and Flood Status are documented by UCI as derived classifications/percentages related to the same measurements used to define Class; high performance can therefore reflect target-policy leakage or deterministic feature construction.",
            "The ARFF repeats each of 215 unique rows five times. Duplicate-group-aware folds prevent exact copies crossing train/test, but UCI supplies no higher-level experiment group identifiers, so other dependence may remain.",
            "Despite the current UCI landing page stating no missing values, the official ARFF contains 15 '?' cells in Packet_lost; training-fold median imputation is used and disclosed.",
            "No hyperparameter tuning or nested CV is performed; these are fixed transparent baselines.",
            "Permutation importance is model- and split-dependent and can be diluted among correlated or algebraically related predictors.",
        ],
        "pso_svm": {
            "status": "reported-only blocker",
            "reason": "No original PSO-SVM executable artifact or complete source configuration (swarm, bounds, iterations, objective, preprocessing, seed) is present in the official UCI404 ARFF/metadata. No PSO-SVM result was invented or rerun.",
        },
    }
    with (output_dir / "provenance.json").open("w", encoding="utf-8") as f:
        json.dump(provenance, f, ensure_ascii=False, indent=2)
        f.write("\n")
    manifest = {"algorithm": "SHA-256", "note": "Manifest excludes itself.", "files": output_hashes(output_dir)}
    with (output_dir / "output_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")
    return output_dir


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=None)
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    destination = run(args.config, args.output_dir)
    print(f"Wrote UCI404 source-only outputs to {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
