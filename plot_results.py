"""Generate figures strictly from raw and derived CSV outputs."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SCENARIO_LABELS = {
    "S0": "Baseline", "S1": "Attack", "S2_rate_limit": "Rate limit",
    "S2_isolation": "Isolation",
}


def _save(fig, path: Path):
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def _mean_ci(values):
    x = np.asarray(values, dtype=float)
    mean = float(x.mean())
    half = 0.0 if len(x) < 2 else 1.96 * float(x.std(ddof=1)) / np.sqrt(len(x))
    return mean, half


def make_plots(raw_dir: str | Path, tables_dir: str | Path, figures_dir: str | Path):
    raw, tables, figures = Path(raw_dir), Path(tables_dir), Path(figures_dir)
    figures.mkdir(parents=True, exist_ok=True)
    runs = pd.read_csv(raw / "runs.csv")
    sweep = pd.read_csv(raw / "sweep.csv")
    ml = pd.read_csv(tables / "ml_results.csv")

    # Paired seed view of baseline versus undefended attack.
    paired = runs[runs["scenario"].isin(["S0", "S1"])].pivot(
        index="seed", columns="scenario", values="legal_packets").sort_index()
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    x = np.arange(len(paired))
    for scenario, marker in (("S0", "o"), ("S1", "s")):
        if scenario in paired:
            ax.plot(x, paired[scenario], marker=marker, linewidth=1.8,
                    label=SCENARIO_LABELS[scenario])
    ax.set(xticks=x, xticklabels=paired.index.astype(str), xlabel="Seed",
           ylabel="Legal packets", title="Legal throughput by seed")
    ax.grid(axis="y", alpha=.25); ax.legend()
    _save(fig, figures / "throughput_by_seed.png")

    # Attack-rate response from sweep samples; preserve raw points and means.
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 7.2), sharex=True)
    sweep_metrics = (("legal_packets", "Legal packets"),
                     ("bursts_sent", "Backbone bursts sent"))
    for ax, (metric, ylabel) in zip(axes, sweep_metrics):
        for seed, part in sweep.groupby("seed"):
            ax.plot(part["attack_rate_mbps"], part[metric], color="0.65", alpha=.65,
                    linewidth=1, marker=".")
        means = sweep.groupby("attack_rate_mbps", as_index=False)[metric].mean()
        ax.plot(means["attack_rate_mbps"], means[metric], color="#1565c0",
                marker="o", linewidth=2.2, label="Mean")
        ax.set_ylabel(ylabel); ax.grid(alpha=.25); ax.legend()
    axes[-1].set_xlabel("Attack rate (Mb/s)")
    axes[0].set_title("Impact of attack-rate sweep")
    _save(fig, figures / "impact_sweep.png")

    # Per-run mitigation comparison, with normal-approximation 95% CI.
    order = [s for s in ("S0", "S1", "S2_rate_limit", "S2_isolation")
             if s in set(runs["scenario"])]
    stats = [_mean_ci(runs.loc[runs["scenario"] == s, "legal_packets"]) for s in order]
    means, errors = zip(*stats)
    fig, ax = plt.subplots(figsize=(7.4, 4.5))
    ax.bar(range(len(order)), means, yerr=errors, capsize=5,
           color=["#4c78a8", "#e45756", "#f2cf5b", "#54a24b"][:len(order)])
    ax.set(xticks=range(len(order)), xticklabels=[SCENARIO_LABELS.get(s, s) for s in order],
           ylabel="Mean legal packets", title="Mitigation throughput (95% CI)")
    ax.grid(axis="y", alpha=.25)
    _save(fig, figures / "mitigation_ci.png")

    # Fold-level grouped-CV MCC; mean and fold spread are both visible.
    model_order = [m for m in ("SVM-RBF", "KNN", "DecisionTree", "GaussianNB")
                   if m in set(ml["model"])]
    grouped = ml.groupby("model")["mcc"]
    mcc_means = [grouped.get_group(m).mean() for m in model_order]
    mcc_sd = [grouped.get_group(m).std(ddof=1) if len(grouped.get_group(m)) > 1 else 0
              for m in model_order]
    fig, ax = plt.subplots(figsize=(7.4, 4.5))
    ax.bar(range(len(model_order)), mcc_means, yerr=mcc_sd, capsize=5, color="#6f4e9c")
    for i, model in enumerate(model_order):
        vals = grouped.get_group(model).to_numpy()
        ax.scatter(np.full(len(vals), i), vals, color="black", s=18, alpha=.65, zorder=3)
    ax.axhline(0, color="black", linewidth=.8)
    ax.set(xticks=range(len(model_order)), xticklabels=model_order, ylabel="MCC",
           title="Seed-grouped cross-validation MCC")
    ax.grid(axis="y", alpha=.25)
    _save(fig, figures / "ml_mcc.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="results/raw")
    ap.add_argument("--tables", default="results/tables")
    ap.add_argument("--figures", default="results/figures")
    args = ap.parse_args()
    make_plots(args.raw, args.tables, args.figures)


if __name__ == "__main__":
    main()
