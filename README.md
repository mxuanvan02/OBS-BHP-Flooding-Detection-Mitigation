# BHP Flooding OBS Thesis Reproduction

Aggregated reproduction repository for the OBS/BHP thesis: modified nOBS source, native NS-2.35 direct-BHP experiment, validators, analysis, figures/document pipeline, audit reports and final thesis artifacts.

## Evidence status

- Native direct-BHP matrix: **32/32 cells validated** (4 scenarios × 8 fixed seeds).
- Results are limited to the declared seven-node topology, traffic profile and five-second runs.
- The guard is a deterministic token-budget control path, not a reconstructed ML detector.
- UCI/ML material is separately audited and is not silently claimed as an exact reproduction where source/protocol artifacts are unavailable.

## Quick checks

```bash
# Validate portable config/source boundary.
python3 experiments/direct_bhp/validator.py --config experiments/direct_bhp/config.json

# Check packaged compact evidence and rebuild final artifacts.
bash reproduce_thesis.sh --reuse-canonical

# Portable tests (native execution tests skip unless build/.../ns is provisioned).
python3 -m unittest discover -s experiments/tests -v
python3 -m unittest discover -s tests -v
```

`--reuse-canonical` verifies the packaged 32-cell validation report and statistics; it does not claim to revalidate excluded raw traces. `--full` requires a native NS-2.35 build/toolchain and creates local runtime outputs that are ignored by Git.
