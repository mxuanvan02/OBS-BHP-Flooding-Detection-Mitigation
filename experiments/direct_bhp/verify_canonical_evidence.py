#!/usr/bin/env python3
"""Verify the compact, trace-free canonical direct-BHP evidence bundle.

The checker is deliberately fail-closed: it accepts only a v2 validation
record whose provenance hash chain matches the retained compact artifacts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

LABELS = {"S0", "S1", "S2_rate_limit", "S2_isolation"}
SEEDS = {101, 202, 303, 404, 505, 606, 707, 808}
REQUIRED = {
    "completion.json", "experiment_config.snapshot.json", "matrix_manifest.json",
    "per_seed.csv", "REPORT.md", "summary.json", "validation.json", "validation.rerun.json",
}


def load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"CANONICAL_EVIDENCE_INVALID: cannot read {path}: {exc}") from exc


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"CANONICAL_EVIDENCE_INVALID: {message}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=Path("evidence/direct_bhp_matrix"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    root = args.evidence.resolve()
    missing = sorted(name for name in REQUIRED if not (root / name).is_file())
    if missing:
        fail("missing required files: " + ", ".join(missing))

    completion = load(root / "completion.json")
    if not (completion.get("complete") is True and completion.get("full_matrix_complete") is True
            and completion.get("successful_cells") == 32 and completion.get("failed_cells") == 0):
        fail("completion is not an accepted 32/32 matrix")

    validation_path = root / "validation.rerun.json"
    validation = load(validation_path)
    primary_validation_path = root / "validation.json"
    primary_validation = load(primary_validation_path)
    cells = validation.get("cells", {})
    expected_cells = {f"seed_{seed}/{label}" for seed in SEEDS for label in LABELS}
    if (validation.get("schema") != "nobs-direct-bhp-validation-v2"
            or validation.get("valid") is not True
            or validation.get("selected_cells_complete") is not True
            or validation.get("full_matrix_complete") is not True
            or validation.get("expected_selected_cells") != 32
            or set(cells) != expected_cells):
        fail("retained revalidation is not a valid v2 complete 32-cell matrix")
    if digest(primary_validation_path) != digest(validation_path):
        fail("validation.json and validation.rerun.json differ")
    if primary_validation.get("schema") != "nobs-direct-bhp-validation-v2":
        fail("validation.json is not a v2 validation record")

    provenance = validation.get("provenance")
    hashes = validation.get("hashes")
    if not isinstance(provenance, dict) or not isinstance(hashes, dict):
        fail("v2 validation lacks provenance hashes")
    retained_hashes = {
        "completion.json": digest(root / "completion.json"),
        "matrix_manifest.json": digest(root / "matrix_manifest.json"),
        "experiment_config.snapshot.json": digest(root / "experiment_config.snapshot.json"),
    }
    provenance_keys = {
        "completion.json": "completion_sha256",
        "matrix_manifest.json": "matrix_manifest_sha256",
        "experiment_config.snapshot.json": "experiment_config_snapshot_sha256",
    }
    for filename, actual_hash in retained_hashes.items():
        if provenance.get(provenance_keys[filename]) != actual_hash:
            fail(f"v2 provenance does not bind {filename}")
        if hashes.get(filename) != actual_hash:
            fail(f"v2 hash index does not bind {filename}")
    engine_hash = provenance.get("validation_engine_sha256")
    if not isinstance(engine_hash, str) or hashes.get("validation_engine") != engine_hash:
        fail("v2 validation-engine provenance is missing or inconsistent")
    verified_cells = provenance.get("verified_cells")
    if not isinstance(verified_cells, dict) or set(verified_cells) != expected_cells:
        fail("v2 provenance does not cover every expected cell")
    if not isinstance(provenance.get("verified_input_sha256"), dict) or not provenance["verified_input_sha256"]:
        fail("v2 provenance lacks verified input hashes")

    manifest = load(root / "matrix_manifest.json")
    selected_cells = manifest.get("selected_cells")
    selected_keys = {
        f"seed_{cell.get('seed')}/{cell.get('label')}"
        for cell in selected_cells
    } if isinstance(selected_cells, list) else set()
    if (manifest.get("expected_selected_cells") != 32
            or manifest.get("full_matrix_requested") is not True
            or selected_keys != expected_cells):
        fail("matrix manifest does not declare the expected full matrix")

    summary = load(root / "summary.json")
    validation_sha256 = digest(validation_path)
    if summary.get("source_validation_sha256") != validation_sha256:
        fail("summary.json does not bind to validation.rerun.json")
    if set(summary.get("seeds", [])) != SEEDS:
        fail("summary.json seed set does not match the declared matrix")

    result = {
        "schema": "nobs-direct-bhp-canonical-evidence-check-v2",
        "evidence": str(root),
        "valid": True,
        "cells": 32,
        "validation_engine_sha256": engine_hash,
        "validation_rerun_sha256": validation_sha256,
        "summary_sha256": digest(root / "summary.json"),
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    print("CANONICAL_EVIDENCE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
