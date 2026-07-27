from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile
from lxml import etree
from docx import Document

BASE = Path(__file__).resolve().parent
DOCX = BASE / "LuanVan_ThS_NguyenQuangTin_CAPNHAT_KETQUA_NS2_20260726.docx"
NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

with ZipFile(DOCX) as archive:
    media = sorted(name for name in archive.namelist() if name.startswith("word/media/"))
    rel_root = etree.fromstring(archive.read("word/_rels/document.xml.rels"))
    relmap = {}
    for rel in rel_root:
        target = rel.get("Target", "")
        if target.startswith("media/"):
            relmap[rel.get("Id")] = "word/" + target
    root = etree.fromstring(archive.read("word/document.xml"))
    print("MEDIA_COUNT", len(media))
    for name in media:
        data = archive.read(name)
        print("MEDIA", name, sha256(data).hexdigest(), len(data))
    print("DRAWINGS_BY_PARAGRAPH")
    body_paragraphs = root.xpath(".//w:body/w:p", namespaces=NS)
    for index, node in enumerate(body_paragraphs):
        text = "".join(node.xpath(".//w:t/text()", namespaces=NS)).strip()
        embeds = node.xpath(".//a:blip/@r:embed", namespaces=NS)
        if embeds:
            print("DRAWING", index, repr(text[:120]), [(rid, relmap.get(rid)) for rid in embeds])

print("CAPTIONS")
document = Document(DOCX)
for index, paragraph in enumerate(document.paragraphs):
    text = paragraph.text.strip()
    if text.startswith(("Hình 3.", "Bảng 3.")):
        print("CAPTION", index, text)
