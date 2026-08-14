# Repository scope

This repository is an experiment-code artifact for BHP-flooding research in Optical Burst Switching (OBS) networks.

## Included

- `nobs/`: modified nOBS/NS-2.35 source overlay, including native BHP source, guard and audit components.
- `experiments/`: Tcl scenarios, native runner, validators, trace parsing, analysis and tests.
- `evidence/direct_bhp_matrix/`: compact validation metadata, per-seed statistics and result summaries for the retained 32-cell matrix.
- `source_only/uci404/`, `data/`, `ml_pipeline.py`, `simulator.py`, and `results/`: separately scoped dataset analysis and reconstructed approximation code/results.
- `audits/`: experiment scope, provenance, threat-model and claim-boundary audits that do not depend on a thesis manuscript.

## Excluded

The repository deliberately excludes all thesis artifacts and document-production tooling:

- DOCX, PDF and ZIP deliverables;
- manuscript editing/rendering scripts and figure insertion scripts;
- thesis-specific requirements, traceability audits and screenshots;
- LibreOffice/PDF document dependencies.

Those materials are retained outside the repository as local thesis artifacts. The experiment code neither creates nor validates a thesis document.

## Claim boundaries

The native direct-BHP matrix covers four scenarios across eight fixed seeds in a declared seven-node topology and five-second run duration. It validates a deterministic token-budget guard on the native control path. It does not establish an online ML detector-actuator loop, a production deployment, a false-positive estimate for all legitimate traffic, or a reproduction of unavailable upstream protocols.

Raw native traces are not committed because of repository size. A fresh native run is reproducible by provisioning NS-2.35 with `provision_native_ns.sh` and executing `run_native_repro.sh --full`; the committed evidence is a compact, independently checkable record rather than a substitute for executing NS.
