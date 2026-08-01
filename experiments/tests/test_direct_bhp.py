#!/usr/bin/env python3
"""Focused fail-closed tests for the native direct-BHP harness."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

EXPERIMENTS = Path(__file__).resolve().parents[1]
DIRECT = EXPERIMENTS / "direct_bhp"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


validator = load_module("direct_bhp_validator", DIRECT / "validator.py")
sys.modules["validator"] = validator
runner = load_module("direct_bhp_runner", DIRECT / "runner.py")


def hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def header() -> str:
    return (
        "# BHP_AUDIT schema=1 format=tab-separated append-only\n"
        "# " + ",".join(validator.AUDIT_COLUMNS) + "\n"
    )


def native_row(record_type: str, values: dict[str, object], suffix: int) -> str:
    row = [str(values.get(column, "")) for column in validator.AUDIT_COLUMNS]
    row.extend([""] * suffix)
    output = []
    stream = _ListWriter(output)
    csv.writer(stream, lineterminator="").writerow(row)
    return "".join(output) + "\n"


class _ListWriter:
    def __init__(self, target: list[str]):
        self.target = target

    def write(self, value: str) -> int:
        self.target.append(value)
        return len(value)


class DirectBhpConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads((DIRECT / "config.json").read_text(encoding="utf-8"))

    def test_thesis_schema_seeds_labels_and_semantics(self):
        validator.validate_config(self.config)
        self.assertEqual(self.config["schema"], "nobs-direct-bhp-experiment-v1")
        self.assertEqual(self.config["seeds"], [101, 202, 303, 404, 505, 606, 707, 808])
        self.assertEqual(
            {item["label"] for item in self.config["scenarios"]},
            {"S0", "S1", "S2_rate_limit", "S2_isolation"},
        )

    def test_route_node_ids_must_be_exact_integers_and_paths_nonempty(self):
        bad = json.loads(json.dumps(self.config))
        bad["topology"]["routes"][0]["path"][1] = 1.0
        with self.assertRaisesRegex(validator.ValidationError, "endpoints/path"):
            validator.validate_config(bad)
        bad = json.loads(json.dumps(self.config))
        bad["topology"]["routes"][0]["path"] = []
        with self.assertRaisesRegex(validator.ValidationError, "endpoints/path"):
            validator.validate_config(bad)


class NativeLogTests(unittest.TestCase):
    def _parse(self, text: str):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "audit.log"
            path.write_text(text, encoding="utf-8")
            return validator.read_audit(path)

    def test_accepts_only_record_specific_empty_suffix(self):
        values = {"type": "OBSERVE", "event_time": 1, "packet_uid": 9}
        rows = self._parse(header() + native_row("OBSERVE", values, 2))
        self.assertEqual(rows[0]["packet_uid"], "9")

        with self.assertRaises(validator.ValidationError):
            self._parse(header() + native_row("OBSERVE", values, 1))
        with self.assertRaises(validator.ValidationError):
            self._parse(header() + native_row("OBSERVE", values, 3))

    def test_rejects_nonempty_native_suffix(self):
        row = ["" for _ in range(len(validator.AUDIT_COLUMNS) + 2)]
        row[0:3] = ["OBSERVE", "1", "9"]
        row[-1] = "not-empty"
        with self.assertRaisesRegex(validator.ValidationError, "suffix"):
            self._parse(header() + ",".join(row) + "\n")

    def test_source_log_has_separate_bhp_create_only_contract(self):
        values = {"type": "BHP_CREATE", "event_time": 1, "packet_uid": 9}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.log"
            path.write_text(header() + native_row("BHP_CREATE", values, 0), encoding="utf-8")
            self.assertEqual(validator.read_source_log(path)[0]["type"], "BHP_CREATE")
            with self.assertRaises(validator.ValidationError):
                validator.read_audit(path)


class DetectorBoundaryTests(unittest.TestCase):
    def test_current_native_boundary_is_valid(self):
        result = validator.validate_detector_boundary()
        self.assertTrue(result["guard_precedes_reservation"])
        self.assertEqual(result["oracle_markers"], [])

    def test_explicit_oracle_detector_configuration_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            scenario = Path(tmp) / "scenario.tcl"
            scenario.write_text("$guard bhp-guard-oracle $future_label\n", encoding="utf-8")
            with mock.patch.object(validator, "SCENARIO", scenario):
                with self.assertRaisesRegex(validator.ValidationError, "oracle/future"):
                    validator.validate_detector_boundary()


class CausalValidationTests(unittest.TestCase):
    def _cell(self, root: Path, audit_rows: list[str]) -> tuple[dict[str, object], dict[str, str]]:
        source = native_row(
            "BHP_CREATE",
            {"type": "BHP_CREATE", "event_time": 1, "packet_uid": 42,
             "ingress": 5, "claimed_bytes": 1000, "reservation_cost": "8e-06"},
            0,
        )
        files = {
            "out.tr": "",
            "stat.txt": "",
            "bhp_audit.log": header() + "".join(audit_rows),
            "bhp_source.log": header() + source,
            "stdout.log": "RUN_COMPLETE scenario=S1 seed=101\n",
            "stderr.log": "",
        }
        for name, text in files.items():
            (root / name).write_text(text, encoding="utf-8")
        input_hashes = {"test-input": "abc"}
        metadata = {
            "exit_code": 0,
            "seed": 101,
            "label": "S1",
            "input_sha256": input_hashes,
            "artifact_sha256": {name: hash_file(root / name) for name in files},
        }
        (root / "run.json").write_text(json.dumps(metadata), encoding="utf-8")
        item = {"label": "S1", "scenario": "S1", "attack": True}
        config = {"traffic": {"legal_flow_id_base": 100, "legal_flow_count": 2}}
        return item, input_hashes, config

    @staticmethod
    def _chain(order=("OBSERVE", "DECIDE", "ACT")) -> list[str]:
        common = {
            "event_time": 1,
            "packet_uid": 42,
            "ingress": 5,
            "destination": 4,
            "route_class": 5,
            "claimed_bytes": 1000,
            "claimed_packets": 1,
            "reservation_cost": "8e-06",
        }
        values = {
            "OBSERVE": {**common, "type": "OBSERVE", "state_before": "NORMAL"},
            "DECIDE": {**common, "type": "DECIDE", "state_before": "NORMAL",
                       "state_after": "NORMAL", "action": "ALLOW", "reason": "NONE",
                       "detection_time": -1, "decision_time": 1},
            "ACT": {**common, "type": "ACT", "state_before": "NORMAL",
                    "state_after": "NORMAL", "action": "ALLOW", "reason": "NONE",
                    "detection_time": -1, "decision_time": 1, "action_time": 1,
                    "reservation_attempted": 1, "cleanup_succeeded": 1},
            "OUTCOME": {"type": "OUTCOME", "event_time": 1, "packet_uid": 42,
                        "ingress": 5, "destination": -1, "route_class": -1,
                        "claimed_bytes": 0, "claimed_packets": 0,
                        "reservation_cost": 0, "reservation_result": "ACCEPTED",
                        "control_result": "DELIVERED_TO_EGRESS", "data_result": "ABSENT",
                        "right_censored": 0},
        }
        rows = [native_row(kind, values[kind], validator.NATIVE_TRAILING_EMPTY_FIELDS[kind]) for kind in order]
        if "ACT" in order:
            rows.append(native_row("OUTCOME", values["OUTCOME"], 0))
        return rows

    def test_accepts_complete_create_observe_decide_act_chain(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            item, hashes, config = self._cell(root, self._chain())
            metrics = {
                "transport": {
                    "tcp": {"flow_ids": [100, 101], "legal_receive_packets": 2,
                            "legal_receive_bytes": 2080,
                            "per_flow": {"100": {"legal_receive_packets": 1, "legal_receive_bytes": 1040},
                                         "101": {"legal_receive_packets": 1, "legal_receive_bytes": 1040}}},
                    "ack": {"legal_receive_packets": 2},
                },
                "optical": {"burst_pairs": 1, "control_link_reservations_succeeded": 1,
                            "data_bursts_explicitly_dropped": 0},
            }
            with mock.patch.object(validator.TRACE, "parse_path", return_value=metrics) as parse_path:
                report = validator.validate_cell(root, item, 101, hashes, config)
            parse_path.assert_called_once_with(
                root / "out.tr",
                direct_control_uids={42},
                delivered_direct_control_uids={42},
                forbidden_direct_control_uids=set(),
            )
            self.assertEqual(report["causal_chains"], 1)
            self.assertEqual(report["actions"], {"ALLOW": 1})

    def test_rejects_noncausal_record_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            item, hashes, config = self._cell(root, self._chain(("DECIDE", "OBSERVE", "ACT")))
            metrics = {
                "transport": {
                    "tcp": {"flow_ids": [100, 101], "legal_receive_packets": 2,
                            "legal_receive_bytes": 2080, "per_flow": {}},
                    "ack": {"legal_receive_packets": 2},
                },
                "optical": {"burst_pairs": 1, "control_link_reservations_succeeded": 1,
                            "data_bursts_explicitly_dropped": 0},
            }
            with mock.patch.object(validator.TRACE, "parse_path", return_value=metrics):
                with self.assertRaisesRegex(validator.ValidationError, "non-causal record order"):
                    validator.validate_cell(root, item, 101, hashes, config)

    def test_rejected_lifecycle_uses_reservation_rejected_and_needs_no_delivery(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rows = self._chain()
            rejected = {
                "type": "OUTCOME", "event_time": 1, "packet_uid": 42,
                "ingress": 5, "destination": -1, "route_class": -1,
                "claimed_bytes": 0, "claimed_packets": 0,
                "reservation_cost": 0, "reservation_result": "REJECTED",
                "control_result": "RESERVATION_REJECTED", "data_result": "ABSENT",
                "right_censored": 0,
            }
            rows[-1] = native_row("OUTCOME", rejected, 0)
            item, hashes, config = self._cell(root, rows)
            metrics = {
                "transport": {
                    "tcp": {"flow_ids": [100, 101], "legal_receive_packets": 2,
                            "legal_receive_bytes": 2080, "per_flow": {}},
                    "ack": {"legal_receive_packets": 2},
                },
                "optical": {"burst_pairs": 0, "control_link_reservations_succeeded": 0,
                            "data_bursts_explicitly_dropped": 0},
            }
            with mock.patch.object(validator.TRACE, "parse_path", return_value=metrics) as parse_path:
                validator.validate_cell(root, item, 101, hashes, config)
            parse_path.assert_called_once_with(
                root / "out.tr",
                direct_control_uids={42},
                delivered_direct_control_uids=set(),
                forbidden_direct_control_uids=set(),
            )

    def test_rejects_audit_uid_without_source_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rows = self._chain()
            extra = {
                "type": "OUTCOME", "event_time": 1, "packet_uid": 99,
                "ingress": 5, "reservation_result": "REJECTED",
                "control_result": "RESERVATION_REJECTED", "data_result": "ABSENT",
                "right_censored": 0,
            }
            rows.append(native_row("OUTCOME", extra, 0))
            item, hashes, config = self._cell(root, rows)
            with self.assertRaisesRegex(validator.ValidationError, "no BHP_CREATE provenance"):
                validator.validate_cell(root, item, 101, hashes, config)

    def test_rejects_duplicate_outcome_for_source_uid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rows = self._chain()
            rows.append(rows[-1])
            item, hashes, config = self._cell(root, rows)
            with self.assertRaisesRegex(validator.ValidationError, "has 2 OUTCOME records"):
                validator.validate_cell(root, item, 101, hashes, config)

    def test_rejects_contradictory_act_semantics(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rows = self._chain()
            common = {
                "type": "ACT", "event_time": 1, "packet_uid": 42,
                "ingress": 5, "destination": 4, "route_class": 5,
                "claimed_bytes": 1000, "claimed_packets": 1,
                "reservation_cost": "8e-06", "state_before": "NORMAL",
                "state_after": "NORMAL", "action": "ALLOW", "reason": "NONE",
                "detection_time": -1, "decision_time": 1, "action_time": 1,
                "reservation_attempted": 0, "cleanup_succeeded": 1,
            }
            rows[2] = native_row("ACT", common, 0)
            item, hashes, config = self._cell(root, rows)
            with self.assertRaisesRegex(validator.ValidationError, "invalid ACT semantics"):
                validator.validate_cell(root, item, 101, hashes, config)


class TraceDirectControlTests(unittest.TestCase):
    @staticmethod
    def _event(uid: int, kind: str = "+", to_node: int = 1):
        return validator.TRACE.Event(
            kind=kind, time=1.0, from_node=0, to_node=to_node,
            packet_type="OP_BURST", size_bytes=40, flags="-------",
            flow_id=0, source=validator.TRACE.Address(0, 0),
            destination=validator.TRACE.Address(4, 0), sequence_number=-1,
            packet_uid=uid, line_number=1,
        )

    def test_first_hop_rejection_can_have_no_trace_event(self):
        result = validator.TRACE.analyze([], direct_control_uids={42})
        self.assertEqual(result["trace"]["lines"], 0)

    def test_downstream_rejection_can_have_partial_trace(self):
        result = validator.TRACE.analyze(
            [self._event(42)], direct_control_uids={42}
        )
        self.assertEqual(result["trace"]["lines"], 1)

    def test_blocked_direct_control_is_forbidden_in_trace(self):
        with self.assertRaisesRegex(validator.TRACE.TraceFormatError, "blocked direct-BHP"):
            validator.TRACE.analyze(
                [self._event(42)], forbidden_direct_control_uids={42}
            )

    def test_accepted_direct_control_requires_destination_receive(self):
        with self.assertRaisesRegex(validator.TRACE.TraceFormatError, "not delivered"):
            validator.TRACE.analyze(
                [self._event(42)], direct_control_uids={42},
                delivered_direct_control_uids={42},
            )

    def test_delivered_set_must_be_subset_of_direct_set(self):
        with self.assertRaisesRegex(validator.TRACE.TraceFormatError, "not a subset"):
            validator.TRACE.analyze([], delivered_direct_control_uids={42})


class ValidationProvenanceTests(unittest.TestCase):
    def test_build_verified_provenance_exports_manifest_inputs_and_cell_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "matrix_manifest.json"
            completion = root / "completion.json"
            snapshot = root / "experiment_config.snapshot.json"
            manifest.write_text('{"schema":"matrix"}\n', encoding="utf-8")
            completion.write_text('{"complete":true}\n', encoding="utf-8")
            snapshot.write_text('{"schema":"config"}\n', encoding="utf-8")
            run_dir = root / "seed_101" / "S0"
            run_dir.mkdir(parents=True)
            metadata = {"artifact_sha256": {"out.tr": "abc", "stat.txt": "def"}}
            run_json = run_dir / "run.json"
            run_json.write_text(json.dumps(metadata) + "\n", encoding="utf-8")

            result = validator.build_verified_provenance(
                root, manifest, completion, snapshot, {(101, "S0")}, {"ns": "123"}
            )

            self.assertEqual(result["validation_engine_sha256"], hash_file(DIRECT / "validator.py"))
            self.assertEqual(result["matrix_manifest_sha256"], hash_file(manifest))
            self.assertEqual(result["completion_sha256"], hash_file(completion))
            self.assertEqual(result["experiment_config_snapshot_sha256"], hash_file(snapshot))
            self.assertEqual(result["verified_input_sha256"], {"ns": "123"})
            self.assertEqual(
                result["verified_cells"]["seed_101/S0"]["artifact_sha256"],
                metadata["artifact_sha256"],
            )
            self.assertEqual(
                result["verified_cells"]["seed_101/S0"]["run_json_sha256"],
                hash_file(run_json),
            )


class NativeOwnershipRegressionTests(unittest.TestCase):
    def test_null_destination_detaches_and_frees_phantom_and_control(self):
        source = (EXPERIMENTS.parent / "nobs/optical/op-classifier.cc").read_text(
            encoding="utf-8"
        )
        self.assertIn("Packet* phantom = burst->burst;", source)
        self.assertIn("burst->burst = 0;", source)
        self.assertIn("Packet::free(phantom);", source)
        self.assertIn("Packet::free(p);", source)

    def test_shared_audit_writer_suppresses_duplicate_headers(self):
        source = (EXPERIMENTS.parent / "nobs/optical/op-bhp-audit.cc").read_text(
            encoding="utf-8"
        )
        self.assertIn("fseek(stream_, 0, SEEK_END)", source)
        self.assertIn("header_written_ = ftell(stream_) > 0;", source)


@unittest.skipUnless(runner.NS.is_file() and os.access(runner.NS, os.X_OK), "native NS binary unavailable")
class RunnerSmokeTests(unittest.TestCase):
    def test_single_native_cell_retains_and_hashes_all_artifacts(self):
        with tempfile.TemporaryDirectory(prefix="direct-bhp-test-") as tmp:
            output = Path(tmp) / "results"
            completed = subprocess.run(
                [sys.executable, str(DIRECT / "runner.py"), "--out", str(output),
                 "--seed", "101", "--label", "S0"],
                cwd=DIRECT, text=True, capture_output=True, timeout=90, check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            run_dir = output / "seed_101" / "S0"
            metadata = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            for name in runner.ARTIFACTS:
                self.assertTrue((run_dir / name).is_file(), name)
                self.assertEqual(metadata["artifact_sha256"][name], hash_file(run_dir / name))
            validation = json.loads((output / "validation.json").read_text(encoding="utf-8"))
            self.assertTrue(validation["selected_cells_complete"])
            self.assertFalse(validation["full_matrix_complete"])


if __name__ == "__main__":
    unittest.main()
