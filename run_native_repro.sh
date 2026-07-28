#!/usr/bin/env bash
# Reproducible native NS-2.35+nOBS runner.
# Usage:
#   bash run_native_repro.sh --smoke
#   bash run_native_repro.sh --full
set -Eeuo pipefail
IFS=$'\n\t'

BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASE"
DIRECT="$BASE/experiments/direct_bhp"
MODE="${1:---smoke}"
STAMP="$(date +%Y%m%d_%H%M%S)"
OUT="$BASE/reproduction_runs/$STAMP/native_matrix"
LOG="$BASE/reproduction_runs/$STAMP/native_run.log"
mkdir -p "$(dirname "$LOG")"
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "NATIVE_RUN_FAILED exit=$rc line=$LINENO"; exit "$rc"' ERR

case "$MODE" in
  --smoke)
    SEED="${SEED:-101}"
    LABEL="${LABEL:-S2_rate_limit}"
    SELECT=(--seed "$SEED" --label "$LABEL")
    ;;
  --full)
    SELECT=()
    ;;
  *)
    echo "Usage: bash run_native_repro.sh [--smoke|--full]" >&2
    exit 2
    ;;
esac

NS="${NOBS_NS_TREE:-$BASE/build/ns-allinone-2.35/ns-2.35}/ns"
[[ -x "$NS" ]] || {
  echo "NATIVE_BINARY_MISSING: $NS" >&2
  echo "Set NOBS_NS_TREE to a provisioned native NS-2.35 tree, then rerun." >&2
  exit 3
}
command -v python3 >/dev/null
mkdir -p "$OUT"

# The runner snapshots config and hashes NS, scenario, validator, parser and
# every native BHP source input into matrix_manifest.json and each run.json.
echo "mode=$MODE"
echo "output=$OUT"
echo "log=$LOG"
echo "native_ns=$NS"
python3 "$DIRECT/validator.py" --config "$DIRECT/config.json"
python3 "$DIRECT/runner.py" --config "$DIRECT/config.json" --out "$OUT" "${SELECT[@]}"

python3 "$DIRECT/validator.py" \
  --config "$OUT/experiment_config.snapshot.json" \
  --results "$OUT" \
  --output "$OUT/revalidation.json"

python3 - "$OUT" "$MODE" <<'PY'
import json, sys
from pathlib import Path
root = Path(sys.argv[1]); mode = sys.argv[2]
completion = json.loads((root / "completion.json").read_text())
validation = json.loads((root / "revalidation.json").read_text())
assert completion["complete"] is True
assert validation["valid"] is True
if mode == "--full":
    assert completion["full_matrix_complete"] is True
    assert completion["successful_cells"] == 32
    import subprocess
    subprocess.run([sys.executable, "experiments/direct_bhp/analyze_results.py", str(root), "--out", str(root / "analysis")], check=True)
print(json.dumps({
    "mode": mode,
    "cells": completion["successful_cells"],
    "full_matrix_complete": completion["full_matrix_complete"],
    "output": str(root),
}, indent=2))
PY

(
  find "$OUT" -type f ! -name SHA256SUMS.txt -print0 | sort -z | xargs -0 sha256sum > "$OUT/SHA256SUMS.txt"
)
echo "NATIVE_RUN_OK"
echo "output=$OUT"
echo "log=$LOG"
