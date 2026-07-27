#!/usr/bin/env python3
"""Validate and summarize a completed paired nOBS matrix, fail closed."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from collections import defaultdict
from pathlib import Path

from parse_trace import parse_path

try:
    from scipy.stats import t as student_t
except ImportError:  # pragma: no cover
    student_t = None

EXPECTED = ("S0", "S1", "S2_rate_limit", "S2_isolation")
RUN_CONFIG = re.compile(
    r"attack_multiplier=(?P<multiplier>[-+0-9.eE]+) "
    r"effective_attack_rate_mbps_per_source=(?P<effective>[-+0-9.eE]+)"
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty table: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def ci95(values: list[float]) -> tuple[float, float, float]:
    n = len(values)
    mean = sum(values) / n
    if n < 2:
        return mean, math.nan, math.nan
    sd = math.sqrt(sum((x - mean) ** 2 for x in values) / (n - 1))
    critical = float(student_t.ppf(0.975, n - 1)) if student_t else 1.96
    half = critical * sd / math.sqrt(n)
    return mean, mean - half, mean + half


def validate(root: Path) -> list[dict]:
    completion = json.loads((root / "completion.json").read_text(encoding="utf-8"))
    required_completion = {
        "complete": True,
        "attempted_cells": 32,
        "successful_cells": 32,
        "failed_cells": 0,
        "failures": [],
    }
    if any(completion.get(key) != value for key, value in required_completion.items()):
        raise ValueError(f"matrix is not complete: {completion}")
    manifest = json.loads((root / "matrix_manifest.json").read_text(encoding="utf-8"))
    snapshot = root / "experiment_config.snapshot.json"
    if not snapshot.is_file() or sha256(snapshot) != manifest.get("experiment_config_sha256"):
        raise ValueError("experiment config snapshot hash mismatch")
    config = json.loads(snapshot.read_text(encoding="utf-8"))
    seeds = [int(x) for x in config["seeds"]]
    labels = tuple(item["label"] for item in config["scenarios"])
    if tuple(labels) != EXPECTED or len(seeds) * len(labels) != completion["attempted_cells"]:
        raise ValueError(f"unexpected experiment design: seeds={seeds} labels={labels}")
    expected_paths = {(seed, label) for seed in seeds for label in EXPECTED}
    actual_paths = {
        (int(path.parts[-3].split("_", 1)[1]), path.parent.name)
        for path in root.glob("seed_*/*/run.json")
    }
    if actual_paths != expected_paths:
        raise ValueError(f"cell mismatch: missing={sorted(expected_paths-actual_paths)} extra={sorted(actual_paths-expected_paths)}")

    rows: list[dict] = []
    multipliers: dict[int, set[float]] = defaultdict(set)
    for seed, label in sorted(expected_paths):
        cell = root / f"seed_{seed}" / label
        run = json.loads((cell / "run.json").read_text(encoding="utf-8"))
        if run.get("exit_code") != 0:
            raise ValueError(f"failed cell {seed}/{label}: {run}")
        trace, metrics_path = cell / "out.tr", cell / "metrics.json"
        for path in (trace, metrics_path, cell / "stdout.log", cell / "stderr.log", cell / "command.txt"):
            if not path.is_file():
                raise ValueError(f"missing artifact: {path}")
        if sha256(trace) != run.get("trace_sha256") or sha256(metrics_path) != run.get("metrics_sha256"):
            raise ValueError(f"hash mismatch: {seed}/{label}")
        stored_metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        reparsed_metrics = parse_path(trace)
        if reparsed_metrics != stored_metrics:
            raise ValueError(f"reparsed metrics mismatch: {seed}/{label}")
        metrics = reparsed_metrics
        if metrics.get("schema") != "ns2-old-12-field":
            raise ValueError(f"unknown metrics schema: {seed}/{label}")
        stdout = (cell / "stdout.log").read_text(encoding="utf-8")
        match = RUN_CONFIG.search(stdout)
        if not match:
            raise ValueError(f"missing RUN_CONFIG: {seed}/{label}")
        multiplier, effective = float(match["multiplier"]), float(match["effective"])
        multipliers[seed].add(multiplier)
        tcp, optical, trace_meta = metrics["transport"]["tcp"], metrics["optical"], metrics["trace"]
        attempted = int(optical["control_link_reservations_attempted"])
        succeeded = int(optical["control_link_reservations_succeeded"])
        failed = int(optical["control_link_reservations_failed"])
        if attempted != succeeded + failed:
            raise ValueError(f"reservation accounting mismatch: {seed}/{label}")
        rows.append({
            "seed": seed, "scenario": label,
            "nominal_attack_mbps_per_source": run["attack_rate_mbps_per_source"],
            "attack_multiplier": multiplier, "effective_attack_mbps_per_source": effective,
            "legal_packets": tcp["legal_receive_packets"], "legal_bytes": tcp["legal_receive_bytes"],
            "bursts_offered": optical["data_bursts_offered"],
            "bursts_sent": optical["data_bursts_sent_end_to_end"],
            "bursts_explicitly_dropped": optical["data_bursts_explicitly_dropped"],
            "burst_drop_ratio": optical["data_burst_drop_ratio"],
            "control_reservations_attempted": attempted,
            "control_reservations_succeeded": succeeded,
            "control_reservations_failed": failed,
            "control_unresolved_at_trace_end": optical["control_packets_unresolved_at_trace_end"],
            "trace_last_time_s": trace_meta["last_time_s"],
            "trace_bytes": run["trace_bytes"], "trace_sha256": run["trace_sha256"],
            "metrics_sha256": run["metrics_sha256"], "exit_code": 0,
        })
    bad = {seed: values for seed, values in multipliers.items() if len(values) != 1}
    if bad:
        raise ValueError(f"paired cells do not share multiplier: {bad}")
    return rows


def summarize(rows: list[dict], out: Path) -> None:
    write_csv(out / "runs.csv", rows)
    summary: list[dict] = []
    metrics = ("legal_packets", "legal_bytes", "bursts_offered", "bursts_sent", "burst_drop_ratio")
    for scenario in EXPECTED:
        part = [row for row in rows if row["scenario"] == scenario]
        for metric in metrics:
            mean, low, high = ci95([float(row[metric]) for row in part])
            summary.append({"scenario": scenario, "metric": metric, "n": len(part), "mean": mean, "ci95_low": low, "ci95_high": high})
    write_csv(out / "scenario_summary.csv", summary)

    by_cell = {(int(row["seed"]), row["scenario"]): row for row in rows}
    contrasts: list[dict] = []
    for metric in ("legal_packets", "legal_bytes", "bursts_offered", "bursts_sent"):
        for reference, comparison in (("S0", "S1"), ("S1", "S2_rate_limit"), ("S1", "S2_isolation")):
            diffs = [float(by_cell[(seed, comparison)][metric]) - float(by_cell[(seed, reference)][metric]) for seed in sorted({int(r["seed"]) for r in rows})]
            mean, low, high = ci95(diffs)
            ref_mean = sum(float(by_cell[(seed, reference)][metric]) for seed in sorted({int(r["seed"]) for r in rows})) / len(diffs)
            contrasts.append({"metric": metric, "reference": reference, "comparison": comparison, "n_pairs": len(diffs), "mean_paired_difference": mean, "ci95_low": low, "ci95_high": high, "percent_of_reference_mean": 100 * mean / ref_mean if ref_mean else math.nan})
    write_csv(out / "paired_contrasts.csv", contrasts)
    (out / "validation.json").write_text(json.dumps({
        "complete": True,
        "validation_mode": "all raw traces independently reparsed and matched to retained metrics",
        "attempted_cells": len(rows),
        "successful_cells": len(rows),
        "failed_cells": 0,
        "expected_scenarios": list(EXPECTED),
    }, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("matrix"); ap.add_argument("--out", required=True)
    args = ap.parse_args(); root, out = Path(args.matrix).resolve(), Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True); rows = validate(root); summarize(rows, out)
    print(f"validated={len(rows)} failed=0 out={out}")


if __name__ == "__main__":
    main()
