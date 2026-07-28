#!/usr/bin/env python3
"""Build and verify the figure lineage manifest for the final thesis DOCX."""
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: build_figure_lineage_manifest.py FINAL.docx OUTPUT_DIR")

    docx = Path(sys.argv[1]).resolve()
    out_dir = Path(sys.argv[2]).resolve()
    base = Path(__file__).resolve().parents[1]
    out_dir.mkdir(parents=True, exist_ok=True)

    generator = base / "docx_work/rebuild_direct_docx.py"
    canonical_summary = base / "evidence/direct_bhp_matrix/summary.json"
    canonical_per_seed = base / "evidence/direct_bhp_matrix/per_seed.csv"
    uci_root = base.parent / "obs_repro/source_only/uci404/outputs"
    uci_manifest_path = uci_root / "output_manifest.json"
    original_docx = base / "deliverables/LuanVan_ThS_NguyenQuangTin_BAN_GOC_01072026.docx"

    required = [docx, generator, canonical_summary, canonical_per_seed, uci_manifest_path, original_docx]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise AssertionError(f"missing lineage inputs: {missing}")

    uci_manifest = json.loads(uci_manifest_path.read_text(encoding="utf-8"))
    for item in uci_manifest["files"]:
        path = uci_root / item["path"]
        assert path.is_file(), path
        assert sha256(path) == item["sha256"], f"UCI manifest mismatch: {path}"

    expected_media = {
        "3.1": ("word/media/image24.png", uci_root / "figures/single_feature_audit.png"),
        "3.2": ("word/media/image25.png", uci_root / "figures/rf_oof_permutation_importance.png"),
        "3.4": ("word/media/image26.png", base / "docx_work/figure_3_4_direct.png"),
        "3.5": ("word/media/image27.png", base / "docx_work/figure_3_5_scope.png"),
        "3.6": ("word/media/image28.png", base / "docx_work/figure_3_6_evidence_gap.png"),
        "3.7": ("word/media/image29.png", base / "docx_work/figure_3_7_direct.png"),
    }

    with zipfile.ZipFile(docx) as archive:
        final_media = {name: archive.read(name) for name in archive.namelist() if name.startswith("word/media/")}
    with zipfile.ZipFile(original_docx) as archive:
        original_media = {name: archive.read(name) for name in archive.namelist() if name.startswith("word/media/")}

    entries: list[dict] = []
    for number, (member, output_path) in expected_media.items():
        assert output_path.is_file(), output_path
        assert member in final_media, f"missing embedded media: {member}"
        output_hash = sha256(output_path)
        embedded_hash = hashlib.sha256(final_media[member]).hexdigest()
        assert output_hash == embedded_hash, f"embedded figure mismatch: Hình {number}"

        if number == "3.1":
            sources = [
                uci_root / "raw/single_feature_fold_metrics.csv",
                uci_root / "summary/single_feature_summary.csv",
            ]
            category = "experimental-result"
            generator_path = base.parent / "obs_repro/source_only/uci404/pipeline.py"
        elif number == "3.2":
            sources = [
                uci_root / "raw/rf_oof_permutation_fold.csv",
                uci_root / "summary/rf_permutation_importance_summary.csv",
            ]
            category = "experimental-result"
            generator_path = base.parent / "obs_repro/source_only/uci404/pipeline.py"
        elif number in {"3.4", "3.7"}:
            sources = [canonical_summary]
            category = "experimental-result"
            generator_path = generator
        else:
            sources = [canonical_per_seed]
            category = "experimental-result"
            generator_path = generator

        assert generator_path.is_file(), generator_path
        entries.append({
            "figure": number,
            "category": category,
            "docx_member": member,
            "embedded_sha256": embedded_hash,
            "output_file": str(output_path.relative_to(base.parent)),
            "output_sha256": output_hash,
            "generator": str(generator_path.relative_to(base.parent)),
            "generator_sha256": sha256(generator_path),
            "sources": [
                {
                    "path": str(source.relative_to(base.parent)),
                    "sha256": sha256(source),
                }
                for source in sources
            ],
            "gate": "PASS",
        })

    # Hình 3.3 is intentionally an architecture diagram, not an experimental result.
    architecture_member = "word/media/image23.png"
    assert architecture_member in final_media, architecture_member
    assert architecture_member in original_media, architecture_member
    architecture_hash = hashlib.sha256(final_media[architecture_member]).hexdigest()
    original_architecture_hash = hashlib.sha256(original_media[architecture_member]).hexdigest()
    assert architecture_hash == original_architecture_hash, "architecture figure unexpectedly changed"
    entries.insert(2, {
        "figure": "3.3",
        "category": "conceptual-architecture",
        "docx_member": architecture_member,
        "embedded_sha256": architecture_hash,
        "source": str(original_docx.relative_to(base)),
        "source_sha256": sha256(original_docx),
        "experimental_result": False,
        "gate": "PASS (explicitly non-experimental)",
    })

    payload = {
        "schema": "thesis-figure-lineage-v1",
        "document": str(docx),
        "document_sha256": sha256(docx),
        "policy": "Hình 3.1–3.2 and 3.4–3.7 must be generated from declared experiment outputs; Hình 3.3 is explicitly conceptual architecture.",
        "all_gates_pass": True,
        "figures": entries,
    }
    json_path = out_dir / "FIGURE_LINEAGE.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# MANIFEST NGUỒN GỐC HÌNH CHƯƠNG 3",
        "",
        "- Hình 3.1–3.2 và 3.4–3.7: sinh từ đầu ra thực nghiệm được khai báo và đã đối chiếu SHA-256 với ảnh nhúng trong DOCX.",
        "- Hình 3.3: sơ đồ kiến trúc khái niệm, không phải biểu đồ kết quả thực nghiệm.",
        "",
        "| Hình | Loại | Nguồn chính | Trạng thái |",
        "|---|---|---|---|",
    ]
    for item in entries:
        if item["figure"] == "3.3":
            source = item["source"]
        else:
            source = ", ".join(source["path"] for source in item["sources"])
        lines.append(f"| {item['figure']} | {item['category']} | `{source}` | {item['gate']} |")
    lines.extend(["", f"DOCX SHA-256: `{payload['document_sha256']}`", ""])
    (out_dir / "FIGURE_LINEAGE.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"FIGURE_LINEAGE_GATE_OK figures={len(entries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
