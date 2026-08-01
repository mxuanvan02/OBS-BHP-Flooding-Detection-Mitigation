#!/usr/bin/env bash
# Run the OBS/BHP experiment, validation, figures, DOCX and PDF pipeline.
# Usage:
#   bash run_pipeline.sh --full             # rerun all 32 NS-2.35+nOBS cells
#   bash run_pipeline.sh --reuse-canonical  # reuse the validated canonical 32-cell matrix
set -Eeuo pipefail
IFS=$'\n\t'

BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIRECT="$BASE/experiments/direct_bhp"
CANONICAL="$BASE/evidence/direct_bhp_matrix"
SOURCE_DOCX="$BASE/deliverables/LuanVan_ThS_NguyenQuangTin_CAPNHAT_KETQUA_NS2_20260726.docx"
ORIGINAL_DOCX="$BASE/deliverables/LuanVan_ThS_NguyenQuangTin_BAN_GOC_01072026.docx"
ORIGINAL_SHA256="a5cb463bd902422cee6e3e243157b238de02aedab4b881c957cd0b650480637e"
NORMAL_DOCX="$BASE/LuanVan_ThS_NguyenQuangTin_CAPNHAT_KETQUA_NS2_20260726.docx"
HIGHLIGHT_DOCX="$BASE/LuanVan_ThS_NguyenQuangTin_CAPNHAT_KETQUA_NS2_20260726_HIGHLIGHT.docx"
MODE="${1:---full}"
STAMP="$(date +%Y%m%d_%H%M%S)"
RUN_ROOT="$BASE/reproduction_runs/$STAMP"
LOG="$RUN_ROOT/pipeline.log"

case "$MODE" in
  --full|--reuse-canonical) ;;
  *) echo "Usage: bash run_pipeline.sh [--full|--reuse-canonical]" >&2; exit 2 ;;
esac

mkdir -p "$RUN_ROOT"
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "PIPELINE_FAILED exit=$rc line=$LINENO"; exit "$rc"' ERR

require_file() {
  [[ -f "$1" ]] || { echo "Missing required file: $1" >&2; exit 3; }
}

require_file "$DIRECT/config.json"
require_file "$DIRECT/runner.py"
require_file "$DIRECT/validator.py"
require_file "$DIRECT/analyze_results.py"
require_file "$SOURCE_DOCX"
require_file "$ORIGINAL_DOCX"
[[ "$(sha256sum "$ORIGINAL_DOCX" | awk '{print $1}')" == "$ORIGINAL_SHA256" ]] || {
  echo "Original DOCX hash mismatch: $ORIGINAL_DOCX" >&2
  exit 4
}
require_file "$BASE/docx_work/rebuild_direct_docx.py"
require_file "$BASE/docx_work/audit_docx_highlights.py"
require_file "$BASE/docx_work/validate_updated_docx.py"
require_file "$BASE/docx_work/final_integrity_check.py"
require_file "$BASE/docx_work/build_figure_lineage_manifest.py"
require_file "$BASE/docx_work/audit_chapter3_lists.py"
command -v python3 >/dev/null
command -v libreoffice >/dev/null
command -v pdfinfo >/dev/null
command -v pdftotext >/dev/null

echo "[1/7] Select or reproduce native 32-cell matrix"
if [[ "$MODE" == "--full" ]]; then
  MATRIX="$RUN_ROOT/native_matrix"
  python3 "$DIRECT/runner.py" --config "$DIRECT/config.json" --out "$MATRIX"
else
  MATRIX="$CANONICAL"
fi

require_file "$MATRIX/completion.json"
require_file "$MATRIX/validation.json"

# Full mode revalidates retained traces and causal chains. Reuse mode verifies the
# packaged, previously validated evidence without pretending raw traces are present.
echo "[2/7] Fail-closed validation"
if [[ "$MODE" == "--full" ]]; then
  python3 "$DIRECT/validator.py" \
    --config "$DIRECT/config.json" \
    --results "$MATRIX" \
    --output "$RUN_ROOT/validation.rerun.json"
else
  require_file "$MATRIX/validation.rerun.json"
  cp -a "$MATRIX/validation.rerun.json" "$RUN_ROOT/validation.rerun.json"
fi
python3 - "$MATRIX/completion.json" "$RUN_ROOT/validation.rerun.json" <<'PY'
import json, sys
completion = json.load(open(sys.argv[1], encoding="utf-8"))
validation = json.load(open(sys.argv[2], encoding="utf-8"))
assert completion.get("complete") is True
assert completion.get("full_matrix_complete") is True
assert completion.get("successful_cells") == 32
assert completion.get("failed_cells") == 0
assert validation.get("valid") is True
assert validation.get("full_matrix_complete") is True
assert validation.get("expected_selected_cells") == 32
assert len(validation.get("cells", {})) == 32
print("NATIVE_MATRIX_GATE_OK cells=32/32")
PY

# Analyze raw results in full mode. Reuse mode copies the packaged canonical
# statistics, preserving the distinction between reproducibility evidence and raw traces.
echo "[3/7] Statistics and canonical consistency gate"
mkdir -p "$RUN_ROOT/analysis"
if [[ "$MODE" == "--full" ]]; then
  python3 "$DIRECT/analyze_results.py" "$MATRIX" --out "$RUN_ROOT/analysis"
else
  require_file "$CANONICAL/summary.json"
  require_file "$CANONICAL/per_seed.csv"
  require_file "$CANONICAL/REPORT.md"
  cp -a "$CANONICAL/summary.json" "$RUN_ROOT/analysis/summary.json"
  cp -a "$CANONICAL/per_seed.csv" "$RUN_ROOT/analysis/per_seed.csv"
  cp -a "$CANONICAL/REPORT.md" "$RUN_ROOT/analysis/REPORT.md"
fi
python3 - "$RUN_ROOT/analysis/summary.json" "$CANONICAL/summary.json" <<'PY'
import json, math, sys
new = json.load(open(sys.argv[1], encoding="utf-8"))
ref = json.load(open(sys.argv[2], encoding="utf-8"))
keys = ("S0", "S1", "S2_rate_limit", "S2_isolation")
metrics = ("legal_tcp_packets", "legal_tcp_bytes", "optical_burst_pairs", "successful_link_reservations")
for label in keys:
    for metric in metrics:
        a = new["summary"][label][metric]["mean"]
        b = ref["summary"][label][metric]["mean"]
        assert math.isclose(a, b, rel_tol=0, abs_tol=1e-9), (label, metric, a, b)
for key, value in ref["effects"].items():
    if isinstance(value, (int, float)):
        assert math.isclose(new["effects"][key], value, rel_tol=0, abs_tol=1e-9), key
print("CANONICAL_METRICS_GATE_OK")
PY

# Preserve current outputs before the deterministic rebuild script overwrites them.
echo "[4/7] Generate figures and rebuild DOCX"
BACKUP="$RUN_ROOT/pre_rebuild_backup"
mkdir -p "$BACKUP"
[[ ! -f "$NORMAL_DOCX" ]] || cp -a "$NORMAL_DOCX" "$BACKUP/"
[[ ! -f "$HIGHLIGHT_DOCX" ]] || cp -a "$HIGHLIGHT_DOCX" "$BACKUP/"
python3 "$BASE/docx_work/rebuild_direct_docx.py"
python3 "$BASE/docx_work/validate_updated_docx.py" "$NORMAL_DOCX"
python3 "$BASE/docx_work/final_integrity_check.py"
python3 "$BASE/docx_work/audit_docx_highlights.py" \
  "$ORIGINAL_DOCX" "$NORMAL_DOCX" "$HIGHLIGHT_DOCX" \
  > "$RUN_ROOT/highlight_audit.json"
python3 - "$RUN_ROOT/highlight_audit.json" <<'PY'
import json, sys
result = json.load(open(sys.argv[1], encoding="utf-8"))
assert result.get("complete") is True, result
assert not result.get("missing_paragraph_marks"), result
assert not result.get("missing_cell_marks"), result
assert not result.get("missing_media_marks"), result
print("HIGHLIGHT_AUDIT_GATE_OK")
PY
require_file "$BASE/docx_work/figure_3_4_direct.png"
require_file "$BASE/docx_work/figure_3_5_scope.png"
require_file "$BASE/docx_work/figure_3_6_evidence_gap.png"
require_file "$BASE/docx_work/figure_3_7_direct.png"
python3 "$BASE/docx_work/build_figure_lineage_manifest.py" \
  "$NORMAL_DOCX" "$RUN_ROOT/figure_lineage"
require_file "$RUN_ROOT/figure_lineage/FIGURE_LINEAGE.json"
require_file "$RUN_ROOT/figure_lineage/FIGURE_LINEAGE.md"

# Render in an isolated LibreOffice profile so a desktop instance cannot hijack the job.
echo "[5/7] Render final DOCX to PDF"
RENDER="$RUN_ROOT/rendered"
PROFILE="$RUN_ROOT/lo-profile"
mkdir -p "$RENDER" "$PROFILE"
libreoffice \
  -env:UserInstallation="file://$PROFILE" \
  --headless --convert-to pdf --outdir "$RENDER" "$NORMAL_DOCX"
PDF="$RENDER/${NORMAL_DOCX##*/}"
PDF="${PDF%.docx}.pdf"
require_file "$PDF"
pdfinfo "$PDF" > "$RUN_ROOT/pdfinfo.txt"
pdftotext "$PDF" "$RUN_ROOT/rendered.txt"

# Text, page, format and metadiscourse/obsolete-number gates.
echo "[6/7] Final artifact gates"
python3 - "$PDF" "$RUN_ROOT/pdfinfo.txt" "$RUN_ROOT/rendered.txt" <<'PY'
from pathlib import Path
import re, sys
pdf = Path(sys.argv[1]); info = Path(sys.argv[2]).read_text(errors="replace"); text = Path(sys.argv[3]).read_text(errors="replace")
assert pdf.stat().st_size > 1_000_000, pdf.stat().st_size
pages = int(re.search(r"^Pages:\s+(\d+)", info, re.M).group(1))
assert pages >= 60, pages
assert "A4" in info
required = ["48.678", "15.034,25", "15.633.620", "69,12%", "BHP điều khiển trực tiếp", "100% mức S0"]
missing = [x for x in required if x not in text]
assert not missing, f"missing rendered content: {missing}"
obsolete = ["82.568", "38.281", "3.426", "316,25", "90,77%", "40 Mb/s/nguồn"]
found = [x for x in obsolete if x in text]
assert not found, f"obsolete rendered content: {found}"
meta = [r"Vì đây là tiểu luận", r"tiểu luận cần", r"để người học hiểu", r"người đọc cần", r"cách đọc phần"]
hits = [p for p in meta if re.search(p, text, re.I)]
assert not hits, f"metadiscourse remains: {hits}"
print(f"FINAL_PDF_GATE_OK pages={pages} bytes={pdf.stat().st_size}")
PY
python3 "$BASE/docx_work/audit_chapter3_lists.py" "$NORMAL_DOCX" "$PDF"

# Copy a self-contained delivery set without altering the validated matrix.
echo "[7/7] Package deliverables"
DELIVERY="$RUN_ROOT/deliverables"
mkdir -p "$DELIVERY"
cp -a "$NORMAL_DOCX" "$HIGHLIGHT_DOCX" "$PDF" \
  "$BASE/docx_work/figure_3_4_direct.png" \
  "$BASE/docx_work/figure_3_5_scope.png" \
  "$BASE/docx_work/figure_3_6_evidence_gap.png" \
  "$BASE/docx_work/figure_3_7_direct.png" \
  "$RUN_ROOT/figure_lineage/FIGURE_LINEAGE.json" \
  "$RUN_ROOT/figure_lineage/FIGURE_LINEAGE.md" \
  "$RUN_ROOT/validation.rerun.json" "$RUN_ROOT/analysis/summary.json" \
  "$RUN_ROOT/analysis/REPORT.md" "$RUN_ROOT/pdfinfo.txt" \
  "$RUN_ROOT/highlight_audit.json" "$DELIVERY/"
(
  cd "$DELIVERY"
  sha256sum ./* > SHA256SUMS.txt
  sha256sum -c SHA256SUMS.txt
)

FINAL_ZIP="$BASE/deliverables/LuanVan_ThS_NguyenQuangTin_FINAL_NATIVE_DIRECT_BHP_${STAMP}.zip"
mkdir -p "$BASE/deliverables"
python3 - "$DELIVERY" "$FINAL_ZIP" <<'PY'
from pathlib import Path
import sys, zipfile
source, output = map(Path, sys.argv[1:])
with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for path in sorted(source.iterdir()):
        if path.is_file():
            archive.write(path, path.name)
with zipfile.ZipFile(output) as archive:
    bad = archive.testzip()
    assert bad is None, bad
    names = set(archive.namelist())
    required = {
        "LuanVan_ThS_NguyenQuangTin_CAPNHAT_KETQUA_NS2_20260726.docx",
        "LuanVan_ThS_NguyenQuangTin_CAPNHAT_KETQUA_NS2_20260726_HIGHLIGHT.docx",
        "LuanVan_ThS_NguyenQuangTin_CAPNHAT_KETQUA_NS2_20260726.pdf",
        "FIGURE_LINEAGE.json", "FIGURE_LINEAGE.md", "SHA256SUMS.txt",
    }
    assert required <= names, sorted(required - names)
print(f"ZIP_STRUCTURE_OK files={len(names)} bytes={output.stat().st_size}")
PY
TMP_EXTRACT="$RUN_ROOT/zip_verify"
mkdir -p "$TMP_EXTRACT"
unzip -q "$FINAL_ZIP" -d "$TMP_EXTRACT"
(
  cd "$TMP_EXTRACT"
  sha256sum -c SHA256SUMS.txt
)
cmp "$DELIVERY/${NORMAL_DOCX##*/}" "$TMP_EXTRACT/${NORMAL_DOCX##*/}"
cmp "$DELIVERY/${HIGHLIGHT_DOCX##*/}" "$TMP_EXTRACT/${HIGHLIGHT_DOCX##*/}"
cmp "$DELIVERY/${PDF##*/}" "$TMP_EXTRACT/${PDF##*/}"
cmp "$DELIVERY/FIGURE_LINEAGE.json" "$TMP_EXTRACT/FIGURE_LINEAGE.json"
echo "ZIP_FRESHNESS_GATE_OK sha256=$(sha256sum "$FINAL_ZIP" | awk '{print $1}')"

cat <<EOF
PIPELINE_OK
mode=$MODE
matrix=$MATRIX
run_root=$RUN_ROOT
deliverables=$DELIVERY
pdf=$PDF
zip=$FINAL_ZIP
log=$LOG
EOF
