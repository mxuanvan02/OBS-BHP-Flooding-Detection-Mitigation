#!/usr/bin/env python3
"""Plot the validated nOBS S1 rate sweep from trace-derived summary CSV."""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("summary", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    frame = pd.read_csv(args.summary)
    required = {"attack_rate_mbps", "metric", "n", "mean", "ci95_low", "ci95_high"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")
    if frame.empty or frame[list(required)].isnull().any().any():
        raise ValueError("summary contains missing values")
    numeric = ("attack_rate_mbps", "n", "mean", "ci95_low", "ci95_high")
    if not all(frame[column].map(lambda value: math.isfinite(float(value))).all() for column in numeric):
        raise ValueError("summary contains non-finite values")
    seed_counts = set(frame["n"])
    if len(seed_counts) != 1 or next(iter(seed_counts)) < 2:
        raise ValueError("expected one seed count of at least two for every rate/metric")
    if not ((frame["ci95_low"] <= frame["mean"]) & (frame["mean"] <= frame["ci95_high"])).all():
        raise ValueError("confidence intervals must contain their means")

    panels = [
        ("legal_packets", "Legitimate packets received", "#1565c0"),
        ("bursts_offered", "Optical bursts offered", "#ef6c00"),
        ("burst_loss_rate", "Explicit burst-drop ratio", "#c62828"),
    ]
    expected_rates = None
    fig, axes = plt.subplots(3, 1, figsize=(8.0, 9.0), sharex=True)
    for ax, (metric, ylabel, color) in zip(axes, panels):
        part = frame.loc[frame["metric"] == metric].sort_values("attack_rate_mbps")
        rates = tuple(part["attack_rate_mbps"])
        if len(rates) != len(set(rates)):
            raise ValueError(f"duplicate rates for {metric}")
        if expected_rates is None:
            expected_rates = rates
        elif rates != expected_rates:
            raise ValueError(f"inconsistent rate set for {metric}")
        yerr = [part["mean"] - part["ci95_low"], part["ci95_high"] - part["mean"]]
        ax.errorbar(part["attack_rate_mbps"], part["mean"], yerr=yerr,
                    marker="o", linewidth=2, capsize=3, color=color)
        ax.set_ylabel(ylabel)
        ax.grid(alpha=0.25)
    n = int(next(iter(seed_counts)))
    axes[0].set_title(f"S1 attack-rate response (descriptive mean and 95% t-interval, n={n} fixed seeds)")
    axes[-1].set_xlabel("Nominal attack rate per source (Mb/s)")
    axes[-1].set_xticks(sorted(frame["attack_rate_mbps"].unique()))
    fig.tight_layout()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(args.out)


if __name__ == "__main__":
    main()
