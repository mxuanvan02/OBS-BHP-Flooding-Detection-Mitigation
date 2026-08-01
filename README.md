# OBS BHP Flooding Detection and Mitigation

Research prototype for detecting and mitigating Burst Header Packet (BHP) flooding in Optical Burst Switching (OBS) networks. The repository combines machine-learning analysis, NS-2.35+nOBS network simulation, native BHP control-plane enforcement, causal auditing, and mitigation evaluation.

The enforcement target is the trusted OBS edge ingress, before a BHP creates a wavelength reservation in the optical core. The codebase contains both the reconstructed valid-burst overload experiment and the native control-only BHP/guard prototype; their evidence and claims are kept separate.

## Evidence status

- Native direct-BHP matrix: **32/32 cells validated** (4 scenarios × 8 fixed seeds).
- Results are limited to the declared seven-node topology, traffic profile and five-second runs.
- The guard is a deterministic token-budget control path, not a reconstructed ML detector.
- UCI/ML material is separately audited and is not silently claimed as an exact reproduction where source/protocol artifacts are unavailable.

## What the code does

- analyzes OBS/BHP datasets and evaluates classification metrics while checking label leakage;
- simulates legal TCP traffic and BHP/burst load through NS-2.35+nOBS;
- prototypes direct control-only BHP generation and admission control with `BHPFloodAgent`, `BhpGuard`, and `BhpAuditLogger`;
- records the causal chain `BHP_CREATE → OBSERVE → DETECT → DECIDE → ACT`;
- validates source provenance, experiment manifests, traces, metrics, figures, and document artifacts.

## Clone, install, and reproduce the published artifacts

Validated reference environment: Ubuntu 24.04, Python 3.12.12, LibreOffice 24.2, and the exact Python package versions in `requirements.txt`. From a fresh clone:

```bash
git clone git@github.com:mxuanvan02/OBS-BHP-Flooding-Detection-Mitigation.git
cd OBS-BHP-Flooding-Detection-Mitigation

# Ubuntu/Debian: install system tools, create .venv, and install pinned Python packages.
bash setup_environment.sh --system-deps
source .venv/bin/activate

# Recompute the UCI404 machine-learning tables and figures from the included ARFF.
python3 source_only/uci404/pipeline.py
python3 -m unittest discover -s source_only/uci404/tests -v

# Validate portable/native configuration and all portable tests.
python3 experiments/direct_bhp/validator.py --config experiments/direct_bhp/config.json
python3 -m unittest discover -s experiments/tests -v
python3 -m unittest discover -s tests -v

# Rebuild and gate the thesis DOCX/PDF using the packaged validated 32-cell matrix.
bash run_pipeline.sh --reuse-canonical
```

A successful final command prints `PIPELINE_OK` and the generated artifact paths under `reproduction_runs/<timestamp>/`. This is the shortest audited route from a fresh clone to the tables, figures, statistics, DOCX, and PDF reported in the repository. It verifies and reuses the retained native 32-cell evidence because raw native traces are intentionally not committed. It does **not** describe the matrix as a newly executed NS-2 experiment.

The included UCI404 ARFF is hash-gated at `c573b83a9b8db30658be8dd53ef5769a94bc03a0695e78d6c130306c60cc69de`. The UCI/ML analysis remains separate from the direct-BHP native experiment and does not fabricate the unavailable original PSO-SVM protocol.

### Dependency check only

If system packages are already installed, omit `--system-deps`:

```bash
bash setup_environment.sh
source .venv/bin/activate
```

## Source synchronization and reproducible native run

The experiment is reproducible only when both components below are available:

1. The versioned nOBS overlay in `nobs/` (guard, audit, source-routing and BHP-agent files).
2. A native, patched NS-2.35 binary at `build/ns-allinone-2.35/ns-2.35/ns`, or at the path supplied by `NOBS_NS_TREE`.

The current repository snapshot contains the nOBS overlay and the runner/configuration, but **does not contain the native NS binary**. The runner therefore fails closed instead of silently substituting a Python simulation. To perform a fresh native rerun, install/build NS-2.35 first:

Run the provisioner below. It downloads the pinned NS-2.35 archive, verifies its SHA-256, extracts local X11 headers when needed, applies the versioned nOBS overlay, adds all nOBS objects to `OBJ_CC`, and builds the native binary. No manual copying or Makefile editing is required:

```bash
bash provision_native_ns.sh
```

The archive can also be supplied offline with `NS235_ARCHIVE=/absolute/path/ns-allinone-2.35.tar.gz`. The provisioner accepts only SHA-256 `2216f4e8e274f5c2437741fc6e9c9728369fabe1838c708ef974d262b941cd5d`. `xgraph` is optional; failure to build that helper does not invalidate the `ns` binary. Compiler or dependency failure stops the script and is not silently replaced by the Python model.

After success, `build/ns-allinone-2.35/ns-2.35/ns` is the native executable. To rebuild from scratch, use `bash provision_native_ns.sh --clean`.

These steps are intentionally explicit: a native 32-cell rerun is accepted only with the patched executable and all trace/causal gates. Verify the state with:

```bash
cd /path/to/BHP-Flooding-OBS-Thesis-Reproduction
sha256sum nobs/optical/op-bhp-guard.cc experiments/parse_trace.py
test -x "${NOBS_NS_TREE:-build/ns-allinone-2.35/ns-2.35}/ns" \
  && echo "native NS-2.35: READY" \
  || echo "native NS-2.35: MISSING (full run unavailable)"
python3 experiments/direct_bhp/validator.py \
  --config experiments/direct_bhp/config.json
```

### One-cell smoke test

After provisioning the native binary, run this command. It creates a timestamped directory under `reproduction_runs/`; the outer log captures every command and message, while the runner stores `out.tr`, `stat.txt`, `bhp_audit.log`, `bhp_source.log`, `stdout.log`, `stderr.log`, `command.txt` and hashes for the selected cell:

```bash
cd /path/to/BHP-Flooding-OBS-Thesis-Reproduction
NOBS_NS_TREE=/absolute/path/to/ns-allinone-2.35/ns-2.35 \
  bash run_native_repro.sh --smoke
```

The smoke run is a real native NS-2.35+nOBS execution, not a canonical-data replay. It validates the selected cell, but does not claim 32/32 or reproduce thesis-level aggregate statistics.

### Full native 32-cell reproduction

```bash
cd /path/to/BHP-Flooding-OBS-Thesis-Reproduction
NOBS_NS_TREE=/absolute/path/to/ns-allinone-2.35/ns-2.35 \
  bash run_native_repro.sh --full
```

The full command runs 8 fixed seeds × 4 scenarios, then performs fail-closed validation and native-result analysis. All output is saved under a new timestamped run directory. The final lines print `NATIVE_RUN_OK`, `output` and `log` paths; `completion.json`, `revalidation.json` and, for the full run, `analysis/` are stored below that output directory. A non-zero exit means the run is not accepted.

### Reuse canonical evidence (does not rerun NS)

```bash
bash run_pipeline.sh --reuse-canonical
```

This mode is intentionally different: it checks the retained canonical 32-cell evidence and rebuilds document artifacts. It must not be described as a fresh native run. Use `--full` in `run_pipeline.sh` only after the native binary and patched build are provisioned; that pipeline also renders and gates the DOCX/PDF.
