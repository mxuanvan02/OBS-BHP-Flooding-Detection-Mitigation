# Repository scope

This repository contains a research prototype for BHP-flooding detection and mitigation in Optical Burst Switching (OBS) networks.

- `nobs/`: modified nOBS/ns-2 source and native BHP control-plane components.
- `experiments/`: experiment runners, validators, parsers, analysis and tests.
- `data/`, `ml_pipeline.py`, and `results/`: dataset analysis, leakage checks, metrics and figures.
- `evidence/direct_bhp_matrix/`: compact validation metadata/statistics; raw traces are intentionally excluded.
- `audits/`: scope, threat-model, provenance and claim-boundary audits.
- `deliverables/`: generated DOCX/PDF research artifacts.

The native direct-BHP matrix is validated at 32/32 cells in the declared reconstructed configuration. The main NS-2/nOBS attack matrix uses valid bursts generated from UDP load; the direct control-only BHP path is a separate prototype/smoke path. ML/UCI outputs are reported with their leakage and provenance limitations rather than being presented as deployment evidence.
