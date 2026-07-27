#!/usr/bin/env python3
"""Run a paired NS-2.35+nOBS matrix from one versioned experiment config."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOBS_ROOT = HERE.parent
NS = NOBS_ROOT / "build/ns-allinone-2.35/ns-2.35/ns"
TCL = HERE / "scenario.tcl"
PARSER = HERE / "parse_trace.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def require(config: dict, *keys: str):
    value = config
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            raise SystemExit(f"missing experiment config key: {'.'.join(keys)}")
        value = value[key]
    return value


def load_config(path: Path) -> dict:
    config = json.loads(path.read_text(encoding="utf-8"))
    if config.get("schema") != "nobs-matrix-experiment-v1":
        raise SystemExit(f"unsupported experiment config schema: {config.get('schema')!r}")
    seeds = require(config, "seeds")
    scenarios = require(config, "scenarios")
    if not seeds or len(seeds) != len(set(seeds)) or any(not isinstance(x, int) or x <= 0 for x in seeds):
        raise SystemExit("experiment seeds must be unique positive integers")
    labels = [item.get("label") for item in scenarios]
    if not scenarios or len(labels) != len(set(labels)):
        raise SystemExit("experiment scenario labels must be non-empty and unique")
    network = require(config, "network")
    traffic = require(config, "traffic")
    if network.get("topology_profile") != "nobs-explicit-topology-v1":
        raise SystemExit(f"unsupported topology profile: {network.get('topology_profile')!r}")
    nodes = network.get("optical_nodes")
    links = network.get("optical_links")
    routes = network.get("optical_routes")
    ingresses = network.get("legal_ingress_by_flow")
    if not nodes or len(nodes) != len(set(nodes)) or nodes != list(range(len(nodes))):
        raise SystemExit("optical_nodes must be unique contiguous IDs starting at zero")
    if not links or any(len(link) != 2 or link[0] not in nodes or link[1] not in nodes for link in links):
        raise SystemExit("every optical link must contain two configured optical nodes")
    if not routes or any(route.get("source") not in nodes or route.get("destination") not in nodes
                         or not route.get("path") or route["path"][0] != route["source"]
                         or route["path"][-1] != route["destination"] for route in routes):
        raise SystemExit("every optical route must have configured endpoints and a matching path")
    if len(ingresses or []) != traffic.get("legal_flow_count") or any(node not in nodes for node in ingresses):
        raise SystemExit("legal_ingress_by_flow must provide one configured node per legal flow")
    for key in ("attacker_ingress_node", "receiver_egress_node"):
        if network.get(key) not in nodes:
            raise SystemExit(f"{key} must reference a configured optical node")
    target = network.get("attacker_target_receiver_index")
    if not isinstance(target, int) or not 0 <= target < traffic.get("legal_flow_count", 0):
        raise SystemExit("attacker_target_receiver_index is outside legal flows")
    return config


def experiment_env(config: dict) -> dict[str, str]:
    traffic = require(config, "traffic")
    network = require(config, "network")
    mitigation = require(config, "mitigation")
    simulation = require(config, "simulation")
    mapping = {
        "NOBS_LEGAL_FLOWS": traffic["legal_flow_count"],
        "NOBS_LEGAL_PACKET_BYTES": traffic["legal_packet_bytes"],
        "NOBS_LEGAL_ACCESS_MBPS": traffic["legal_access_mbps"],
        "NOBS_PROTECTED_LEGAL_FLOWS": traffic["protected_legal_flow_count"],
        "NOBS_PROTECTED_LEGAL_MBPS": traffic["protected_legal_mbps"],
        "NOBS_ATTACKER_COUNT": traffic["attacker_count"],
        "NOBS_ATTACKER_PACKET_BYTES": traffic["attacker_packet_bytes"],
        "NOBS_ATTACKER_ACCESS_MBPS": traffic["attacker_access_mbps"],
        "NOBS_ATTACK_START_S": traffic["attack_start_s"],
        "NOBS_LEGAL_START_STAGGER_S": traffic["legal_start_stagger_s"],
        "NOBS_TCP_WINDOW_PACKETS": traffic["tcp_window_packets"],
        "NOBS_LEGAL_FLOW_ID_BASE": traffic["legal_flow_id_base"],
        "NOBS_ATTACKER_FLOW_ID_BASE": traffic["attacker_flow_id_base"],
        "NOBS_ATTACK_MULTIPLIER_MIN": traffic["attack_multiplier_min"],
        "NOBS_ATTACK_MULTIPLIER_MAX": traffic["attack_multiplier_max"],
        "NOBS_OPTICAL_RATE_MBPS": network["optical_rate_mbps"],
        "NOBS_OPTICAL_NODES": ",".join(map(str, network["optical_nodes"])),
        "NOBS_OPTICAL_LINKS": ";".join(",".join(map(str, link)) for link in network["optical_links"]),
        "NOBS_OPTICAL_ROUTES": ";".join(
            f'{route["source"]}|{route["destination"]}|{" ".join(map(str, route["path"]))}'
            for route in network["optical_routes"]),
        "NOBS_LEGAL_INGRESS_BY_FLOW": ",".join(map(str, network["legal_ingress_by_flow"])),
        "NOBS_ATTACKER_INGRESS_NODE": network["attacker_ingress_node"],
        "NOBS_RECEIVER_EGRESS_NODE": network["receiver_egress_node"],
        "NOBS_ATTACKER_TARGET_RECEIVER_INDEX": network["attacker_target_receiver_index"],
        "NOBS_OPTICAL_NODE_TYPE": network["optical_node_type"],
        "NOBS_CONVERSION_TYPE": network["wavelength_conversion_type"],
        "NOBS_ACK_DONT_BURST": network["ack_dont_burst"],
        "NOBS_SOURCE_ROUTING": network["source_routing_enabled"],
        "NOBS_DEBUG_LEVEL": network["debug_level"],
        "NOBS_OPTICAL_DELAY_MS": network["optical_delay_ms"],
        "NOBS_ACCESS_DELAY_MS": network["electronic_access_delay_ms"],
        "NOBS_RECEIVER_ACCESS_MBPS": network["electronic_receiver_access_mbps"],
        "NOBS_QUEUE_PACKETS": network["electronic_queue_packets"],
        "NOBS_MAX_WAVELENGTHS": network["max_wavelengths_per_link"],
        "NOBS_BURST_MAX_PACKETS": network["burst_max_packets"],
        "NOBS_BURST_TIMEOUT_MS": network["burst_timeout_ms"],
        "NOBS_MAX_DELAYED_BURSTS": network["max_delayed_bursts"],
        "NOBS_MAX_FLOW_QUEUES": network["max_flow_queues"],
        "NOBS_JET_TYPE": network["jet_type"],
        "NOBS_CONVERTER_COUNT": network["converter_count_per_optical_node"],
        "NOBS_FDL_DELAYS_S": ",".join(map(str, network["fdl_delays_s"])),
        "NOBS_DETECTION_DELAY_S": mitigation["detection_delay_s"],
        "NOBS_RATE_LIMIT_CIR_MBPS": mitigation["rate_limit_cir_mbps_per_attacker"],
        "NOBS_TBF_BUCKET_BITS": mitigation["tbf_bucket_bits"],
        "NOBS_TBF_QUEUE_PACKETS": mitigation["tbf_queue_packets"],
        "NOBS_DRAIN_TIME_S": simulation["post_measurement_drain_s"],
    }
    return {key: str(value) for key, value in mapping.items()}


def run(args: argparse.Namespace) -> int:
    config_path = Path(args.config).resolve()
    for required in (config_path, NS, TCL, PARSER):
        if not required.is_file():
            raise SystemExit(f"missing required input: {required}")
    if not os.access(NS, os.X_OK):
        raise SystemExit(f"NS binary is not executable: {NS}")
    config = load_config(config_path)
    seeds = config["seeds"]
    scenarios = config["scenarios"]
    rate = float(require(config, "nominal_attack_rate_mbps_per_source"))
    sim_time = float(require(config, "simulation", "measurement_duration_s"))
    timeout = float(require(config, "simulation", "per_cell_timeout_s"))
    if rate <= 0 or sim_time <= 0 or timeout <= 0:
        raise SystemExit("attack rate, measurement duration, and timeout must be positive")

    out = Path(args.out).resolve()
    if out.exists() and any(out.iterdir()) and not args.resume:
        raise SystemExit(f"refusing to overwrite non-empty output: {out}")
    out.mkdir(parents=True, exist_ok=True)
    snapshot = out / "experiment_config.snapshot.json"
    if not snapshot.exists():
        shutil.copy2(config_path, snapshot)
    elif sha256(snapshot) != sha256(config_path):
        raise SystemExit("resume config does not match retained experiment snapshot")

    inputs = {"ns": sha256(NS), "scenario.tcl": sha256(TCL), "parse_trace.py": sha256(PARSER)}
    matrix_manifest = {
        "schema": "nobs-configured-matrix-run-v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "experiment_name": config["name"],
        "experiment_config_source": str(config_path),
        "experiment_config_sha256": sha256(snapshot),
        "expected_cells": len(seeds) * len(scenarios),
        "input_sha256": inputs,
    }
    write_json(out / "matrix_manifest.json", matrix_manifest)
    env = os.environ.copy()
    env.update(experiment_env(config))

    failures: list[str] = []
    successful = 0
    for seed in seeds:
        for item in scenarios:
            label, scenario, mitigation = item["label"], item["scenario"], item["mitigation"]
            run_dir = out / f"seed_{seed}" / label
            run_dir.mkdir(parents=True, exist_ok=True)
            run_path = run_dir / "run.json"
            if args.resume and run_path.is_file():
                prior = json.loads(run_path.read_text(encoding="utf-8"))
                if prior.get("exit_code") == 0 and (run_dir / "metrics.json").is_file():
                    successful += 1
                    print(f"SKIP seed={seed} {label}", flush=True)
                    continue
            command = [str(NS), str(TCL), scenario, str(seed), str(rate), str(sim_time), mitigation, "out.tr"]
            (run_dir / "command.txt").write_text(" ".join(command) + "\n", encoding="utf-8")
            print(f"RUN seed={seed} {label} rate={rate}", flush=True)
            try:
                with (run_dir / "stdout.log").open("w", encoding="utf-8") as stdout, (run_dir / "stderr.log").open("w", encoding="utf-8") as stderr:
                    result = subprocess.run(command, cwd=run_dir, env=env, stdout=stdout, stderr=stderr, timeout=timeout, check=False)
                rc = result.returncode
            except subprocess.TimeoutExpired:
                rc = 124
            record = {"seed": seed, "label": label, "scenario": scenario, "mitigation": mitigation,
                      "attack_rate_mbps_per_source": rate, "sim_time_s": sim_time, "exit_code": rc,
                      "experiment_config_sha256": matrix_manifest["experiment_config_sha256"]}
            trace = run_dir / "out.tr"
            if rc == 0 and trace.is_file():
                parsed = subprocess.run([sys.executable, str(PARSER), str(trace)], text=True, capture_output=True, check=False)
                if parsed.returncode == 0:
                    (run_dir / "metrics.json").write_text(parsed.stdout, encoding="utf-8")
                    record.update({"trace_bytes": trace.stat().st_size, "trace_sha256": sha256(trace),
                                   "metrics_sha256": sha256(run_dir / "metrics.json")})
                    successful += 1
                else:
                    rc = record["exit_code"] = 2
                    (run_dir / "parser.stderr.log").write_text(parsed.stderr, encoding="utf-8")
            if rc != 0:
                failures.append(f"seed={seed}/{label}:rc={rc}")
            write_json(run_path, record)
    write_json(out / "completion.json", {
        "complete": not failures and successful == matrix_manifest["expected_cells"],
        "attempted_cells": matrix_manifest["expected_cells"], "successful_cells": successful,
        "failed_cells": len(failures), "failures": failures,
    })
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="versioned experiment JSON; sole source of experiment parameters")
    parser.add_argument("--out", required=True)
    parser.add_argument("--resume", action="store_true")
    return run(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
