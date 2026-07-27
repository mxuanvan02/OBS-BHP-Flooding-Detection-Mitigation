import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

EXPERIMENTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXPERIMENTS))

from analyze_sweep import ci95  # noqa: E402


class SweepStatisticsTests(unittest.TestCase):
    def test_ci95_is_centered_and_nonzero_for_varying_samples(self):
        mean, low, high = ci95([1.0, 2.0, 3.0, 4.0])
        self.assertEqual(mean, 2.5)
        self.assertLess(low, mean)
        self.assertGreater(high, mean)
        self.assertAlmostEqual(mean - low, high - mean)
        self.assertAlmostEqual(low, 0.445739743239121, places=12)
        self.assertAlmostEqual(high, 4.554260256760879, places=12)

    def test_ci95_single_sample_has_undefined_bounds(self):
        mean, low, high = ci95([7.0])
        self.assertEqual(mean, 7.0)
        self.assertNotEqual(low, low)
        self.assertNotEqual(high, high)


class SweepPlotTests(unittest.TestCase):
    def _write_summary(self, path: Path, n: int = 8) -> None:
        fields = ["attack_rate_mbps", "metric", "n", "mean", "ci95_low", "ci95_high"]
        metrics = ("legal_packets", "bursts_offered", "burst_loss_rate")
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for rate in range(5, 55, 5):
                for metric in metrics:
                    mean = float(rate)
                    writer.writerow({
                        "attack_rate_mbps": rate,
                        "metric": metric,
                        "n": n,
                        "mean": mean,
                        "ci95_low": mean - 1,
                        "ci95_high": mean + 1,
                    })

    def test_plot_cli_writes_nonempty_png(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            summary, output = root / "summary.csv", root / "figure.png"
            self._write_summary(summary)
            subprocess.run(
                [sys.executable, str(EXPERIMENTS / "plot_sweep.py"), str(summary), "--out", str(output)],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertTrue(output.is_file())
            self.assertGreater(output.stat().st_size, 1000)
            self.assertEqual(output.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")

    def test_plot_cli_rejects_wrong_seed_count(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            summary, output = root / "summary.csv", root / "figure.png"
            self._write_summary(summary, n=7)
            result = subprocess.run(
                [sys.executable, str(EXPERIMENTS / "plot_sweep.py"), str(summary), "--out", str(output)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0)

    def test_plot_cli_rejects_duplicate_rates(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            summary, output = root / "summary.csv", root / "figure.png"
            self._write_summary(summary)
            with summary.open(encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
            rows[3]["attack_rate_mbps"] = rows[0]["attack_rate_mbps"]
            with summary.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=rows[0])
                writer.writeheader(); writer.writerows(rows)
            result = subprocess.run(
                [sys.executable, str(EXPERIMENTS / "plot_sweep.py"), str(summary), "--out", str(output)],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("duplicate rates", result.stderr)


class RetainedSweepArtifactTests(unittest.TestCase):
    def test_retained_sweep_validation_is_complete(self):
        validation = EXPERIMENTS / "sweep_analysis_20260726" / "sweep_validation.json"
        if not validation.is_file():
            self.skipTest("retained sweep analysis artifact is not present")
        value = json.loads(validation.read_text(encoding="utf-8"))
        self.assertTrue(value["complete"])
        self.assertEqual(value["attempted_cells"], 80)
        self.assertEqual(value["successful_cells"], 80)
        self.assertEqual(value["failed_cells"], 0)
        self.assertEqual(set(value["seeds_per_rate"].values()), {8})


if __name__ == "__main__":
    unittest.main()
