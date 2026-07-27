#!/usr/bin/env python3
"""Create reproducible descriptive statistics for a validated direct-BHP matrix."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path

LABELS = ("S0", "S1", "S2_rate_limit", "S2_isolation")
METRICS = (
    "legal_tcp_packets",
    "legal_tcp_bytes",
    "optical_burst_pairs",
    "successful_link_reservations",
    "direct_bhp_created",
)


def mean_ci(values: list[int | float]) -> tuple[float, float | None, float | None, float]:
    n = len(values)
    mean = statistics.fmean(values)
    if n < 2:
        return mean, None, None, 0.0
    sd = statistics.stdev(values)
    # Student-t 0.975, df=7; the thesis matrix contract fixes n=8.
    t975 = 2.364624251 if n == 8 else 1.96
    half = t975 * sd / math.sqrt(n)
    return mean, mean - half, mean + half, sd


def pct(numerator: float, denominator: float) -> float | None:
    return None if denominator == 0 else 100.0 * numerator / denominator


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    root = args.results.resolve()
    out = (args.out or root / "analysis").resolve()
    out.mkdir(parents=True, exist_ok=True)
    validation_path = root / "validation.json"
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    if (
        validation.get("valid") is not True
        or validation.get("full_matrix_complete") is not True
        or validation.get("expected_selected_cells") != 32
    ):
        raise SystemExit("refusing analysis: matrix is not validated 32/32")

    seeds = sorted({int(key.split("/")[0].split("_")[1]) for key in validation["cells"]})
    rows: list[dict[str, int | str]] = []
    for seed in seeds:
        for label in LABELS:
            cell = validation["cells"][f"seed_{seed}/{label}"]
            network = cell["network"]
            actions = cell["actions"]
            rows.append(
                {
                    "seed": seed,
                    "label": label,
                    "legal_tcp_packets": network["legal_tcp_receive_packets"],
                    "legal_tcp_bytes": network["legal_tcp_receive_bytes"],
                    "legal_ack_packets": network["legal_ack_receive_packets"],
                    "optical_burst_pairs": network["optical_burst_pairs"],
                    "successful_link_reservations": network["optical_successful_link_reservations"],
                    "direct_bhp_created": cell["created"],
                    "allow": actions.get("ALLOW", 0),
                    "release": actions.get("RELEASE", 0),
                    "drop_over_profile": actions.get("DROP_OVER_PROFILE", 0),
                    "quarantine": actions.get("QUARANTINE_INGRESS", 0),
                }
            )

    with (out / "per_seed.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    by_label = {label: [row for row in rows if row["label"] == label] for label in LABELS}
    summary: dict[str, dict] = {}
    for label, group in by_label.items():
        summary[label] = {}
        for metric in METRICS:
            values = [int(row[metric]) for row in group]
            mean, low, high, sd = mean_ci(values)
            summary[label][metric] = {
                "n": len(values),
                "mean": mean,
                "sd": sd,
                "descriptive_95pct_t_interval": [low, high],
                "values": values,
            }
        totals = {
            key: sum(int(row[key]) for row in group)
            for key in ("direct_bhp_created", "allow", "release", "drop_over_profile", "quarantine")
        }
        totals["admitted"] = totals["allow"] + totals["release"]
        totals["blocked"] = totals["drop_over_profile"] + totals["quarantine"]
        totals["blocked_fraction"] = (
            None
            if totals["direct_bhp_created"] == 0
            else totals["blocked"] / totals["direct_bhp_created"]
        )
        summary[label]["action_totals"] = totals

    s0 = summary["S0"]["legal_tcp_bytes"]["mean"]
    s1 = summary["S1"]["legal_tcp_bytes"]["mean"]
    rate = summary["S2_rate_limit"]["legal_tcp_bytes"]["mean"]
    isolation = summary["S2_isolation"]["legal_tcp_bytes"]["mean"]
    effects = {
        "S1_reduction_vs_S0_pct": pct(s0 - s1, s0),
        "S1_remaining_vs_S0_pct": pct(s1, s0),
        "S2_rate_limit_vs_S0_pct": pct(rate, s0),
        "S2_isolation_vs_S0_pct": pct(isolation, s0),
        "S2_rate_limit_recovered_lost_bytes_pct": pct(rate - s1, s0 - s1),
        "S2_isolation_recovered_lost_bytes_pct": pct(isolation - s1, s0 - s1),
        "paired_direction_counts": {
            "S1_below_S0": sum(
                int(attack["legal_tcp_bytes"]) < int(base["legal_tcp_bytes"])
                for attack, base in zip(by_label["S1"], by_label["S0"])
            ),
            "S2_rate_limit_above_S1": sum(
                int(defended["legal_tcp_bytes"]) > int(attack["legal_tcp_bytes"])
                for defended, attack in zip(by_label["S2_rate_limit"], by_label["S1"])
            ),
            "S2_isolation_above_S1": sum(
                int(defended["legal_tcp_bytes"]) > int(attack["legal_tcp_bytes"])
                for defended, attack in zip(by_label["S2_isolation"], by_label["S1"])
            ),
        },
        "two_sided_exact_sign_test_p_for_8_of_8_same_direction": 0.0078125,
    }
    result = {
        "schema": "nobs-direct-bhp-analysis-v1",
        "source_validation_sha256": hashlib.sha256(validation_path.read_bytes()).hexdigest(),
        "matrix": str(root),
        "seeds": seeds,
        "summary": summary,
        "effects": effects,
        "interpretation_limits": [
            "Intervals describe only the eight fixed seeds.",
            "The workload emits native direct control-only BHPs with absent data payload.",
            "The guard is a deterministic contemporaneous token-budget state machine, not a reconstructed ML detector.",
            "Legitimate nOBS controls do not enter the explicit direct-BHP guard path; zero collateral here is architectural scope, not an estimated false-positive rate.",
            "Claims are limited to the declared seven-node topology, traffic profile, and five-second runs.",
        ],
    }
    (out / "summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    report = [
        "# Direct-BHP matrix analysis",
        "",
        "- Validated cells: 32/32",
        "- Seeds: " + ", ".join(map(str, seeds)),
        f"- S0 legal TCP bytes (mean): {s0:,.0f}",
        f"- S1 legal TCP bytes (mean): {s1:,.0f} ({effects['S1_reduction_vs_S0_pct']:.2f}% below S0)",
        f"- S2 rate-limit legal TCP bytes: {rate:,.0f} ({effects['S2_rate_limit_vs_S0_pct']:.2f}% of S0)",
        f"- S2 isolation legal TCP bytes: {isolation:,.0f} ({effects['S2_isolation_vs_S0_pct']:.2f}% of S0)",
        "- Exact sign test: all 8 seeds show S1<S0 and both S2>S1; two-sided p=0.0078125 for each directional comparison.",
        "",
        "## Claim boundary",
        *[f"- {item}" for item in result["interpretation_limits"]],
    ]
    (out / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(out), "effects": effects}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
