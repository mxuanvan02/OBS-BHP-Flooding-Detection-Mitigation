# Validation and execution contract

Run all commands from the repository root after `source .venv/bin/activate`.

## A. Portable validation

```bash
python3 experiments/direct_bhp/validator.py --config experiments/direct_bhp/config.json
python3 -m unittest discover -s experiments/tests -v
python3 -m unittest discover -s source_only/uci404/tests -v
python3 -m unittest discover -s tests -v
```

Expected: validator JSON has `"valid": true`; every test suite ends with `OK`.

## B. Canonical-evidence validation (no native execution)

```bash
python3 experiments/direct_bhp/verify_canonical_evidence.py \
  --evidence evidence/direct_bhp_matrix \
  --output /tmp/direct-bhp-canonical-check.json
```

Expected: terminal marker `CANONICAL_EVIDENCE_OK`; `/tmp/direct-bhp-canonical-check.json` has `"valid": true` and `"cells": 32`. This checks the compact committed evidence and its summary-to-validation hash binding only; it does not regenerate raw traces or run NS-2.35.

## C. Native smoke execution

```bash
bash provision_native_ns.sh
NOBS_NS_TREE="$PWD/build/ns-allinone-2.35/ns-2.35" \
  bash run_native_repro.sh --smoke
```

Expected terminal marker: `NATIVE_RUN_OK`.

Expected output: `reproduction_runs/<timestamp>/native_matrix/` containing a selected cell's trace, BHP logs, command, manifest, validation reports and SHA-256 sums.

## D. Native full-matrix execution

```bash
NOBS_NS_TREE="$PWD/build/ns-allinone-2.35/ns-2.35" \
  bash run_native_repro.sh --full
```

Expected terminal marker: `NATIVE_RUN_OK`.

Acceptance criteria:

```text
completion.json: successful_cells = 32, failed_cells = 0, full_matrix_complete = true
revalidation.json: valid = true
analysis/: per_seed.csv, summary.json, REPORT.md
SHA256SUMS.txt: present
```

No command in this repository produces a DOCX/PDF/ZIP manuscript artifact.
