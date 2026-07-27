import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import tempfile
import unittest


HERE = pathlib.Path(__file__).resolve().parents[1]
NOBS_ROOT = HERE.parent
SCRIPT = HERE / "scenario.tcl"
RUNNER = HERE / "run_matrix.py"
CONFIG = HERE / "configs" / "full_400_rate40_8seed.json"
MANIFEST = HERE / "manifest.json"
NS = NOBS_ROOT / "build/ns-allinone-2.35/ns-2.35/ns"


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ScenarioConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SCRIPT.read_text(encoding="utf-8")
        cls.config = json.loads(CONFIG.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_manifest_marks_reconstruction_and_no_python_simulator(self):
        self.assertEqual(self.manifest["status"], "reconstructed")
        self.assertFalse(self.manifest["simulator"]["python_simulator_used"])
        self.assertFalse(self.manifest["simulator"]["binary_modified_for_experiment"])

    def test_versioned_config_contains_complete_experiment_design(self):
        self.assertEqual(self.config["schema"], "nobs-matrix-experiment-v1")
        self.assertEqual(len(self.config["seeds"]), 8)
        self.assertEqual(
            {item["label"] for item in self.config["scenarios"]},
            {"S0", "S1", "S2_rate_limit", "S2_isolation"},
        )
        for section in ("simulation", "traffic", "network", "mitigation"):
            self.assertIn(section, self.config)
        network = self.config["network"]
        self.assertEqual(network["topology_profile"], "nobs-explicit-topology-v1")
        self.assertEqual(len(network["optical_links"]), 6)
        self.assertEqual(len(network["optical_routes"]), 4)

    def test_cli_and_scenario_contract_is_explicit(self):
        for name in ("scenario", "seed", "attack_rate", "sim_time", "mitigation"):
            self.assertIn(f"set {name} [lindex $argv", self.text)
        self.assertIn("S2 requires mitigation=rate_limit or isolation", self.text)

    def test_tcl_is_fail_closed_and_topology_is_config_driven(self):
        self.assertIn("missing required experiment parameter", self.text)
        self.assertIn("NOBS_OPTICAL_NODES", self.text)
        self.assertIn("NOBS_OPTICAL_LINKS", self.text)
        self.assertIn("NOBS_OPTICAL_ROUTES", self.text)
        self.assertIn("foreach encoded_link $optical_links", self.text)
        self.assertIn("foreach encoded_route $optical_routes", self.text)
        self.assertIn("$ns op_src_rting [env_nonnegative_int NOBS_SOURCE_ROUTING]", self.text)
        self.assertNotIn("env_positive_int NOBS_LEGAL_FLOWS 2", self.text)
        self.assertNotIn("env_positive_double NOBS_OPTICAL_RATE_MBPS 1000.0", self.text)
        self.assertNotIn('install_route n 0 4 "0 1 2 3 4"', self.text)
        self.assertNotIn("optical_duplex $ns $n(0) $n(1)", self.text)
        self.assertNotIn("simulator.py", self.text)

    def test_traffic_and_mitigation_are_config_driven(self):
        required_env = (
            "NOBS_LEGAL_FLOWS", "NOBS_LEGAL_PACKET_BYTES", "NOBS_ATTACKER_COUNT",
            "NOBS_ATTACK_START_S", "NOBS_TCP_WINDOW_PACKETS",
            "NOBS_DETECTION_DELAY_S", "NOBS_RATE_LIMIT_CIR_MBPS",
            "NOBS_TBF_BUCKET_BITS", "NOBS_TBF_QUEUE_PACKETS",
        )
        for name in required_env:
            self.assertIn(name, self.text)
        self.assertIn("new Agent/TCP/Reno", self.text)
        self.assertIn("new Agent/UDP", self.text)
        self.assertIn("new Application/Traffic/CBR", self.text)
        self.assertIn("new TBF", self.text)
        self.assertIn('$ns at $isolation_time "$udp($k) attach-tbf $tbf($k)"', self.text)
        self.assertIn('$ns at $isolation_time "$udp($k) target $isolation_sink($k)"', self.text)
        self.assertNotIn('$ns at $isolation_time "$attack($k) stop"', self.text)

    @unittest.skipUnless(NS.is_file() and os.access(NS, os.X_OK), "native NS-2.35+nOBS binary unavailable")
    def test_direct_tcl_run_without_config_environment_fails_closed(self):
        result = subprocess.run(
            [str(NS), str(SCRIPT), "S1", "1", "1", "0.1", "none"],
            cwd=HERE, text=True, capture_output=True, timeout=10, check=False,
            env={"PATH": os.environ.get("PATH", "")},
        )
        self.assertEqual(result.returncode, 64)
        self.assertIn("missing required experiment parameter", result.stderr)

    @unittest.skipUnless(NS.is_file() and os.access(NS, os.X_OK), "native NS-2.35+nOBS binary unavailable")
    def test_invalid_scenario_contract_is_rejected_before_execution(self):
        result = subprocess.run(
            [str(NS), str(SCRIPT), "S2", "1", "12", "0.1", "none"],
            cwd=HERE, text=True, capture_output=True, timeout=10, check=False,
        )
        self.assertEqual(result.returncode, 64)
        self.assertIn("S2 requires mitigation", result.stderr)

    @unittest.skipUnless(NS.is_file() and os.access(NS, os.X_OK), "native NS-2.35+nOBS binary unavailable")
    def test_runner_snapshots_config_and_real_nobs_reaches_egress(self):
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        config["name"] = "config-driven-smoke"
        config["seeds"] = [7]
        config["nominal_attack_rate_mbps_per_source"] = 1.0
        config["simulation"]["measurement_duration_s"] = 0.25
        config["simulation"]["per_cell_timeout_s"] = 60
        config["scenarios"] = [{"label": "S1", "scenario": "S1", "mitigation": "none"}]
        with tempfile.TemporaryDirectory(prefix="nobs-config-smoke-") as tmp:
            root = pathlib.Path(tmp)
            config_path, output = root / "experiment.json", root / "result"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(RUNNER), "--config", str(config_path), "--out", str(output)],
                cwd=HERE, text=True, capture_output=True, timeout=90, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            completion = json.loads((output / "completion.json").read_text(encoding="utf-8"))
            self.assertEqual(completion["successful_cells"], 1)
            snapshot = output / "experiment_config.snapshot.json"
            run = json.loads((output / "seed_7" / "S1" / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run["experiment_config_sha256"], sha256(snapshot))
            trace = (output / "seed_7" / "S1" / "out.tr").read_text(encoding="utf-8")
            self.assertIn(" cbr ", trace)
            self.assertIn(" OP_BURST ", trace)
            self.assertRegex(trace, r"(?m)^r [^ ]+ 4 9 cbr ")


if __name__ == "__main__":
    unittest.main()
