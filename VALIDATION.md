# Validation and execution contract

The committed canonical evidence is `evidence/direct_bhp_matrix/`. It contains the validated compact 32-cell result (four scenarios × eight fixed seeds), summary statistics, per-seed data and provenance metadata. Raw NS-2 traces and the native build are intentionally excluded from Git because of size; `--full` therefore requires a separately provisioned NS-2.35+nOBS toolchain.

The portable validation checks are:

```bash
# Config and packaged-source boundary.
python3 experiments/direct_bhp/validator.py --config experiments/direct_bhp/config.json

# Portable test suites.
python3 -m unittest discover -s experiments/tests -v
python3 -m unittest discover -s tests -v

# Verify compact canonical evidence, rebuild DOCX/PDF, and run artifact gates.
bash run_pipeline.sh --reuse-canonical
```

`--reuse-canonical` checks the committed completion metadata, 32-cell validation report, summary/per-seed statistics, and final document gates. It deliberately does not rerun raw-trace validation because raw traces are excluded. Use `--full` with a separately provisioned native build to rerun and revalidate all 32 cells.

The direct-BHP result is a native control-only prototype with a deterministic token-budget guard. The repository does not claim that the current code is a production detector, an online ML-to-actuator loop, or an end-to-end deployment benchmark. Re-running packaged evidence validates the declared artifacts; it does not recreate unavailable original inputs.
