#!/usr/bin/env python3
"""Fail-closed validation for the direct BHP control-path experiment."""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
SOURCE_TREE = REPO_ROOT / "nobs"
NS_TREE = REPO_ROOT / "build/ns-allinone-2.35/ns-2.35"
OBSERVATION_HEADER = SOURCE_TREE / "optical/op-bhp-guard.h"
SRAGENT_SOURCE = SOURCE_TREE / "optical/op-sragent.cc"
SCENARIO = HERE / "scenario.tcl"
TRACE_PARSER = HERE.parent / "parse_trace.py"
SCHEMA = "nobs-direct-bhp-experiment-v1"
EXPECTED_LABELS = {"S0", "S1", "S2_rate_limit", "S2_isolation"}
EXPECTED_SEEDS = [101, 202, 303, 404, 505, 606, 707, 808]
OBSERVATION_FIELDS = {
    "event_time", "trusted_ingress", "packet_uid", "destination", "route_class",
    "claimed_burst_bytes", "claimed_packet_count", "claimed_reservation_cost",
    "syntax_valid", "range_valid", "route_consistent",
}
AUDIT_PREFIX = [
    "type", "event_time", "packet_uid", "burst_id", "ingress", "destination",
    "route_class", "claimed_bytes", "claimed_packets", "reservation_cost",
    "state_before", "state_after", "action", "reason", "detection_time",
    "decision_time", "action_time", "reservation_attempted", "cleanup_succeeded",
]
AUDIT_COLUMNS = AUDIT_PREFIX + [
    "reservation_result", "control_result", "data_result", "right_censored",
    "data_uid", "impact_packets", "impact_bytes", "impact_reason",
]
AUDIT_TYPES = {"OBSERVE", "DETECT", "DECIDE", "ACT", "OUTCOME", "LEGIT_IMPACT"}
# The native logger's format strings append a small, record-type-specific
# number of empty CSV fields.  This is a property of the audited native class,
# not an invitation to accept arbitrary wide rows.  We trim only these known
# empty suffixes and reject every other width/content combination.
NATIVE_TRAILING_EMPTY_FIELDS = {
    "OBSERVE": 2,
    "DETECT": 1,
    "DECIDE": 1,
    "ACT": 0,
    "OUTCOME": 0,
    "LEGIT_IMPACT": 0,
}

SOURCE_TYPES = {"BHP_CREATE"}
SOURCE_TRAILING_EMPTY_FIELDS = {"BHP_CREATE": 0}

class ValidationError(ValueError):
    pass


def _load_trace_parser():
    spec = importlib.util.spec_from_file_location("direct_bhp_parse_trace", TRACE_PARSER)
    if spec is None or spec.loader is None:
        raise ValidationError("cannot load retained-trace parser")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


TRACE = _load_trace_parser()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _require(mapping: dict[str, Any], key: str, kind: type | tuple[type, ...] | None = None) -> Any:
    if key not in mapping:
        raise ValidationError(f"missing config key: {key}")
    value = mapping[key]
    if kind is not None and (isinstance(value, bool) or not isinstance(value, kind)):
        raise ValidationError(f"invalid type for config key: {key}")
    return value


def _positive(value: Any, name: str, allow_zero: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise ValidationError(f"{name} must be finite numeric")
    if value < 0 or (value == 0 and not allow_zero):
        raise ValidationError(f"{name} must be {'nonnegative' if allow_zero else 'positive'}")
    return float(value)


def validate_config(config: dict[str, Any], thesis_profile: bool = True) -> None:
    if config.get("schema") != SCHEMA or config.get("version") != 1:
        raise ValidationError("unsupported direct-BHP config schema/version")
    seeds = _require(config, "seeds", list)
    if not seeds or len(seeds) != len(set(seeds)) or any(type(seed) is not int or seed <= 0 for seed in seeds):
        raise ValidationError("seeds must be unique positive integers")
    _positive(_require(config, "nominal_attack_rate_mbps_per_source"), "nominal attack rate")
    simulation = _require(config, "simulation", dict)
    duration = _positive(_require(simulation, "duration_s"), "duration")
    _positive(_require(simulation, "per_cell_timeout_s"), "cell timeout")
    topology = _require(config, "topology", dict)
    nodes = _require(topology, "optical_nodes", list)
    if nodes != list(range(7)):
        raise ValidationError("topology must use contiguous thesis-aligned optical nodes 0..6")
    links = _require(topology, "optical_links", list)
    if any(not isinstance(edge, list) or len(edge) != 2 or
           any(type(node) is not int or node not in nodes for node in edge) or
           edge[0] == edge[1] for edge in links):
        raise ValidationError("optical links must contain two distinct configured integer node IDs")
    normalized_links = {tuple(sorted(edge)) for edge in links}
    expected_links = {(0, 1), (1, 2), (2, 3), (3, 4), (5, 6), (2, 6)}
    if normalized_links != expected_links or len(links) != len(expected_links):
        raise ValidationError("topology must be the explicit seven-node T backbone")
    routes = _require(topology, "routes", list)
    route_pairs: set[tuple[int, int]] = set()
    for route in routes:
        if not isinstance(route, dict):
            raise ValidationError("route must be an object")
        source, destination, path = route.get("source"), route.get("destination"), route.get("path")
        if (type(source) is not int or type(destination) is not int or
                source not in nodes or destination not in nodes or
                not isinstance(path, list) or not path or
                any(type(node) is not int for node in path) or
                path[0] != source or path[-1] != destination):
            raise ValidationError("route endpoints/path are inconsistent")
        if any(tuple(sorted(pair)) not in normalized_links for pair in zip(path, path[1:])):
            raise ValidationError("route traverses an unconfigured optical link")
        route_pairs.add((source, destination))
    if route_pairs != {(0, 4), (4, 0), (5, 4), (4, 5)}:
        raise ValidationError("required aggregate routes are incomplete")
    for key in ("optical_rate_mbps", "optical_delay_ms", "receiver_access_mbps",
                "access_delay_ms", "queue_packets", "max_wavelengths",
                "burst_max_packets", "burst_timeout_ms", "max_delayed_bursts",
                "max_flow_queues"):
        _positive(_require(topology, key), key)
    for key in ("node_type", "conversion_type", "converter_count", "jet_type",
                "source_routing", "ack_dont_burst"):
        value = _require(topology, key, int)
        if value < 0:
            raise ValidationError(f"{key} must be nonnegative")
    fdl_delays = _require(topology, "fdl_delays_s", list)
    if not fdl_delays:
        raise ValidationError("fdl_delays_s must be nonempty")
    for delay in fdl_delays:
        _positive(delay, "fdl delay")
    for key in ("attacker_ingress", "receiver_egress"):
        value = _require(topology, key, int)
        if value not in nodes:
            raise ValidationError(f"{key} must identify an optical node")
    traffic = _require(config, "traffic", dict)
    count = _require(traffic, "legal_flow_count", int)
    if count <= 0:
        raise ValidationError("legal_flow_count must be positive")
    for key in ("legal_sender_ids", "legal_receiver_ids", "legal_ingress_by_flow"):
        if len(_require(traffic, key, list)) != count:
            raise ValidationError(f"{key} cardinality must equal legal_flow_count")
    for key in ("legal_sender_ids", "legal_receiver_ids", "legal_ingress_by_flow"):
        values = traffic[key]
        if any(type(value) is not int or value < 0 for value in values):
            raise ValidationError(f"{key} must contain nonnegative integer node IDs")
    for key in ("legal_packet_bytes", "tcp_window_packets", "legal_flow_id_base",
                "attacker_count", "attacker_packet_bytes", "bhp_claimed_packet_count",
                "bhp_route_class"):
        _positive(_require(traffic, key), key, allow_zero=key in {"legal_flow_id_base", "bhp_route_class"})
    for key in ("legal_access_mbps", "legal_start_stagger_s"):
        _positive(_require(traffic, key), key, allow_zero=key == "legal_start_stagger_s")
    _positive(_require(traffic, "attacker_access_mbps"), "attacker_access_mbps")
    attacker_flow_base = _require(traffic, "attacker_flow_id_base", int)
    if attacker_flow_base < 0:
        raise ValidationError("attacker_flow_id_base must be nonnegative")
    if any(ingress not in nodes for ingress in traffic["legal_ingress_by_flow"]):
        raise ValidationError("legal ingress must identify an optical node")
    start = _positive(_require(traffic, "attacker_start_s"), "attack start", allow_zero=True)
    stop = _positive(_require(traffic, "attacker_stop_s"), "attack stop")
    if not start < stop <= duration:
        raise ValidationError("attack interval must be within simulation duration")
    jitter = _positive(_require(traffic, "attack_rate_jitter"), "attack jitter", allow_zero=True)
    if jitter >= 1:
        raise ValidationError("attack jitter must be below one")
    scenarios = _require(config, "scenarios", list)
    labels = [item.get("label") for item in scenarios if isinstance(item, dict)]
    if len(labels) != len(scenarios) or len(labels) != len(set(labels)):
        raise ValidationError("scenario labels must be unique")
    if thesis_profile and (seeds != EXPECTED_SEEDS or set(labels) != EXPECTED_LABELS):
        raise ValidationError("thesis profile requires 8 seeds and S0/S1/S2_rate_limit/S2_isolation")
    by_label = {item["label"]: item for item in scenarios}
    required_semantics = {
        "S0": ("S0", False, None), "S1": ("S1", True, None),
        "S2_rate_limit": ("S2", True, "rate_limit"),
        "S2_isolation": ("S2", True, "isolation"),
    }
    for label, item in by_label.items():
        if label not in required_semantics:
            raise ValidationError(f"unexpected scenario label: {label}")
        scenario, attack, mitigation = required_semantics[label]
        if item.get("scenario") != scenario or item.get("attack") is not attack or item.get("mitigation") != mitigation:
            raise ValidationError(f"scenario semantics mismatch: {label}")
        if item.get("guard") is not True:
            raise ValidationError(f"guard must be enabled for scenario: {label}")
        profile = _require(item, "profile", dict)
        for key in ("event_capacity", "reservation_capacity", "violations", "hold_down_s", "limited_release_s"):
            _positive(_require(profile, key), f"{label}.{key}")
        for key in ("event_rate", "reservation_rate"):
            _positive(_require(profile, key), f"{label}.{key}", allow_zero=True)
    if thesis_profile:
        if by_label["S2_rate_limit"]["profile"]["event_rate"] <= 0:
            raise ValidationError("rate-limit profile must refill its event budget")
        isolation = by_label["S2_isolation"]["profile"]
        if isolation["event_rate"] != 0 or isolation["reservation_rate"] != 0:
            raise ValidationError("isolation profile must have zero refill rates")


def validate_detector_boundary() -> dict[str, Any]:
    header = OBSERVATION_HEADER.read_text(encoding="utf-8")
    match = re.search(r"struct\s+BhpObservation\s*\{(.*?)\};", header, re.S)
    if not match:
        raise ValidationError("cannot locate BhpObservation interface")
    fields = set(re.findall(r"^\s*(?:double|int|unsigned\s+long|bool)\s+(\w+)\s*;", match.group(1), re.M))
    if fields != OBSERVATION_FIELDS:
        raise ValidationError(f"detector observation fields changed: {sorted(fields)}")
    source = SRAGENT_SOURCE.read_text(encoding="utf-8")
    body_match = re.search(r"bool\s+OpSRAgent::bhp_admit_control\(.*?\n\}", source, re.S)
    if not body_match:
        raise ValidationError("cannot locate direct control admission function")
    body = body_match.group(0)
    assignments = set(re.findall(r"observation\.(\w+)\s*=", body))
    if assignments != OBSERVATION_FIELDS:
        raise ValidationError(f"observation population is incomplete or expanded: {sorted(assignments)}")
    observe_call = body.find("bhp_guard_.observe(observation)")
    recv_start = source.find("OpSRAgent::recv")
    reservation = source.find("LinkReservation_[slot_no].recv", recv_start)
    admission = source.find("bhp_admit_control(packet", recv_start)
    if min(observe_call, recv_start, admission, reservation) < 0 or admission >= reservation:
        raise ValidationError("guard is not proven before the reservation attempt")
    observation_text = match.group(1) + body
    forbidden = ("detect_delay", "attack_label", "future_label", "control_only",
                 "outcome", "oracle")
    hits = [token for token in forbidden if token in observation_text.lower()]
    # Scenario labels and attack stop times legitimately exist in workload
    # construction.  Only commands that configure the detector are inspected
    # for an illicit oracle/future channel.
    guard_configuration = "\n".join(
        line for line in SCENARIO.read_text(encoding="utf-8").lower().splitlines()
        if "bhp-guard-" in line
    )
    scenario_forbidden = ("detect_delay", "attack_label", "future_label", "outcome", "oracle", "bhp-guard-reset")
    hits.extend(token for token in scenario_forbidden if token in guard_configuration)
    if hits:
        raise ValidationError(f"oracle/future control marker in detector boundary: {sorted(set(hits))}")
    return {"observation_fields": sorted(fields), "guard_precedes_reservation": True, "oracle_markers": []}


def _read_native_log(
    path: Path,
    allowed_types: set[str],
    suffixes: dict[str, int],
    *,
    allow_empty: bool = False,
) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    if allow_empty and not text.strip():
        return []
    rows: list[dict[str, str]] = []
    schema_seen = False
    header_seen = False
    schema_header = "# BHP_AUDIT schema=1 format=tab-separated append-only"
    for number, line in enumerate(text.splitlines(), 1):
        if not line or line.startswith("#"):
            if line.startswith("# BHP_AUDIT"):
                if line != schema_header:
                    raise ValidationError(f"{path}:{number}: invalid audit schema header")
                schema_seen = True
            elif line.startswith("# type,"):
                if line[2:].split(",") != AUDIT_COLUMNS:
                    raise ValidationError(f"{path}:{number}: invalid audit column header")
                header_seen = True
            continue
        values = next(csv.reader([line]))
        if not values or values[0] not in allowed_types:
            raise ValidationError(f"{path}:{number}: unknown audit record type {values[0] if values else ''!r}")
        expected_width = len(AUDIT_COLUMNS)
        suffix = suffixes[values[0]]
        actual_width = len(values)
        if actual_width != expected_width + suffix:
            raise ValidationError(
                f"{path}:{number}: expected {expected_width + suffix} columns "
                f"for {values[0]}, got {actual_width}"
            )
        if suffix:
            if any(values[-suffix:]):
                raise ValidationError(f"{path}:{number}: native suffix must contain only empty fields")
            values = values[:-suffix]
        rows.append(dict(zip(AUDIT_COLUMNS, values)))
    if not schema_seen or not header_seen:
        raise ValidationError(f"{path}: missing or invalid audit header")
    return rows


def read_audit(path: Path) -> list[dict[str, str]]:
    return _read_native_log(path, AUDIT_TYPES, NATIVE_TRAILING_EMPTY_FIELDS)


def read_source_log(path: Path) -> list[dict[str, str]]:
    """Read the generation stream using its BHP_CREATE-only native schema."""
    return _read_native_log(
        path, SOURCE_TYPES, SOURCE_TRAILING_EMPTY_FIELDS, allow_empty=True
    )


def _time(row: dict[str, str], path: Path) -> float:
    try:
        value = float(row["event_time"])
    except (ValueError, KeyError) as exc:
        raise ValidationError(f"invalid audit event time in {path}") from exc
    if not math.isfinite(value) or value < 0:
        raise ValidationError(f"invalid audit event time in {path}")
    return value


def validate_cell(
    run_dir: Path, item: dict[str, Any], seed: int,
    input_hashes: dict[str, str], config: dict[str, Any],
) -> dict[str, Any]:
    required = ("out.tr", "stat.txt", "bhp_audit.log", "bhp_source.log", "stdout.log", "stderr.log", "run.json")
    missing = [name for name in required if not (run_dir / name).is_file()]
    if missing:
        raise ValidationError(f"{run_dir}: missing retained artifacts {missing}")
    metadata = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    if metadata.get("exit_code") != 0 or metadata.get("seed") != seed or metadata.get("label") != item["label"]:
        raise ValidationError(f"{run_dir}: run metadata/exit status mismatch")
    if metadata.get("input_sha256") != input_hashes:
        raise ValidationError(f"{run_dir}: input hash snapshot mismatch")
    hashes = metadata.get("artifact_sha256", {})
    for name in required[:-1]:
        if hashes.get(name) != sha256(run_dir / name):
            raise ValidationError(f"{run_dir}: retained artifact hash mismatch: {name}")
    stdout = (run_dir / "stdout.log").read_text(encoding="utf-8")
    if "RUN_COMPLETE " not in stdout or f"scenario={item['scenario']}" not in stdout:
        raise ValidationError(f"{run_dir}: missing successful native NS completion marker")
    source_path, audit_path = run_dir / "bhp_source.log", run_dir / "bhp_audit.log"
    creates = read_source_log(source_path)
    audit = read_audit(audit_path)
    source_uids: set[str] = set()
    for create in creates:
        uid = create.get("packet_uid", "")
        if not uid or uid in source_uids:
            raise ValidationError(f"{run_dir}: duplicate/empty BHP_CREATE UID {uid!r}")
        source_uids.add(uid)

    by_uid: dict[str, dict[str, list[dict[str, str]]]] = defaultdict(lambda: defaultdict(list))
    positions: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
    for index, row in enumerate(audit):
        uid = row["packet_uid"]
        if not uid:
            raise ValidationError(f"{run_dir}: audit record has empty packet UID")
        if uid not in source_uids:
            raise ValidationError(f"{run_dir}: audit UID {uid} has no BHP_CREATE provenance")
        by_uid[uid][row["type"]].append(row)
        positions[uid][row["type"]].append(index)

    if not item["attack"] and creates:
        raise ValidationError(f"{run_dir}: S0 emitted attack BHPs")
    if item["attack"] and not creates:
        raise ValidationError(f"{run_dir}: attack cell emitted no direct BHPs")

    actions: dict[str, int] = defaultdict(int)
    seen: set[str] = set()
    traced_uids: set[int] = set()
    delivered_uids: set[int] = set()
    blocked_uids: set[int] = set()
    for create in creates:
        uid = create["packet_uid"]
        seen.add(uid)
        events = by_uid.get(uid, {})
        chain = []
        for kind in ("OBSERVE", "DECIDE", "ACT"):
            rows = events.get(kind, [])
            if len(rows) != 1:
                raise ValidationError(f"{run_dir}: UID {uid} has {len(rows)} {kind} records")
            chain.append(rows[0])
        order = [positions[uid][kind][0] for kind in ("OBSERVE", "DECIDE", "ACT")]
        if order != sorted(order) or len(set(order)) != 3:
            raise ValidationError(f"{run_dir}: non-causal record order for UID {uid}: {order}")
        times = [_time(create, source_path)] + [_time(row, audit_path) for row in chain]
        if times != sorted(times):
            raise ValidationError(f"{run_dir}: non-causal timestamps for UID {uid}: {times}")
        observe, decide, act = chain
        for name in ("ingress", "claimed_bytes", "reservation_cost"):
            if create[name] != observe[name]:
                raise ValidationError(f"{run_dir}: CREATE/OBSERVE {name} mismatch for UID {uid}")
        for name in (
            "ingress", "destination", "route_class", "claimed_bytes",
            "claimed_packets", "reservation_cost",
        ):
            if decide[name] != observe[name] or act[name] != observe[name]:
                raise ValidationError(f"{run_dir}: OBSERVE/DECIDE/ACT {name} mismatch for UID {uid}")
        if any(observe.get(name, "") for name in AUDIT_COLUMNS[11:]):
            raise ValidationError(f"{run_dir}: OBSERVE row contains decision/outcome fields for UID {uid}")
        detections = events.get("DETECT", [])
        if len(detections) > 1:
            raise ValidationError(f"{run_dir}: UID {uid} has multiple DETECT records")
        if detections:
            detect_position = positions[uid]["DETECT"][0]
            if not order[0] < detect_position < order[1]:
                raise ValidationError(f"{run_dir}: non-causal DETECT order for UID {uid}")
            detect_time = _time(detections[0], audit_path)
            if not times[1] <= detect_time <= times[2]:
                raise ValidationError(f"{run_dir}: non-causal DETECT timestamp for UID {uid}")
        if decide["action"] != act["action"] or decide["decision_time"] != act["decision_time"]:
            raise ValidationError(f"{run_dir}: DECIDE/ACT mismatch for UID {uid}")
        if act["action"] not in {"ALLOW", "RELEASE", "DROP_OVER_PROFILE", "QUARANTINE_INGRESS"}:
            raise ValidationError(f"{run_dir}: unsupported actuator action {act['action']!r}")
        actions[act["action"]] += 1
        outcomes = events.get("OUTCOME", [])
        admitted = act["action"] in {"ALLOW", "RELEASE"}
        if admitted:
            if act["reservation_attempted"] != "1" or act["cleanup_succeeded"] != "1":
                raise ValidationError(f"{run_dir}: admitted UID {uid} has invalid ACT semantics")
            if len(outcomes) != 1:
                raise ValidationError(
                    f"{run_dir}: admitted UID {uid} has {len(outcomes)} OUTCOME records"
                )
            outcome = outcomes[0]
            if positions[uid]["OUTCOME"][0] <= order[2]:
                raise ValidationError(f"{run_dir}: OUTCOME precedes ACT for UID {uid}")
            if _time(outcome, audit_path) < times[-1]:
                raise ValidationError(f"{run_dir}: OUTCOME time precedes ACT for UID {uid}")
            if outcome["reservation_result"] not in {"ACCEPTED", "REJECTED"}:
                raise ValidationError(
                    f"{run_dir}: invalid scheduler outcome for UID {uid}: "
                    f"{outcome['reservation_result']!r}"
                )
            if outcome["ingress"] != create["ingress"]:
                raise ValidationError(f"{run_dir}: OUTCOME ingress mismatch for UID {uid}")
            expected_control_result = (
                "DELIVERED_TO_EGRESS"
                if outcome["reservation_result"] == "ACCEPTED"
                else "RESERVATION_REJECTED"
            )
            if outcome["control_result"] != expected_control_result or outcome["data_result"] != "ABSENT":
                raise ValidationError(f"{run_dir}: direct-BHP lifecycle outcome mismatch for UID {uid}")
            if outcome["right_censored"] != "0":
                raise ValidationError(f"{run_dir}: completed direct-BHP UID {uid} is right-censored")
            numeric_uid = int(uid)
            traced_uids.add(numeric_uid)
            if outcome["reservation_result"] == "ACCEPTED":
                delivered_uids.add(numeric_uid)
        else:
            if act["reservation_attempted"] != "0" or act["cleanup_succeeded"] != "1":
                raise ValidationError(f"{run_dir}: blocked UID {uid} has invalid ACT semantics")
            if outcomes:
                raise ValidationError(f"{run_dir}: blocked UID {uid} unexpectedly reached scheduler")
            blocked_uids.add(int(uid))

    try:
        trace_metrics = TRACE.parse_path(
            run_dir / "out.tr",
            direct_control_uids=traced_uids,
            delivered_direct_control_uids=delivered_uids,
            forbidden_direct_control_uids=blocked_uids,
        )
    except (OSError, TRACE.TraceFormatError) as exc:
        raise ValidationError(f"{run_dir}: invalid retained network trace: {exc}") from exc
    tcp = trace_metrics["transport"]["tcp"]
    traffic = config["traffic"]
    expected_flows = list(range(
        int(traffic["legal_flow_id_base"]),
        int(traffic["legal_flow_id_base"]) + int(traffic["legal_flow_count"]),
    ))
    if tcp["flow_ids"] != expected_flows or tcp["legal_receive_packets"] <= 0:
        raise ValidationError(
            f"{run_dir}: legal TCP outcome is missing configured endpoint flows"
        )
    network = {
        "legal_tcp_receive_packets": tcp["legal_receive_packets"],
        "legal_tcp_receive_bytes": tcp["legal_receive_bytes"],
        "legal_tcp_per_flow": tcp["per_flow"],
        "legal_ack_receive_packets": trace_metrics["transport"]["ack"]["legal_receive_packets"],
        "optical_burst_pairs": trace_metrics["optical"]["burst_pairs"],
        "optical_successful_link_reservations": trace_metrics["optical"]["control_link_reservations_succeeded"],
        "optical_explicit_data_drops": trace_metrics["optical"]["data_bursts_explicitly_dropped"],
    }
    if not item["attack"]:
        return {"created": 0, "causal_chains": 0, "actions": {}, "network": network}
    label = item["label"]
    if label == "S1" and set(actions) - {"ALLOW", "RELEASE"}:
        raise ValidationError(f"{run_dir}: S1 permissive monitor mitigated direct BHPs")
    if label == "S2_rate_limit" and not ({"DROP_OVER_PROFILE", "QUARANTINE_INGRESS"} & set(actions)):
        raise ValidationError(f"{run_dir}: rate-limit cell exercised no actuator")
    if label == "S2_isolation" and "QUARANTINE_INGRESS" not in actions:
        raise ValidationError(f"{run_dir}: isolation cell never quarantined ingress")
    return {
        "created": len(creates), "causal_chains": len(seen),
        "actions": dict(sorted(actions.items())), "network": network,
    }


def validate_network_outcomes(cell_reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Require an observed attack effect and recovery for every complete seed quartet."""
    grouped: dict[int, dict[str, dict[str, Any]]] = defaultdict(dict)
    for key, report in cell_reports.items():
        seed_text, label = key.split("/", 1)
        grouped[int(seed_text.removeprefix("seed_"))][label] = report
    required = EXPECTED_LABELS
    outcomes: dict[str, Any] = {}
    for seed, cells in sorted(grouped.items()):
        if set(cells) != required:
            continue
        byte_counts = {
            label: cells[label]["network"]["legal_tcp_receive_bytes"]
            for label in sorted(required)
        }
        baseline, attacked = byte_counts["S0"], byte_counts["S1"]
        if not 0 < attacked < baseline:
            raise ValidationError(
                f"seed {seed}: S1 did not reduce legal TCP bytes relative to S0"
            )
        if attacked / baseline > 0.90:
            raise ValidationError(
                f"seed {seed}: S1 network effect is below the declared 10% gate"
            )
        for label in ("S2_rate_limit", "S2_isolation"):
            recovered = byte_counts[label]
            if recovered <= attacked:
                raise ValidationError(f"seed {seed}: {label} did not improve over S1")
            if recovered > baseline * 1.01:
                raise ValidationError(f"seed {seed}: {label} exceeds S0 by more than 1%")
            for flow_id, flow in cells[label]["network"]["legal_tcp_per_flow"].items():
                attacked_flow = cells["S1"]["network"]["legal_tcp_per_flow"][flow_id]["legal_receive_bytes"]
                if flow["legal_receive_bytes"] < attacked_flow:
                    raise ValidationError(
                        f"seed {seed}: {label} harms legal flow {flow_id} relative to S1"
                    )
        s1_accepted = cells["S1"]["actions"].get("ALLOW", 0) + cells["S1"]["actions"].get("RELEASE", 0)
        for label in ("S2_rate_limit", "S2_isolation"):
            admitted = cells[label]["actions"].get("ALLOW", 0) + cells[label]["actions"].get("RELEASE", 0)
            if admitted >= s1_accepted:
                raise ValidationError(f"seed {seed}: {label} did not reduce admitted direct BHPs")
        outcomes[str(seed)] = {
            "legal_tcp_receive_bytes": byte_counts,
            "s1_remaining_fraction_of_s0": attacked / baseline,
            "rate_limit_recovery_fraction_of_s0": byte_counts["S2_rate_limit"] / baseline,
            "isolation_recovery_fraction_of_s0": byte_counts["S2_isolation"] / baseline,
        }
    return {"complete_seed_quartets": len(outcomes), "per_seed": outcomes}


def build_verified_provenance(
    root: Path,
    manifest_path: Path,
    completion_path: Path,
    snapshot: Path,
    expected_pairs: set[tuple[int, str]],
    input_hashes: dict[str, str],
) -> dict[str, Any]:
    """Export the exact hash chain already verified by the fail-closed validator."""
    cells: dict[str, Any] = {}
    for seed, label in sorted(expected_pairs):
        run_dir = root / f"seed_{seed}" / label
        run_json = run_dir / "run.json"
        metadata = json.loads(run_json.read_text(encoding="utf-8"))
        cells[f"seed_{seed}/{label}"] = {
            "run_json_sha256": sha256(run_json),
            "artifact_sha256": dict(sorted(metadata["artifact_sha256"].items())),
        }
    return {
        "validation_engine_sha256": sha256(Path(__file__).resolve()),
        "matrix_manifest_sha256": sha256(manifest_path),
        "completion_sha256": sha256(completion_path),
        "experiment_config_snapshot_sha256": sha256(snapshot),
        "verified_input_sha256": dict(sorted(input_hashes.items())),
        "verified_cells": cells,
    }


def validate_results(config: dict[str, Any], root: Path) -> dict[str, Any]:
    manifest_path = root / "matrix_manifest.json"
    completion_path = root / "completion.json"
    if not manifest_path.is_file() or not completion_path.is_file():
        raise ValidationError("results lack matrix_manifest.json or completion.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    completion = json.loads(completion_path.read_text(encoding="utf-8"))
    snapshot = root / "experiment_config.snapshot.json"
    if not snapshot.is_file():
        raise ValidationError("results lack experiment_config.snapshot.json")
    if json.loads(snapshot.read_text(encoding="utf-8")) != config:
        raise ValidationError("config does not match retained experiment snapshot")
    selected = manifest.get("selected_cells")
    if not isinstance(selected, list) or not selected:
        raise ValidationError("manifest has no selected-cell declaration")
    if completion.get("successful_cells") != len(selected) or completion.get("failed_cells") != 0:
        raise ValidationError("not all expected selected cells succeeded")
    if manifest.get("expected_selected_cells") != len(selected) or completion.get("expected_selected_cells") != len(selected):
        raise ValidationError("selected-cell count metadata mismatch")
    if completion.get("complete") is not True:
        raise ValidationError("completion metadata does not claim selected-cell completion")
    items = {item["label"]: item for item in config["scenarios"]}
    seeds = set(config["seeds"])
    expected_pairs: set[tuple[int, str]] = set()
    for cell in selected:
        pair = (cell.get("seed"), cell.get("label"))
        if pair[0] not in seeds or pair[1] not in items or pair in expected_pairs:
            raise ValidationError(f"invalid/duplicate selected cell: {cell}")
        expected_pairs.add(pair)
    actual_pairs = set()
    for run_json in root.glob("seed_*/*/run.json"):
        metadata = json.loads(run_json.read_text(encoding="utf-8"))
        actual_pairs.add((metadata.get("seed"), metadata.get("label")))
    if actual_pairs != expected_pairs:
        raise ValidationError(f"expected/actual cell mismatch: expected={sorted(expected_pairs)} actual={sorted(actual_pairs)}")
    input_hashes = manifest.get("input_sha256")
    if not isinstance(input_hashes, dict) or not input_hashes:
        raise ValidationError("manifest lacks input hashes")
    snapshot_hash = sha256(snapshot)
    if (manifest.get("config_sha256") != snapshot_hash or
            input_hashes.get("experiment_config.snapshot.json") != snapshot_hash):
        raise ValidationError("retained config snapshot hash mismatch")
    cell_reports = {}
    for seed, label in sorted(expected_pairs):
        cell_reports[f"seed_{seed}/{label}"] = validate_cell(
            root / f"seed_{seed}" / label, items[label], seed, input_hashes, config
        )
    network_outcomes = validate_network_outcomes(cell_reports)
    all_pairs = {(seed, item["label"]) for seed in config["seeds"] for item in config["scenarios"]}
    full = expected_pairs == all_pairs
    if manifest.get("full_matrix_requested") is not full:
        raise ValidationError("full-matrix claim does not match selected cells")
    if completion.get("full_matrix_complete") is not full:
        raise ValidationError("completion full-matrix claim does not match selected cells")
    provenance = build_verified_provenance(
        root, manifest_path, completion_path, snapshot, expected_pairs, input_hashes
    )
    return {
        "schema": "nobs-direct-bhp-validation-v2", "valid": True,
        "selected_cells_complete": True, "full_matrix_complete": full,
        "expected_selected_cells": len(expected_pairs), "detector_boundary": validate_detector_boundary(),
        "provenance": provenance,
        "hashes": {
            "validation_engine": provenance["validation_engine_sha256"],
            "matrix_manifest.json": provenance["matrix_manifest_sha256"],
            "completion.json": provenance["completion_sha256"],
            "experiment_config.snapshot.json": provenance["experiment_config_snapshot_sha256"],
        },
        "cells": cell_reports, "network_outcome_gate": network_outcomes,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(HERE / "config.json"))
    parser.add_argument("--results")
    parser.add_argument("--allow-nonthesis-profile", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        config = json.loads(Path(args.config).read_text(encoding="utf-8"))
        validate_config(config, thesis_profile=not args.allow_nonthesis_profile)
        report: dict[str, Any] = {
            "schema": "nobs-direct-bhp-validation-v1", "valid": True,
            "config_valid": True, "detector_boundary": validate_detector_boundary(),
        }
        if args.results:
            report = validate_results(config, Path(args.results).resolve())
        text = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.output:
            Path(args.output).write_text(text, encoding="utf-8")
        else:
            sys.stdout.write(text)
        return 0
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        sys.stderr.write(f"validation failed: {exc}\n")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
