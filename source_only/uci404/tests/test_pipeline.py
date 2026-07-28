import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "pipeline.py"
spec = importlib.util.spec_from_file_location("uci404_pipeline", MODULE_PATH)
pipeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline)


class DatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_path = Path(__file__).resolve().parents[1] / "config.json"
        cls.config = pipeline.load_config(cls.config_path)
        cls.dataset_path = pipeline.resolve_dataset_path(cls.config, cls.config_path)
        cls.frame, cls.metadata, cls.digest = pipeline.load_arff_dataset(
            cls.dataset_path, cls.config["dataset"]["expected_sha256"])

    def test_official_hash_shape_schema_and_classes(self):
        self.assertEqual(self.digest, "c573b83a9b8db30658be8dd53ef5769a94bc03a0695e78d6c130306c60cc69de")
        self.assertEqual(self.frame.shape, (1075, 22))
        self.assertEqual(self.metadata.names()[-1], "Class")
        self.assertEqual(set(self.frame["Class"]), {"NB-No Block", "Block", "No Block", "NB-Wait"})
        self.assertEqual(int(self.frame.isna().sum().sum()), 15)
        self.assertEqual(int(self.frame["Packet_lost"].isna().sum()), 15)

    def test_config_has_public_stratified_five_fold_seeds(self):
        self.assertEqual(self.config["evaluation"]["splitter"], "StratifiedGroupKFold")
        self.assertEqual(self.config["evaluation"]["n_splits"], 5)
        self.assertEqual(self.config["evaluation"]["seeds"], [17, 42, 73, 101, 2026])
        self.assertEqual(self.config["random_forest_importance"]["n_estimators"], 200)

    def test_preprocessing_and_all_models_fit_small_partition(self):
        target = self.config["dataset"]["target"]
        predictors, numeric, categorical = pipeline.feature_types(self.frame, target)
        self.assertEqual(len(predictors), 21)
        self.assertEqual(categorical, ["Node Status"])
        models = pipeline.build_models(self.config, numeric, categorical, seed=17)
        self.assertEqual(set(models), {"DecisionTree", "SVM-RBF", "KNN", "GaussianNB"})
        for model in models.values():
            model.fit(self.frame[predictors].iloc[:200], self.frame[target].iloc[:200])
            self.assertEqual(len(model.predict(self.frame[predictors].iloc[200:210])), 10)

    def test_exact_duplicates_are_grouped_and_do_not_cross_folds(self):
        target = self.config["dataset"]["target"]
        predictors = [c for c in self.frame if c != target]
        groups = pipeline.make_groups(self.frame, predictors)
        self.assertEqual(len(set(groups)), 215)
        self.assertEqual(int(self.frame.duplicated().sum()), 860)
        for train, test in pipeline.splitter(self.config, self.frame[target], groups, 17):
            self.assertTrue(set(groups[train]).isdisjoint(groups[test]))

    def test_hash_mismatch_is_blocking(self):
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            pipeline.load_arff_dataset(self.dataset_path, "0" * 64)

    def test_metric_values_are_bounded(self):
        actual = ["a", "a", "b", "b"]
        predicted = ["a", "b", "b", "b"]
        metrics = pipeline.metric_row(actual, predicted)
        for name, value in metrics.items():
            lower = -1 if name == "mcc" else 0
            self.assertGreaterEqual(value, lower)
            self.assertLessEqual(value, 1)


class SmokeRunTests(unittest.TestCase):
    def test_end_to_end_reduced_config(self):
        config_path = Path(__file__).resolve().parents[1] / "config.json"
        config = pipeline.load_config(config_path)
        config["evaluation"]["seeds"] = [17]
        config["random_forest_importance"]["n_estimators"] = 5
        config["random_forest_importance"]["permutation_repeats"] = 2
        config["dataset"]["path"] = str(pipeline.resolve_dataset_path(config, config_path))
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            reduced_config = tmp / "config.json"
            reduced_config.write_text(json.dumps(config), encoding="utf-8")
            output = pipeline.run(reduced_config, tmp / "outputs")
            self.assertEqual(len(list((output / "figures").glob("*.png"))), 3)
            self.assertTrue((output / "raw" / "fold_metrics.csv").is_file())
            self.assertTrue((output / "summary" / "model_summary.csv").is_file())
            self.assertTrue((output / "provenance.json").is_file())
            manifest = json.loads((output / "output_manifest.json").read_text())
            self.assertGreaterEqual(len(manifest["files"]), 10)


if __name__ == "__main__":
    unittest.main()
