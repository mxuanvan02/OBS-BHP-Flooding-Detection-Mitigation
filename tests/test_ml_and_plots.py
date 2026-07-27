from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ml_pipeline import LEAKAGE_COLUMNS, run_ml_pipeline
from plot_results import make_plots


def _fixture(root: Path):
    raw, tables, figures = root / "raw", root / "tables", root / "figures"
    raw.mkdir()
    tables.mkdir()
    figures.mkdir()
    rows = []
    for seed in range(6):
        for window in range(4):
            attack = int(window >= 2)
            rows.append(
                {
                    "scenario": "S1" if attack else "S0",
                    "seed": seed,
                    "window_start": window * 0.25,
                    "window_end": (window + 1) * 0.25,
                    "attack_label": attack,
                    "legal_mbps": 10 - attack * 3 + seed * 0.01,
                    "aggregate_mbps": 11 + attack * 7,
                    "attacker_mbps": attack * 50,
                    "burst_rate": 2 + attack * 4,
                    "burst_loss_rate": 0.01,
                    "rate_cv": 0.1,
                    "active_sources": attack,
                }
            )
    pd.DataFrame(rows).to_csv(raw / "window_dataset.csv", index=False)
    pd.DataFrame(
        [
            {
                "scenario": scenario,
                "seed": seed,
                "legal_packets": 100 - (scenario != "S0") * 20,
            }
            for scenario in ["S0", "S1", "S2_rate_limit", "S2_isolation"]
            for seed in range(6)
        ]
    ).to_csv(raw / "runs.csv", index=False)
    pd.DataFrame(
        [
            {
                "attack_rate_mbps": rate,
                "seed": seed,
                "legal_packets": 100 - rate,
                "bursts_sent": rate * 2,
            }
            for rate in [5, 10, 15]
            for seed in [1, 2, 3]
        ]
    ).to_csv(raw / "sweep.csv", index=False)
    return raw, tables, figures


class MlAndPlotTests(unittest.TestCase):
    def test_ml_outputs_schema_and_excludes_leakage(self):
        with tempfile.TemporaryDirectory(prefix="obs-ml-test-") as tmp:
            raw, tables, _ = _fixture(Path(tmp))
            results, audit = run_ml_pipeline(raw / "window_dataset.csv", tables)
            self.assertEqual(
                set(results["model"]),
                {"SVM-RBF", "KNN", "DecisionTree", "GaussianNB"},
            )
            self.assertTrue({"model", "fold", "mcc", "balanced_accuracy"} <= set(results.columns))
            self.assertEqual(len(results), 20)
            self.assertTrue({"feature", "excluded_for_model", "fold", "mcc"} <= set(audit.columns))
            used = set(";".join(results["features"]).split(";"))
            self.assertFalse(used & LEAKAGE_COLUMNS)
            self.assertEqual(
                set(audit.loc[audit["excluded_for_model"], "feature"]),
                {"attacker_mbps", "active_sources"},
            )

    def test_plots_outputs_png(self):
        with tempfile.TemporaryDirectory(prefix="obs-plot-test-") as tmp:
            raw, tables, figures = _fixture(Path(tmp))
            run_ml_pipeline(raw / "window_dataset.csv", tables)
            make_plots(raw, tables, figures)
            expected = {
                "throughput_by_seed.png",
                "impact_sweep.png",
                "mitigation_ci.png",
                "ml_mcc.png",
            }
            self.assertEqual({path.name for path in figures.glob("*.png")}, expected)
            self.assertTrue(all(path.stat().st_size > 100 for path in figures.glob("*.png")))


if __name__ == "__main__":
    unittest.main()
