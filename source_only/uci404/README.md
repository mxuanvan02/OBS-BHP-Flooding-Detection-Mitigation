# UCI404 source-only reproduction

This isolated pipeline reads the official UCI 404 ARFF directly. It never uses
`results/window_dataset.csv`, `simulator.py`, or files under `artifacts/github/nOBS`.

## Reproduce

From the repository root, first install the pinned environment (`bash setup_environment.sh` or `bash setup_environment.sh --system-deps` on Ubuntu/Debian), then run:

```bash
source .venv/bin/activate
python3 source_only/uci404/pipeline.py
python3 -m unittest discover -s source_only/uci404/tests -v
```

The fixed public configuration is `config.json`: five shuffled stratified group
folds for each seed `17, 42, 73, 101, 2026`; fixed, untuned DecisionTree,
SVM-RBF, KNN, and GaussianNB baselines. Inspection found that the 1,075-row ARFF
is exactly five copies of 215 unique rows. Group IDs are hashes of all original
predictors (excluding the target), so exact copies never cross train/test.
Numeric values are median-imputed inside each training fold: contrary to the
current UCI page's “no missing values” statement, the ARFF has 15 `?` cells in
`Packet_lost`. The nominal `Node Status` is most-frequent-imputed and one-hot
encoded inside each training fold. SVM-RBF, KNN, and GaussianNB use training-fold
standardization. The DecisionTree does not use scaling.

The single-feature audit applies the fixed DecisionTree independently to every
one of the 21 predictors over the same 25 test folds. The RandomForest audit
uses 200 trees and seed 42. In each of five folds it is fitted only to the
training partition, then each original feature is permuted 10 times only in the
unseen test partition; macro-F1 decrease is reported. This out-of-fold design
avoids in-sample importance, although it does not eliminate dependencies among
rows or target-construction leakage.

Outputs include raw fold CSVs, aggregate summary CSVs, schema/provenance and
SHA-256 manifests, plus PNG figures under `outputs/`.

## Important interpretation limits

UCI documents `Node Status`, `Flood Status`, and `Class` as classifications or
quantities derived from overlapping network measurements. `Class` is therefore
a four-class policy label rather than independent physical ground truth. Very
high scores—especially from a single feature—must be treated as evidence of
possible deterministic target construction/leakage, not proof of generalization
to a new OBS deployment. UCI supplies no higher-level experiment group IDs or
recommended split.

## PSO-SVM blocker

**Reported-only:** the official UCI artifact/metadata does not provide a
reproducible original PSO-SVM artifact and complete configuration (swarm,
search bounds, iterations, objective, preprocessing, seeds). This pipeline does
not fabricate one and does not copy thesis-reported numbers.
