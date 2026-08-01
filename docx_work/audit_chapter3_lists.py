#!/usr/bin/env python3
"""Fail-closed audit for Chapter 3 lists, body captions, and rendered pages."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from docx import Document


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\u00ad", "")).strip()


def page_text(pdf: Path, page: int) -> str:
    result = subprocess.run(
        ["pdftotext", "-f", str(page), "-l", str(page), str(pdf), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    return normalize(result.stdout)


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: audit_chapter3_lists.py FINAL.docx FINAL.pdf")
    docx, pdf = map(Path, sys.argv[1:])
    doc = Document(docx)
    paragraphs = [normalize(p.text) for p in doc.paragraphs]

    entries = [
        ("Bảng 3.1.", "Kết quả tái phân tích bốn mô hình cơ sở trên UCI404 bằng StratifiedGroupKFold (25 lượt đánh giá/mô hình).", 46),
        ("Bảng 3.2.", "Bốn kịch bản mô phỏng đối chứng.", 49),
        ("Bảng 3.3.", "Tác động của tấn công lên các chỉ số mạng (tám hạt giống).", 50),
        ("Bảng 3.4.", "Trạng thái kiểm toán bộ chuẩn đánh giá theo cửa sổ từ dấu vết nguyên bản và tiêu chí không suy biến.", 53),
        ("Bảng 3.5.", "Trạng thái bằng chứng cho đường cong phát hiện theo cường độ tấn công.", 53),
        ("Bảng 3.6.", "Thông lượng TCP hợp pháp theo bốn kịch bản direct-BHP (khoảng mô tả trên tám seed).", 55),
        ("Hình 3.1.", "Kết quả phép thử từng đặc trưng trên UCI404 dưới giao thức nhóm bản sao chính xác.", 46),
        ("Hình 3.2.", "Độ quan trọng hoán vị ngoài mẫu của các đặc trưng UCI404, dùng macro-F1 làm thước đo.", 47),
        ("Hình 3.3.", "Kiến trúc mục tiêu phát hiện–quyết định–ứng phó tại nút biên; ma trận hiện tại chỉ kiểm chứng cơ chế kiểm soát BHP trực tiếp trước khi đặt trước tài nguyên và hai cấu hình ứng phó.", 49),
        ("Hình 3.4.", "Tác động của BHP điều khiển trực tiếp không kèm chùm dữ liệu lên thông lượng TCP hợp pháp giữa S0 và S1 trên tám hạt giống ngẫu nhiên cố định.", 51),
        ("Hình 3.5.", "Số gói TCP hợp pháp theo từng hạt giống ngẫu nhiên trong bốn kịch bản; mỗi đường biểu diễn tám lượt chạy từ môi trường NS-2.35+nOBS nguyên bản.", 52),
        ("Hình 3.6.", "Phân bố các quyết định của cơ chế kiểm soát BHP trực tiếp theo hai cấu hình ứng phó, tổng hợp trên tám hạt giống ngẫu nhiên.", 54),
        ("Hình 3.7.", "Hiệu quả của hai cấu hình kiểm soát BHP trực tiếp trên tám hạt giống ngẫu nhiên cố định.", 56),
    ]

    failures: list[str] = []
    page_cache: dict[int, str] = {}
    for label, title, page in entries:
        exact = normalize(f"{label} {title}")
        list_exact = normalize(f"{label} {title}\t{page}")
        # python-docx returns tab-separated list paragraphs; normalization turns
        # tabs into spaces, so require the exact title followed by the page.
        if normalize(f"{exact} {page}") not in paragraphs:
            failures.append(f"missing/stale list entry: {label} -> {page}")
        if exact not in paragraphs:
            failures.append(f"missing body caption: {label}")
        page_cache.setdefault(page, page_text(pdf, page))
        # A stable short prefix avoids false failures from PDF line-breaking or
        # discretionary hyphenation while still binding label/title to the page.
        words = normalize(title).split()
        probe = normalize(f"{label} {' '.join(words[:8])}")
        if probe not in page_cache[page]:
            failures.append(f"caption not found on rendered page {page}: {label}")

    labels = [label for label, _, _ in entries]
    for label in labels:
        list_hits = [p for p in paragraphs if p.startswith(label) and re.search(r"\s\d+$", p)]
        body_hits = [p for p in paragraphs if p.startswith(label) and not re.search(r"\s\d+$", p)]
        if len(list_hits) != 1:
            failures.append(f"expected one list entry for {label}, found {len(list_hits)}")
        if len(body_hits) != 1:
            failures.append(f"expected one body caption for {label}, found {len(body_hits)}")

    if failures:
        raise AssertionError("CHAPTER3_LIST_AUDIT_FAILED\n- " + "\n- ".join(failures))
    print(f"CHAPTER3_LIST_AUDIT_OK entries={len(entries)} pages={len(page_cache)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
