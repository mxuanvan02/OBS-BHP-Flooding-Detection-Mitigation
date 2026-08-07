"""Fix TOC styles and convert static List-of-Tables/Figures to real HYPERLINK+PAGEREF fields.

Run after rebuild_direct_docx.py produces the output DOCX.
Modifies the DOCX in-place (with backup).
"""
import zipfile, re, shutil, hashlib
from pathlib import Path
from lxml import etree

BASE = Path(__file__).resolve().parents[1]
DOCX = BASE / "LuanVan_ThS_NguyenQuangTin_CAPNHAT_KETQUA_NS2_20260726.docx"
assert DOCX.is_file(), f"DOCX not found: {DOCX}"

# Hardcoded mapping: (list_para_idx, body_caption_idx, bookmark_name)
# list_para_idx  = index of the static text line in Danh muc Bang/Hinh
# body_caption_idx = index of the real caption paragraph in the body
MAPPING = [
    (12, 127, "bang_1_1"),
    (13, 309, "bang_2_1"),
    (14, 345, "bang_3_1"),
    (15, 368, "bang_3_2"),
    (16, 373, "bang_3_3"),
    (17, 385, "bang_3_4"),
    (18, 388, "bang_3_5"),
    (19, 396, "bang_3_6"),
    (22, 105, "hinh_1_1"),
    (23, 116, "hinh_1_2"),
    (24, 146, "hinh_1_3"),
    (25, 150, "hinh_1_4"),
    (26, 160, "hinh_1_5"),
    (27, 170, "hinh_1_6"),
    (28, 173, "hinh_1_7"),
    (29, 179, "hinh_1_8"),
    (30, 185, "hinh_1_9"),
    (31, 207, "hinh_1_10"),
    (32, 264, "hinh_2_1"),
    (33, 318, "hinh_2_2"),
    (34, 350, "hinh_3_1"),
    (35, 353, "hinh_3_2"),
    (36, 364, "hinh_3_3"),
    (37, 375, "hinh_3_4"),
    (38, 379, "hinh_3_5"),
    (39, 391, "hinh_3_6"),
    (40, 398, "hinh_3_7"),
]

W  = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R  = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL_HYPERLINK = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink"

def qn(tag):
    ns, local = tag.split(":")
    return "{%s}%s" % ({"w": W, "r": R}[ns], local)

# ── 1. Parse document.xml and styles.xml from zip ────────────────────────────
backup = DOCX.with_suffix(".bak-fixtoc-20260807.docx")
shutil.copy2(DOCX, backup)
print("Backup:", backup)

with zipfile.ZipFile(DOCX) as z:
    doc_xml  = z.read("word/document.xml")
    sty_xml  = z.read("word/styles.xml")
    rel_xml  = z.read("word/_rels/document.xml.rels")
    members  = z.infolist()
    all_data = {m.filename: z.read(m.filename) for m in members}

doc_tree = etree.fromstring(doc_xml)
sty_tree = etree.fromstring(sty_xml)
rel_tree = etree.fromstring(rel_xml)

# ── 2. Collect all <w:p> elements in document order ──────────────────────────
body = doc_tree.find(".//{%s}body" % W)
all_paras = body.findall(".//{%s}p" % W)
print(f"Total paragraphs in body: {len(all_paras)}")

# ── 3. Add TOC1/TOC2/TOC3 + Hyperlink styles to styles.xml ──────────────────
existing_style_ids = {
    s.get(qn("w:styleId"))
    for s in sty_tree.findall("{%s}style" % W)
}

TOC_STYLES = """
<w:style xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
         w:type="paragraph" w:styleId="{sid}">
  <w:name w:val="{name}"/>
  <w:basedOn w:val="Normal"/>
  <w:uiPriority w:val="39"/>
  <w:pPr>
    <w:tabs>
      <w:tab w:val="right" w:pos="8787" w:leader="dot"/>
    </w:tabs>
    <w:spacing w:line="360" w:lineRule="auto" w:after="120"/>
    <w:ind w:left="{indent}"/>
  </w:pPr>
  <w:rPr>
    <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
    <w:sz w:val="26"/>
  </w:rPr>
</w:style>
"""

HYPERLINK_STYLE = """
<w:style xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
         w:type="character" w:styleId="Hyperlink">
  <w:name w:val="Hyperlink"/>
  <w:basedOn w:val="DefaultParagraphFont"/>
  <w:uiPriority w:val="99"/>
  <w:unhideWhenUsed/>
  <w:rPr>
    <w:color w:val="000000" w:themeColor="text1"/>
    <w:u w:val="none"/>
  </w:rPr>
</w:style>
"""

toc_defs = [
    ("TOC1", "toc 1", "0"),
    ("TOC2", "toc 2", "216"),
    ("TOC3", "toc 3", "432"),
]

added = 0
for sid, name, indent in toc_defs:
    if sid not in existing_style_ids:
        xml = TOC_STYLES.format(sid=sid, name=name, indent=indent)
        node = etree.fromstring(xml.strip())
        sty_tree.append(node)
        added += 1
        print(f"  Added style: {sid}")

if "Hyperlink" not in existing_style_ids:
    node = etree.fromstring(HYPERLINK_STYLE.strip())
    sty_tree.append(node)
    added += 1
    print("  Added style: Hyperlink")

print(f"Styles added: {added}")

# ── 4. Insert bookmarks into body caption paragraphs ─────────────────────────
body_idxs_to_bm = {body_idx: bm for (_, body_idx, bm) in MAPPING}

for body_idx, bm_name in body_idxs_to_bm.items():
    p = all_paras[body_idx]
    # Check if bookmark already exists
    existing = p.find(".//{%s}bookmarkStart" % W)
    if existing is not None:
        continue
    # Insert bookmarkStart before first run, bookmarkEnd after last run
    runs = p.findall("{%s}r" % W)
    first_run = runs[0] if runs else None
    bm_start = etree.Element(qn("w:bookmarkStart"))
    bm_start.set(qn("w:id"), str(body_idx))
    bm_start.set(qn("w:name"), bm_name)
    bm_end = etree.Element(qn("w:bookmarkEnd"))
    bm_end.set(qn("w:id"), str(body_idx))
    if first_run is not None:
        first_run.addprevious(bm_start)
    else:
        p.insert(0, bm_start)
    p.append(bm_end)
    print(f"  Bookmark '{bm_name}' -> para#{body_idx}")

# ── 5. Convert static list entries to HYPERLINK + PAGEREF fields ──────────────
# Field structure for each list entry:
#   <w:hyperlink w:anchor="bm_name">
#     <w:r><w:rPr>...</w:rPr><w:t>Label text</w:t></w:r>
#     <w:r><w:rPr>...</w:rPr><w:tab/></w:r>
#     <w:r><w:fldChar w:fldCharType="begin"/></w:r>
#     <w:r><w:instrText> PAGEREF bm_name \h </w:instrText></w:r>
#     <w:r><w:fldChar w:fldCharType="separate"/></w:r>
#     <w:r><w:t>??</w:t></w:r>
#     <w:r><w:fldChar w:fldCharType="end"/></w:r>
#   </w:hyperlink>

def make_rpr():
    rpr = etree.Element(qn("w:rPr"))
    fonts = etree.SubElement(rpr, qn("w:rFonts"))
    fonts.set(qn("w:ascii"), "Times New Roman")
    fonts.set(qn("w:hAnsi"), "Times New Roman")
    fonts.set(qn("w:cs"), "Times New Roman")
    sz = etree.SubElement(rpr, qn("w:sz"))
    sz.set(qn("w:val"), "26")
    return rpr

def make_run_text(text):
    r = etree.Element(qn("w:r"))
    r.append(make_rpr())
    t = etree.SubElement(r, qn("w:t"))
    t.text = text
    if text.startswith(" ") or text.endswith(" "):
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    return r

def make_run_tab():
    r = etree.Element(qn("w:r"))
    r.append(make_rpr())
    etree.SubElement(r, qn("w:tab"))
    return r

def make_run_fldchar(kind):
    r = etree.Element(qn("w:r"))
    r.append(make_rpr())
    fc = etree.SubElement(r, qn("w:fldChar"))
    fc.set(qn("w:fldCharType"), kind)
    return r

def make_run_instr(text):
    r = etree.Element(qn("w:r"))
    r.append(make_rpr())
    instr = etree.SubElement(r, qn("w:instrText"))
    instr.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    instr.text = text
    return r

converted = 0
for list_idx, body_idx, bm_name in MAPPING:
    p = all_paras[list_idx]
    # Get current label text: walk each <w:r>'s children in document order
    # and stop collecting as soon as a <w:tab/> element is reached. The old
    # page number lives in a <w:t> AFTER the <w:tab/>, so it must be excluded.
    label_parts = []
    hit_tab = False
    for run in p.findall("{%s}r" % W):
        if hit_tab:
            break
        for child in run:
            tag = etree.QName(child).localname
            if tag == "tab":
                hit_tab = True
                break
            if tag == "t":
                label_parts.append(child.text or "")
    label_text = "".join(label_parts)

    # Build hyperlink element
    hl = etree.Element(qn("w:hyperlink"))
    hl.set(qn("w:anchor"), bm_name)
    hl.append(make_run_text(label_text))
    hl.append(make_run_tab())
    hl.append(make_run_fldchar("begin"))
    hl.append(make_run_instr(f" PAGEREF {bm_name} \\h "))
    hl.append(make_run_fldchar("separate"))
    hl.append(make_run_text("??"))
    hl.append(make_run_fldchar("end"))

    # Replace paragraph content: remove all children, add pPr back, then hyperlink
    pPr = p.find("{%s}pPr" % W)
    for child in list(p):
        p.remove(child)
    if pPr is not None:
        p.append(pPr)
    p.append(hl)
    converted += 1

print(f"List entries converted to HYPERLINK+PAGEREF: {converted}")

# ── 6. Write updated zip ──────────────────────────────────────────────────────
new_doc_xml  = etree.tostring(doc_tree,  xml_declaration=True, encoding="UTF-8", standalone=True)
new_sty_xml  = etree.tostring(sty_tree,  xml_declaration=True, encoding="UTF-8", standalone=True)

tmp = DOCX.with_suffix(".tmp-fixtoc.docx")
with zipfile.ZipFile(DOCX) as zin:
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename == "word/document.xml":
                zout.writestr(item, new_doc_xml)
            elif item.filename == "word/styles.xml":
                zout.writestr(item, new_sty_xml)
            else:
                zout.writestr(item, zin.read(item.filename))

tmp.replace(DOCX)
print(f"Done. DOCX updated: {DOCX}")
print(f"SHA256: {hashlib.sha256(DOCX.read_bytes()).hexdigest()}")
