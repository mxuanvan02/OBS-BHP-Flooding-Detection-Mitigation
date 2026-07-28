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

## Quick checks

```bash
# Validate portable config/source boundary.
python3 experiments/direct_bhp/validator.py --config experiments/direct_bhp/config.json

# Check packaged compact evidence and rebuild final artifacts.
bash run_pipeline.sh --reuse-canonical

# Portable tests (native execution tests skip unless build/.../ns is provisioned).
python3 -m unittest discover -s experiments/tests -v
python3 -m unittest discover -s tests -v
```

`--reuse-canonical` verifies the packaged 32-cell validation report and statistics; it does not claim to revalidate excluded raw traces. `--full` requires a native NS-2.35 build/toolchain and creates local runtime outputs that are ignored by Git. Current direct-BHP evidence is a native control-path prototype; it is not presented as a completed online ML detector or production deployment.

## Source synchronization and reproducible native run

The experiment is reproducible only when both components below are available:

1. The versioned nOBS overlay in `nobs/` (guard, audit, source-routing and BHP-agent files).
2. A native, patched NS-2.35 binary at `build/ns-allinone-2.35/ns-2.35/ns`, or at the path supplied by `NOBS_NS_TREE`.

The current repository snapshot contains the nOBS overlay and the runner/configuration, but **does not contain the native NS binary**. The runner therefore fails closed instead of silently substituting a Python simulation. Verify the state with:

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
