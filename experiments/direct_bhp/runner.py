#!/usr/bin/env python3
"""Run selected cells of the versioned native NS-2.35+nOBS direct-BHP experiment."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import validator

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
NOBS_SOURCE = REPO_ROOT / "nobs"
NS_TREE = Path(os.environ.get("NOBS_NS_TREE", REPO_ROOT / "build/ns-allinone-2.35/ns-2.35"))
NS = NS_TREE / "ns"
SCENARIO = HERE / "scenario.tcl"
VALIDATOR = HERE / "validator.py"
RUNNER = HERE / "runner.py"
TRACE_PARSER = HERE.parent / "parse_trace.py"
SOURCE_INPUTS = (
    "optical/op-bhp-guard.h", "optical/op-bhp-guard.cc",
    "optical/op-bhp-audit.h", "optical/op-bhp-audit.cc",
    "optical/op-bhp-flood-agent.h", "optical/op-bhp-flood-agent.cc",
    "optical/op-classifier.cc",
    "optical/op-sragent.h", "optical/op-sragent.cc",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def require(mapping: dict[str, Any], key: str) -> Any:
    if key not in mapping:
        raise SystemExit(f"missing config key: {key}")
    return mapping[key]


def load_config(path: Path, thesis_profile: bool) -> dict[str, Any]:
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
        validator.validate_config(config, thesis_profile=thesis_profile)
        validator.validate_detector_boundary()
        return config
    except (OSError, json.JSONDecodeError, validator.ValidationError) as exc:
        raise SystemExit(f"invalid experiment config/control boundary: {exc}") from exc


def encoded_environment(config: dict[str, Any], item: dict[str, Any]) -> dict[str, str]:
    topology = config["topology"]
    traffic = config["traffic"]
    profile = item["profile"]
    values = {
        "NOBS_ATTACK_ENABLED": int(item["attack"]),
        "NOBS_OPTICAL_NODES": ",".join(map(str, topology["optical_nodes"])),
        "NOBS_OPTICAL_LINKS": ";".join(",".join(map(str, edge)) for edge in topology["optical_links"]),
        "NOBS_OPTICAL_ROUTES": ";".join(
            f'{route["source"]}|{route["destination"]}|{" ".join(map(str, route["path"]))}'
            for route in topology["routes"]
        ),
        "NOBS_LEGAL_SENDERS": ",".join(map(str, traffic["legal_sender_ids"])),
        "NOBS_LEGAL_RECEIVERS": ",".join(map(str, traffic["legal_receiver_ids"])),
        "NOBS_LEGAL_INGRESSES": ",".join(map(str, traffic["legal_ingress_by_flow"])),
        "NOBS_LEGAL_FLOW_COUNT": traffic["legal_flow_count"],
        "NOBS_LEGAL_PACKET_BYTES": traffic["legal_packet_bytes"],
        "NOBS_LEGAL_ACCESS_MBPS": traffic["legal_access_mbps"],
        "NOBS_TCP_WINDOW_PACKETS": traffic["tcp_window_packets"],
        "NOBS_LEGAL_START_STAGGER_S": traffic["legal_start_stagger_s"],
        "NOBS_LEGAL_FLOW_ID_BASE": traffic["legal_flow_id_base"],
        "NOBS_ATTACKER_COUNT": traffic["attacker_count"],
        "NOBS_ATTACK_START_S": traffic["attacker_start_s"],
        "NOBS_ATTACK_STOP_S": traffic["attacker_stop_s"],
        "NOBS_ATTACKER_PACKET_BYTES": traffic["attacker_packet_bytes"],
        "NOBS_BHP_CLAIMED_PACKET_COUNT": traffic["bhp_claimed_packet_count"],
        "NOBS_BHP_ROUTE_CLASS": traffic["bhp_route_class"],
        "NOBS_ATTACKER_INGRESS": topology["attacker_ingress"],
        "NOBS_RECEIVER_EGRESS": topology["receiver_egress"],
        "NOBS_OPTICAL_RATE_MBPS": topology["optical_rate_mbps"],
        "NOBS_OPTICAL_DELAY_MS": topology["optical_delay_ms"],
        "NOBS_RECEIVER_ACCESS_MBPS": topology["receiver_access_mbps"],
        "NOBS_ACCESS_DELAY_MS": topology["access_delay_ms"],
        "NOBS_QUEUE_PACKETS": topology["queue_packets"],
        "NOBS_NODE_TYPE": topology["node_type"],
        "NOBS_CONVERSION_TYPE": topology["conversion_type"],
        "NOBS_CONVERTER_COUNT": topology["converter_count"],
        "NOBS_FDL_DELAYS_S": ",".join(map(str, topology["fdl_delays_s"])),
        "NOBS_MAX_WAVELENGTHS": topology["max_wavelengths"],
        "NOBS_BURST_MAX_PACKETS": topology["burst_max_packets"],
        "NOBS_BURST_TIMEOUT_MS": topology["burst_timeout_ms"],
        "NOBS_MAX_DELAYED_BURSTS": topology["max_delayed_bursts"],
        "NOBS_MAX_FLOW_QUEUES": topology["max_flow_queues"],
        "NOBS_JET_TYPE": topology["jet_type"],
        "NOBS_SOURCE_ROUTING": topology["source_routing"],
        "NOBS_ACK_DONT_BURST": topology["ack_dont_burst"],
        "NOBS_GUARD_EVENT_CAPACITY": profile["event_capacity"],
        "NOBS_GUARD_EVENT_RATE": profile["event_rate"],
        "NOBS_GUARD_RESERVATION_CAPACITY": profile["reservation_capacity"],
        "NOBS_GUARD_RESERVATION_RATE": profile["reservation_rate"],
        "NOBS_GUARD_VIOLATIONS": profile["violations"],
        "NOBS_GUARD_HOLD_DOWN_S": profile["hold_down_s"],
        "NOBS_GUARD_LIMITED_RELEASE_S": profile["limited_release_s"],
    }
    return {key: str(value) for key, value in values.items()}


def effective_rate(config: dict[str, Any], seed: int) -> tuple[float, float]:
    jitter = float(config["traffic"]["attack_rate_jitter"])
    raw = hashlib.sha256(f'{config["schema"]}:{seed}'.encode()).digest()
    unit = int.from_bytes(raw[:8], "big") / float(2**64 - 1)
    multiplier = (1.0 - jitter) + (2.0 * jitter * unit)
    return float(config["nominal_attack_rate_mbps_per_source"]) * multiplier, multiplier


def input_hashes(snapshot: Path) -> dict[str, str]:
    paths = {
        "experiment_config.snapshot.json": snapshot,
        "scenario.tcl": SCENARIO,
        "validator.py": VALIDATOR,
        "runner.py": RUNNER,
        "parse_trace.py": TRACE_PARSER,
        "ns": NS,
    }
    paths.update({name: NOBS_SOURCE / name for name in SOURCE_INPUTS})
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise SystemExit(f"missing required native input(s): {missing}")
    return {name: sha256(path) for name, path in sorted(paths.items())}


# NS-2 writes stat.txt in the cell working directory.  It is retained and
# hashed as part of the native run, rather than treated as an untracked side
# effect that could be silently lost.
ARTIFACTS = ("out.tr", "stat.txt", "bhp_audit.log", "bhp_source.log", "stdout.log", "stderr.log")


def select_cells(config: dict[str, Any], seeds: list[int] | None, labels: list[str] | None) -> list[tuple[int, dict[str, Any]]]:
    configured_seeds = config["seeds"]
    by_label = {item["label"]: item for item in config["scenarios"]}
    chosen_seeds = configured_seeds if not seeds else seeds
    chosen_labels = list(by_label) if not labels else labels
    invalid_seeds = sorted(set(chosen_seeds) - set(configured_seeds))
    invalid_labels = sorted(set(chosen_labels) - set(by_label))
    if invalid_seeds or invalid_labels:
        raise SystemExit(f"unconfigured selection: seeds={invalid_seeds}, labels={invalid_labels}")
    if len(chosen_seeds) != len(set(chosen_seeds)) or len(chosen_labels) != len(set(chosen_labels)):
        raise SystemExit("duplicate --seed or --label selection")
    return [(seed, by_label[label]) for seed in chosen_seeds for label in chosen_labels]


def run_cell(
    config: dict[str, Any], seed: int, item: dict[str, Any], run_dir: Path,
    hashes: dict[str, str], config_hash: str,
) -> tuple[bool, dict[str, Any]]:
    run_dir.mkdir(parents=True, exist_ok=False)
    rate, multiplier = effective_rate(config, seed)
    duration = float(config["simulation"]["duration_s"])
    command = [
        str(NS), str(SCENARIO), item["scenario"], str(seed), format(rate, ".17g"),
        format(duration, ".17g"), "out.tr", "bhp_audit.log", "bhp_source.log",
    ]
    (run_dir / "command.txt").write_text(" ".join(command) + "\n", encoding="utf-8")
    env = os.environ.copy()
    env.update(encoded_environment(config, item))
    started_utc = utc_now()
    started = time.monotonic()
    timed_out = False
    with (run_dir / "stdout.log").open("w", encoding="utf-8") as stdout, \
         (run_dir / "stderr.log").open("w", encoding="utf-8") as stderr:
        try:
            result = subprocess.run(
                command, cwd=run_dir, env=env, stdout=stdout, stderr=stderr,
                timeout=float(config["simulation"]["per_cell_timeout_s"]), check=False,
            )
            return_code = result.returncode
        except subprocess.TimeoutExpired:
            return_code = 124
            timed_out = True
    finished_utc = utc_now()
    artifacts = ARTIFACTS
    present = {name: sha256(run_dir / name) for name in artifacts if (run_dir / name).is_file()}
    record: dict[str, Any] = {
        "schema": "nobs-direct-bhp-cell-v1",
        "seed": seed,
        "label": item["label"],
        "scenario": item["scenario"],
        "mitigation": item.get("mitigation"),
        "attack_enabled": item["attack"],
        "nominal_attack_rate_mbps_per_source": config["nominal_attack_rate_mbps_per_source"],
        "seed_rate_multiplier": multiplier,
        "effective_attack_rate_mbps_per_source": rate,
        "duration_s": duration,
        "started_utc": started_utc,
        "finished_utc": finished_utc,
        "elapsed_wall_s": time.monotonic() - started,
        "exit_code": return_code,
        "timed_out": timed_out,
        "command_argv": command,
        "config_sha256": config_hash,
        "input_sha256": hashes,
        "artifact_sha256": present,
    }
    write_json(run_dir / "run.json", record)
    success = return_code == 0 and all((run_dir / name).is_file() for name in artifacts)
    return success, record


def execute(args: argparse.Namespace) -> int:
    config_path = Path(args.config).resolve()
    config = load_config(config_path, thesis_profile=not args.allow_nonthesis_profile)
    cells = select_cells(config, args.seed, args.label)
    output = Path(args.out).resolve()
    if output.exists():
        if any(output.iterdir()):
            raise SystemExit(f"refusing to overwrite non-empty output directory: {output}")
    else:
        output.mkdir(parents=True)
    snapshot = output / "experiment_config.snapshot.json"
    shutil.copyfile(config_path, snapshot)
    hashes = input_hashes(snapshot)
    config_hash = hashes["experiment_config.snapshot.json"]
    all_pairs = {(seed, item["label"]) for seed in config["seeds"] for item in config["scenarios"]}
    selected_pairs = {(seed, item["label"]) for seed, item in cells}
    manifest = {
        "schema": "nobs-direct-bhp-matrix-v1",
        "created_utc": utc_now(),
        "experiment_name": config["name"],
        "config_source": str(config_path),
        "config_sha256": config_hash,
        "input_sha256": hashes,
        "expected_selected_cells": len(cells),
        "full_matrix_requested": selected_pairs == all_pairs,
        "selected_cells": [{"seed": seed, "label": item["label"]} for seed, item in cells],
    }
    write_json(output / "matrix_manifest.json", manifest)
    failures: list[dict[str, Any]] = []
    successful = 0
    for seed, item in cells:
        run_dir = output / f"seed_{seed}" / item["label"]
        print(f'RUN seed={seed} label={item["label"]}', flush=True)
        success, record = run_cell(config, seed, item, run_dir, hashes, config_hash)
        if success:
            successful += 1
        else:
            failures.append({"seed": seed, "label": item["label"], "exit_code": record["exit_code"]})
    completion = {
        "schema": "nobs-direct-bhp-completion-v1",
        "finished_utc": utc_now(),
        "expected_selected_cells": len(cells),
        "successful_cells": successful,
        "failed_cells": len(failures),
        "failures": failures,
        "complete": not failures and successful == len(cells),
        "full_matrix_complete": not failures and selected_pairs == all_pairs,
    }
    write_json(output / "completion.json", completion)
    if failures:
        return 1
    try:
        report = validator.validate_results(config, output)
        write_json(output / "validation.json", report)
    except (OSError, json.JSONDecodeError, validator.ValidationError) as exc:
        (output / "validation.stderr.log").write_text(f"validation failed: {exc}\n", encoding="utf-8")
        return 1
    print(f"COMPLETE cells={successful} full_matrix={completion['full_matrix_complete']}", flush=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(HERE / "config.json"))
    parser.add_argument("--out", required=True)
    parser.add_argument("--seed", action="append", type=int, help="configured seed; repeatable")
    parser.add_argument("--label", action="append", help="configured scenario label; repeatable")
    parser.add_argument("--allow-nonthesis-profile", action="store_true", help="permit a reduced config for smoke testing")
    return execute(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
