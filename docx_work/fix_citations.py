"""Convert in-text bracket citations like [12] into real internal hyperlinks
that jump to the matching entry in TAI LIEU THAM KHAO (References).

Adds one bookmark per reference entry (ref_1 .. ref_38) and wraps each
in-text "[n]" occurrence in a <w:hyperlink w:anchor="ref_n"> pointing to it.
Visible text and formatting are unchanged; only structure gains real
Ctrl+click navigation, matching the approach already used for the
List-of-Tables / List-of-Figures fix.

Idempotent: a paragraph that already contains a hyperlink anchored to a
ref_* bookmark is skipped entirely on re-run; reference entries that
already have a bookmark are skipped too.

Run standalone, or automatically via rebuild_direct_docx.py.
"""
import re
import zipfile
import shutil
import hashlib
from pathlib import Path
from lxml import etree

BASE = Path(__file__).resolve().parents[1]
DOCX = BASE / "LuanVan_ThS_NguyenQuangTin_CAPNHAT_KETQUA_NS2_20260726.docx"
assert DOCX.is_file(), f"DOCX not found: {DOCX}"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def qn(tag):
    ns, local = tag.split(":")
    return "{%s}%s" % (W, local)


CITATION_RE = re.compile(r"\[(\d{1,2})\]")
MIN_REF = 1
MAX_REF = 38
REF_HEADING_TEXT = "TÀI LIỆU THAM KHẢO"


def ref_bookmark(n):
    return "ref_%d" % n


def copy_rpr(rpr_src):
    if rpr_src is None:
        return None
    return etree.fromstring(etree.tostring(rpr_src))


def make_text_run(text, rpr_src):
    r = etree.Element(qn("w:r"))
    rpr = copy_rpr(rpr_src)
    if rpr is not None:
        r.append(rpr)
    t = etree.SubElement(r, qn("w:t"))
    t.text = text
    if text != text.strip():
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    return r


def make_citation_hyperlink(text, n, rpr_src):
    hl = etree.Element(qn("w:hyperlink"))
    hl.set(qn("w:anchor"), ref_bookmark(n))
    hl.append(make_text_run(text, rpr_src))
    return hl


def split_run_by_citations(run):
    t_el = run.find(qn("w:t"))
    if t_el is None or not t_el.text:
        return None
    text = t_el.text
    matches = list(CITATION_RE.finditer(text))
    valid = [m for m in matches if MIN_REF <= int(m.group(1)) <= MAX_REF]
    if not valid:
        return None
    rpr_src = run.find(qn("w:rPr"))
    pieces = []
    cursor = 0
    for m in valid:
        before = text[cursor:m.start()]
        if before:
            pieces.append(make_text_run(before, rpr_src))
        n = int(m.group(1))
        pieces.append(make_citation_hyperlink(m.group(0), n, rpr_src))
        cursor = m.end()
    tail = text[cursor:]
    if tail:
        pieces.append(make_text_run(tail, rpr_src))
    return pieces


def main():
    backup = DOCX.with_suffix(".bak-fixcite-20260807.docx")
    shutil.copy2(DOCX, backup)
    print("Backup:", backup)

    with zipfile.ZipFile(DOCX) as z:
        doc_xml = z.read("word/document.xml")

    doc_tree = etree.fromstring(doc_xml)
    body = doc_tree.find(qn("w:body"))
    all_paras = body.findall(qn("w:p"))
    print("Total paragraphs:", len(all_paras))

    heading_idx = None
    for i, p in enumerate(all_paras):
        text = "".join(t.text or "" for t in p.iter(qn("w:t")))
        if REF_HEADING_TEXT in text:
            heading_idx = i
            break
    assert heading_idx is not None, "References heading not found"
    print("References heading at paragraph #%d" % heading_idx)

    entry_idxs = list(range(heading_idx + 1, len(all_paras)))
    bookmarked = 0
    for n, idx in enumerate(entry_idxs, start=1):
        if n > MAX_REF:
            break
        p = all_paras[idx]
        existing = p.find(".//" + qn("w:bookmarkStart"))
        if existing is not None:
            continue
        bm_start = etree.Element(qn("w:bookmarkStart"))
        bm_start.set(qn("w:id"), str(1000 + n))
        bm_start.set(qn("w:name"), ref_bookmark(n))
        bm_end = etree.Element(qn("w:bookmarkEnd"))
        bm_end.set(qn("w:id"), str(1000 + n))
        runs = p.findall(qn("w:r"))
        if runs:
            runs[0].addprevious(bm_start)
        else:
            p.insert(0, bm_start)
        p.append(bm_end)
        bookmarked += 1
    print("Reference bookmarks added:", bookmarked)

    converted = 0
    for p in all_paras[:heading_idx]:
        already_done = False
        for hl in p.findall(qn("w:hyperlink")):
            anchor = hl.get(qn("w:anchor")) or ""
            if anchor.startswith("ref_"):
                already_done = True
        if already_done:
            continue
        runs = p.findall(qn("w:r"))
        for run in runs:
            pieces = split_run_by_citations(run)
            if pieces is None:
                continue
            for piece in pieces:
                run.addprevious(piece)
            p.remove(run)
            converted += 1
    print("Runs converted to citation hyperlinks:", converted)

    new_doc_xml = etree.tostring(doc_tree, xml_declaration=True, encoding="UTF-8", standalone=True)

    tmp = DOCX.with_suffix(".tmp-fixcite.docx")
    with zipfile.ZipFile(DOCX) as zin:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == "word/document.xml":
                    zout.writestr(item, new_doc_xml)
                else:
                    zout.writestr(item, zin.read(item.filename))
    tmp.replace(DOCX)
    print("Done. DOCX updated:", DOCX)
    print("SHA256:", hashlib.sha256(DOCX.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
