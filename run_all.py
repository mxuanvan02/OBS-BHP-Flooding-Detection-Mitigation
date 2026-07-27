from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import shutil
from pathlib import Path

import numpy as np

from simulator import simulate


def mean_ci(values):
    x = np.asarray(values, dtype=float)
    mean = float(x.mean())
    if len(x) < 2:
        return mean, None, None
    half = 1.96 * float(x.std(ddof=1)) / np.sqrt(len(x))
    return mean, mean - half, mean + half


def write_csv(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/default.json")
    parser.add_argument("--out", default="results")
    args = parser.parse_args()

    root = Path(__file__).parent
    cfg = json.loads((root / args.config).read_text())
    out = root / args.out
    if out.exists():
        shutil.rmtree(out)
    raw = out / "raw"
    tables = out / "tables"
    figures = out / "figures"
    raw.mkdir(parents=True)
    tables.mkdir()
    figures.mkdir()

    rows = []
    windows = []
    scenarios = ["S0", "S1", "S2_rate_limit", "S2_isolation"]
    for scenario in scenarios:
        seeds = cfg["simulation"]["seeds"]
        if scenario == "S2_isolation":
            seeds = seeds[:6]
        for seed in seeds:
            result = simulate(cfg, scenario, seed)
            rows.append({
                "scenario": scenario,
                "seed": seed,
                "attack_rate_mbps": result.attack_rate_mbps,
                "legal_packets": result.legal_packets,
                "legal_bytes": result.legal_bytes,
                "bursts_sent": result.bursts_sent,
                "bursts_lost": result.bursts_lost,
                "burst_loss_rate": result.burst_loss_rate,
                "status": "completed",
            })
            windows.extend({"scenario": scenario, "seed": seed, **item} for item in result.windows)

    sweep = []
    for rate in cfg["sweep"]["rates_mbps"]:
        for seed in cfg["sweep"]["seeds"]:
            result = simulate(cfg, "S1", seed, rate)
            sweep.append({
                "attack_rate_mbps": rate,
                "seed": seed,
                "legal_packets": result.legal_packets,
                "bursts_sent": result.bursts_sent,
                "burst_loss_rate": result.burst_loss_rate,
            })

    write_csv(raw / "runs.csv", rows)
    write_csv(raw / "window_dataset.csv", windows)
    write_csv(raw / "sweep.csv", sweep)

    summary = []
    for scenario in scenarios:
        scenario_rows = [row for row in rows if row["scenario"] == scenario]
        for metric in ["legal_packets", "legal_bytes", "bursts_sent", "burst_loss_rate"]:
            mean, low, high = mean_ci([float(row[metric]) for row in scenario_rows])
            summary.append({
                "scenario": scenario,
                "n": len(scenario_rows),
                "metric": metric,
                "mean": mean,
                "ci95_low": low,
                "ci95_high": high,
            })
    write_csv(tables / "scenario_summary.csv", summary)

    manifest = {
        "project": "obs-bhp-reproduction-mvp",
        "classification": "reproduced_mvp_with_explicit_assumptions",
        "source_pdf": "deliverables/LuanVan_ThS_NguyenQuangTin_CAPNHAT_KETQUA_NS2_20260726.pdf",
        "python": platform.python_version(),
        "numpy": np.__version__,
        "config": cfg,
        "reported_targets": {
            "S0_legal_packets": 82568,
            "S1_legal_packets": 38281,
            "S0_bursts": 40462,
            "S1_bursts": 64839,
            "S1_reduction_percent": -53.6,
        },
        "notes": [
            "Not NS-2.35+nOBS bit-for-bit reproduction.",
            "Missing thesis artifacts are documented in README and thesis_requirements.md.",
            "S2 isolation uses n=6 as reported.",
        ],
    }
    manifest["config_sha256"] = hashlib.sha256(
        json.dumps(cfg, sort_keys=True).encode()
    ).hexdigest()
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))

    from ml_pipeline import run_ml_pipeline
    from plot_results import make_plots

    run_ml_pipeline(raw / "window_dataset.csv", tables)
    make_plots(raw, tables, figures)
    print(f"Wrote {len(rows)} runs, {len(windows)} windows, {len(sweep)} sweep rows to {out}")


if __name__ == "__main__":
    main()
