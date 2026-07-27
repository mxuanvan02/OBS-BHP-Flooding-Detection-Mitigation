#!/usr/bin/env python3
"""Validate a completed S1 nOBS rate sweep and emit trace-derived tables."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

try:
    from scipy.stats import t as student_t
except ImportError as exc:  # pragma: no cover
    raise SystemExit("SciPy is required for the reported Student-t confidence intervals") from exc

HERE = Path(__file__).resolve().parent
TRACE_PARSER = HERE / "parse_trace.py"
RUN_CONFIG = re.compile(
    r"attack_multiplier=(?P<multiplier>[-+0-9.eE]+) "
    r"effective_attack_rate_mbps_per_source=(?P<effective>[-+0-9.eE]+)"
)
REQUIRED_MANIFEST = {
    "schema": "nobs-s1-rate-sweep-v1",
    "scenario": "S1",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty table: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def ci95(values: list[float]) -> tuple[float, float, float]:
    n = len(values)
    mean = sum(values) / n
    if n < 2:
        return mean, math.nan, math.nan
    variance = sum((value - mean) ** 2 for value in values) / (n - 1)
    critical = float(student_t.ppf(0.975, n - 1))
    half = critical * math.sqrt(variance / n)
    return mean, mean - half, mean + half


def _load_trace_metrics(trace_path: Path) -> dict:
    completed = subprocess.run(
        [sys.executable, str(TRACE_PARSER), str(trace_path)],
        check=False, capture_output=True, text=True,
    )
    if completed.returncode != 0:
        raise ValueError(f"trace parser failed for {trace_path}: {completed.stderr.strip()}")
    return json.loads(completed.stdout)


def validate(root: Path) -> tuple[list[dict], dict]:
    completion = json.loads((root / "completion.json").read_text(encoding="utf-8"))
    if not completion.get("complete") or completion.get("failed_cells") != 0:
        raise ValueError(f"sweep incomplete: {completion}")
    manifest = json.loads((root / "sweep_manifest.json").read_text(encoding="utf-8"))
    for key, expected_value in REQUIRED_MANIFEST.items():
        if manifest.get(key) != expected_value:
            raise ValueError(f"invalid manifest {key}: {manifest.get(key)!r}")
    rates = [float(value) for value in manifest["rates_mbps_per_source"]]
    seeds = [int(value) for value in manifest["seeds"]]
    if not rates or not seeds or len(rates) != len(set(rates)) or len(seeds) != len(set(seeds)):
        raise ValueError("rates and seeds must be non-empty and unique")
    if any(not math.isfinite(rate) or rate <= 0 for rate in rates):
        raise ValueError("rates must be finite and positive")
    expected = {(rate, seed) for rate in rates for seed in seeds}
    if manifest.get("expected_cells") != len(expected):
        raise ValueError("manifest expected_cells does not match rates x seeds")
    if (completion.get("attempted_cells") != len(expected)
            or completion.get("successful_cells") != len(expected)):
        raise ValueError("completion accounting does not match manifest")
    actual = {
        (float(path.parent.parent.name.removeprefix("rate_")),
         int(path.parent.name.removeprefix("seed_")))
        for path in root.glob("rate_*/seed_*/run.json")
    }
    if actual != expected:
        raise ValueError(f"cell directory mismatch: missing={sorted(expected-actual)} extra={sorted(actual-expected)}")

    rows: list[dict] = []
    seen: set[tuple[float, int]] = set()
    for rate, seed in sorted(expected):
        cell = root / f"rate_{rate:g}" / f"seed_{seed}"
        run_path = cell / "run.json"
        metrics_path = cell / "metrics.json"
        trace_path = cell / "out.tr"
        for path in (run_path, metrics_path, trace_path, cell / "stdout.log", cell / "stderr.log", cell / "command.txt"):
            if not path.is_file():
                raise ValueError(f"missing artifact: {path}")
        run = json.loads(run_path.read_text(encoding="utf-8"))
        if run.get("exit_code") != 0 or float(run.get("rate_mbps_per_source")) != rate or int(run.get("seed")) != seed:
            raise ValueError(f"invalid run record: rate={rate:g}/seed={seed}")
        if sha256(trace_path) != run.get("trace_sha256") or sha256(metrics_path) != run.get("metrics_sha256"):
            raise ValueError(f"hash mismatch: rate={rate:g}/seed={seed}")
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        reparsed = _load_trace_metrics(trace_path)
        if metrics != reparsed:
            raise ValueError(f"metrics are not derived from retained trace: rate={rate:g}/seed={seed}")
        if metrics.get("schema") != "ns2-old-12-field":
            raise ValueError(f"invalid metrics schema: rate={rate:g}/seed={seed}")
        if int(run.get("trace_bytes", -1)) != trace_path.stat().st_size:
            raise ValueError(f"trace byte count mismatch: rate={rate:g}/seed={seed}")
        match = RUN_CONFIG.search((cell / "stdout.log").read_text(encoding="utf-8"))
        if not match:
            raise ValueError(f"missing RUN_CONFIG: rate={rate:g}/seed={seed}")
        tcp = metrics["transport"]["tcp"]
        optical = metrics["optical"]
        attempted = int(optical["control_link_reservations_attempted"])
        succeeded = int(optical["control_link_reservations_succeeded"])
        failed = int(optical["control_link_reservations_failed"])
        if attempted != succeeded + failed:
            raise ValueError(f"reservation accounting mismatch: rate={rate:g}/seed={seed}")
        offered = int(optical["data_bursts_offered"])
        sent = int(optical["data_bursts_sent_end_to_end"])
        dropped = int(optical["data_bursts_explicitly_dropped"])
        loss_rate = float(optical["data_burst_drop_ratio"])
        if min(attempted, succeeded, failed, offered, sent, dropped) < 0:
            raise ValueError(f"negative metric: rate={rate:g}/seed={seed}")
        expected_loss = dropped / offered if offered else 0.0
        if not math.isclose(loss_rate, expected_loss, rel_tol=1e-12, abs_tol=1e-15):
            raise ValueError(f"burst loss ratio mismatch: rate={rate:g}/seed={seed}")
        rows.append({
            "attack_rate_mbps": rate,
            "seed": seed,
            "attack_multiplier": float(match["multiplier"]),
            "effective_attack_rate_mbps_per_source": float(match["effective"]),
            "legal_packets": int(tcp["legal_receive_packets"]),
            "legal_bytes": int(tcp["legal_receive_bytes"]),
            "bursts_offered": offered,
            "bursts_sent": sent,
            "bursts_explicitly_dropped": dropped,
            "burst_loss_rate": loss_rate,
            "control_reservations_attempted": attempted,
            "control_reservations_succeeded": succeeded,
            "control_reservations_failed": failed,
            "control_unresolved_at_trace_end": int(optical["control_packets_unresolved_at_trace_end"]),
            "trace_bytes": int(run["trace_bytes"]),
            "trace_sha256": run["trace_sha256"],
            "metrics_sha256": run["metrics_sha256"],
            "exit_code": 0,
        })
        seen.add((rate, seed))
    if seen != expected:
        raise ValueError(f"cell mismatch: missing={sorted(expected - seen)} extra={sorted(seen - expected)}")
    return rows, manifest


def summarize(rows: list[dict], manifest: dict, out: Path) -> None:
    write_csv(out / "sweep.csv", rows)
    grouped: dict[float, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[float(row["attack_rate_mbps"])].append(row)
    summary: list[dict] = []
    metrics = ("legal_packets", "legal_bytes", "bursts_offered", "bursts_sent", "burst_loss_rate")
    for rate in sorted(grouped):
        part = grouped[rate]
        for metric in metrics:
            mean, low, high = ci95([float(row[metric]) for row in part])
            summary.append({
                "attack_rate_mbps": rate,
                "metric": metric,
                "n": len(part),
                "mean": mean,
                "ci95_low": low,
                "ci95_high": high,
            })
    write_csv(out / "sweep_summary.csv", summary)
    multipliers = sorted({float(row["attack_multiplier"]) for row in rows})
    validation = {
        "complete": True,
        "attempted_cells": len(rows),
        "successful_cells": len(rows),
        "failed_cells": 0,
        "rates": sorted(grouped),
        "seeds_per_rate": {str(rate): len(grouped[rate]) for rate in sorted(grouped)},
        "statistics_scope": "descriptive intervals across the retained fixed seeds",
        "attack_multiplier_min": min(multipliers),
        "attack_multiplier_max": max(multipliers),
        "input_sha256": manifest["input_sha256"],
    }
    (out / "sweep_validation.json").write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("sweep")
    parser.add_argument("--out", required=True)
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    root = Path(args.sweep).resolve()
    out = Path(args.out).resolve()
    if out.exists() and any(out.iterdir()) and not args.replace:
        raise SystemExit(f"refusing to replace non-empty output without --replace: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    rows, manifest = validate(root)
    with tempfile.TemporaryDirectory(prefix=f".{out.name}.", dir=out.parent) as tempdir:
        staged = Path(tempdir)
        summarize(rows, manifest, staged)
        out.mkdir(parents=True, exist_ok=True)
        for source in staged.iterdir():
            os.replace(source, out / source.name)
    print(f"validated={len(rows)} failed=0 out={out}")


if __name__ == "__main__":
    main()
