# OBS BHP Flooding Detection and Mitigation

Research code for experiments on Burst Header Packet (BHP) flooding in Optical Burst Switching (OBS) networks. This repository contains **experiment source only**: NS-2.35+nOBS overlay code, experiment configurations, runners, validators, compact canonical evidence, analysis scripts, tests, and experiment outputs.

**Not included:** thesis DOCX/PDF/ZIP files, document-rendering scripts, LibreOffice requirements, and manuscript-specific audits. Those artifacts are maintained locally outside this Git repository.

## What is reproducible here

| Route | Command | What it does | Primary output |
|---|---|---|---|
| Portable configuration check | `python3 experiments/direct_bhp/validator.py --config experiments/direct_bhp/config.json` | Validates config and control-path boundary without NS execution | JSON verdict on stdout |
| Portable tests | `python3 -m unittest discover -s experiments/tests -v` | Tests runner/validator/parser invariants | unittest report |
| UCI404 analysis | `python3 source_only/uci404/pipeline.py` | Recomputes ML-analysis tables and figures from the included ARFF | `source_only/uci404/outputs/` |
| Native smoke run | `bash run_native_repro.sh --smoke` | Runs one real NS-2.35+nOBS cell | `reproduction_runs/<timestamp>/native_matrix/` |
| Native full run | `bash run_native_repro.sh --full` | Runs all 32 native cells and analyzes them | `reproduction_runs/<timestamp>/native_matrix/` |
| Verify retained canonical evidence | `python3 experiments/direct_bhp/verify_canonical_evidence.py --output /tmp/direct-bhp-canonical-check.json` | Checks the trace-free 32-cell evidence bundle and its hash binding; does not run NS | `/tmp/direct-bhp-canonical-check.json` |

The direct-BHP experiment is bounded to the declared seven-node topology, traffic profile, fixed seeds, and five-second runs. The guard is a deterministic token-budget control path; it is not an ML detector or a deployment benchmark.

## 1. Prepare Ubuntu / WSL2

Use Ubuntu 24.04 or WSL2 Ubuntu. Clone inside the Linux filesystem, not `/mnt/c`.

```bash
git clone git@github.com:mxuanvan02/OBS-BHP-Flooding-Detection-Mitigation.git
cd OBS-BHP-Flooding-Detection-Mitigation
bash setup_environment.sh --system-deps
source .venv/bin/activate
```

Expected final marker:

```text
ENVIRONMENT_READY: .../.venv
```

`setup_environment.sh --system-deps` installs only experiment prerequisites (Python, compiler/build tools, Tcl/Tk/X11 development headers, and archive utilities). It does not install LibreOffice.

## 2. Run portable checks

```bash
python3 experiments/direct_bhp/validator.py --config experiments/direct_bhp/config.json
python3 -m unittest discover -s experiments/tests -v
python3 -m unittest discover -s source_only/uci404/tests -v
python3 -m unittest discover -s tests -v
```

Success conditions:

- validator returns JSON with `"valid": true`;
- all unittest commands end with `OK`.

## 3. Recompute UCI404 analysis (optional, separate from native BHP experiment)

```bash
python3 source_only/uci404/pipeline.py
```

Outputs:

```text
source_only/uci404/outputs/
├── dataset_schema.csv
├── provenance.json
├── output_manifest.json
├── raw/
│   ├── fold_metrics.csv
│   ├── rf_oof_permutation_fold.csv
│   └── single_feature_fold_metrics.csv
├── summary/
│   ├── model_summary.csv
│   ├── rf_permutation_importance_summary.csv
│   └── single_feature_summary.csv
└── figures/
    ├── model_macro_f1.png
    ├── rf_oof_permutation_importance.png
    └── single_feature_audit.png
```

This route is a leakage/provenance-audited dataset analysis. It does not execute NS-2.35 and must not be presented as a direct-BHP native result.

## 4. Build the native NS-2.35+nOBS executable

```bash
bash provision_native_ns.sh
```

The provisioner downloads (or uses `NS235_ARCHIVE`), SHA-256-verifies the pinned NS-2.35 archive, applies the versioned `nobs/` overlay, and builds:

```text
build/ns-allinone-2.35/ns-2.35/ns
```

Expected final marker:

```text
NATIVE_PROVISION_OK: .../ns
```

To rebuild cleanly:

```bash
bash provision_native_ns.sh --clean
```

## 5. Run a real native smoke test

```bash
NOBS_NS_TREE="$PWD/build/ns-allinone-2.35/ns-2.35" \
  bash run_native_repro.sh --smoke
```

The default smoke cell is seed `101`, scenario `S2_rate_limit`. Expected final marker:

```text
NATIVE_RUN_OK
```

Outputs are created at:

```text
reproduction_runs/<timestamp>/
├── native_run.log
└── native_matrix/
    ├── experiment_config.snapshot.json
    ├── matrix_manifest.json
    ├── completion.json
    ├── validation.json
    ├── revalidation.json
    ├── SHA256SUMS.txt
    └── seed_101/S2_rate_limit/
        ├── out.tr
        ├── stat.txt
        ├── bhp_audit.log
        ├── bhp_source.log
        ├── stdout.log
        ├── stderr.log
        ├── command.txt
        └── run.json
```

`out.tr` is the native network trace. `bhp_source.log` records generated direct BHPs; `bhp_audit.log` records the causal control chain; `run.json` records command, inputs and artifact SHA-256 values.

## 6. Run the complete native 32-cell matrix

```bash
NOBS_NS_TREE="$PWD/build/ns-allinone-2.35/ns-2.35" \
  bash run_native_repro.sh --full
```

This executes 8 fixed seeds (`101` … `808`) × 4 scenarios:

- `S0`: legal baseline;
- `S1`: direct-BHP attack, permissive profile;
- `S2_rate_limit`: direct-BHP attack with token-budget rate limit;
- `S2_isolation`: direct-BHP attack with isolation profile.

In addition to the smoke-run files, a full run creates:

```text
reproduction_runs/<timestamp>/native_matrix/analysis/
├── per_seed.csv
├── summary.json
└── REPORT.md
```

Acceptance requirements are all enforced fail-closed:

- `completion.json`: 32 successful cells, 0 failures, `full_matrix_complete: true`;
- `revalidation.json`: `valid: true`;
- `analysis/`: per-seed metrics and aggregate effects;
- `SHA256SUMS.txt`: hashes for all retained run artifacts.

A non-zero exit means the run is not accepted. Do not describe a smoke run as a full-matrix result.

## 7. Validate committed canonical evidence without rerunning NS

Raw traces are deliberately excluded from Git. The compact canonical evidence is retained in `evidence/direct_bhp_matrix/`.

```bash
python3 experiments/direct_bhp/verify_canonical_evidence.py \
  --evidence evidence/direct_bhp_matrix \
  --output /tmp/direct-bhp-canonical-check.json
cat /tmp/direct-bhp-canonical-check.json
```

Expected terminal marker: `CANONICAL_EVIDENCE_OK`. The JSON result must report:

- `"schema": "nobs-direct-bhp-canonical-evidence-check-v2"`;
- `"valid": true` and `"cells": 32`;
- `validation_rerun_sha256`: the exact SHA-256 of the retained v2 revalidation record;
- `validation_engine_sha256`: the validator source hash recorded when the 32-cell matrix was checked;
- `summary_sha256`: the SHA-256 of the descriptive analysis summary bound to that validation record.

### How to read canonical-evidence outputs

| File | Role | Key fields to inspect | What it does **not** prove |
|---|---|---|---|
| `completion.json` | Matrix completion declaration | `successful_cells: 32`, `failed_cells: 0`, `full_matrix_complete: true` | Per-cell causal correctness by itself |
| `matrix_manifest.json` | Declared experiment inputs and 32 selected cells | fixed seed/scenario pairs, input SHA-256 map, full-matrix flag | That a local executable is byte-identical to the retained native executable |
| `validation.json` and `validation.rerun.json` | Identical v2 fail-closed validation reports | `valid`, complete cell set, network-outcome gate, input/artifact provenance, hashes of completion/manifest/config | A new native run on the machine performing this check |
| `per_seed.csv` | One descriptive row per seed × scenario | legal TCP bytes/packets, optical counters, direct-BHP action counts | Uncertainty beyond the eight fixed seeds |
| `summary.json` | Aggregate descriptive statistics and effect calculations | `source_validation_sha256`, means, intervals, action totals, claim limits | A deployment or generalization claim |
| `REPORT.md` | Human-readable matrix summary | 32/32 status, seed set, main directional effects, claim boundary | Additional machine-verifiable evidence beyond the JSON/CSV records |

The verifier rejects the bundle if either validation report is not v2, the two validation files differ, the expected 32 cells are absent, the completion/manifest/config hashes do not match v2 provenance, or `summary.json` does not bind to `validation.rerun.json`.

This is intentionally a **trace-free bundle check**. It verifies the retained compact evidence and its provenance chain. It is **not** a new NS-2.35 execution, does not replay raw traces, and produces no thesis document.

## Repository layout

```text
nobs/                         versioned NS-2.35 overlay and direct-BHP components
experiments/                  native scenarios, runner, validator, parser, analysis, tests
evidence/direct_bhp_matrix/   compact validated 32-cell evidence (not raw traces)
source_only/uci404/           separately scoped UCI404 analysis
data/                         input datasets
results/                      committed non-native experiment outputs
provision_native_ns.sh        build native NS-2.35+nOBS
run_native_repro.sh           smoke/full native execution entry point
VALIDATION.md                 concise command-to-output contract
```

See `REPO_SCOPE.md` for claim boundaries and `VALIDATION.md` for the short execution checklist.
