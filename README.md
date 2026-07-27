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
