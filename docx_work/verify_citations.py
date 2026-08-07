"""Open the DOCX via LibreOffice UNO, update all document indexes (TOC),
save, and export a verification PDF into docx_work/toc_verify4/.

Must run with the system LibreOffice-linked Python (/usr/bin/python3),
against an already-running soffice UNO listener on port 2002.
"""
import time
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DOCX = BASE / "LuanVan_ThS_NguyenQuangTin_CAPNHAT_KETQUA_NS2_20260726.docx"
OUT_PDF_DIR = BASE / "docx_work" / "toc_verify4"
OUT_PDF_DIR.mkdir(exist_ok=True)

import uno
from com.sun.star.beans import PropertyValue


def make_prop(name, value):
    p = PropertyValue()
    p.Name = name
    p.Value = value
    return p


def connect(retries=20, delay=1.0):
    local_ctx = uno.getComponentContext()
    resolver = local_ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", local_ctx
    )
    last_err = None
    for _ in range(retries):
        try:
            ctx = resolver.resolve(
                "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext"
            )
            return ctx
        except Exception as e:
            last_err = e
            time.sleep(delay)
    raise RuntimeError("Could not connect to soffice: %s" % last_err)


def main():
    ctx = connect()
    smgr = ctx.ServiceManager
    desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)

    url = uno.systemPathToFileUrl(str(DOCX))
    load_props = (make_prop("Hidden", True),)
    doc = desktop.loadComponentFromURL(url, "_blank", 0, load_props)

    indexes = doc.getDocumentIndexes()
    count = indexes.getCount()
    print("Document indexes found:", count)
    i = 0
    while i < count:
        idx = indexes.getByIndex(i)
        idx.update()
        print("  Updated index #%d: %s" % (i, idx.getName()))
        i = i + 1

    doc.store()
    print("Saved DOCX with updated TOC field.")

    pdf_path = OUT_PDF_DIR / (DOCX.stem + ".pdf")
    pdf_url = uno.systemPathToFileUrl(str(pdf_path))
    export_props = (make_prop("FilterName", "writer_pdf_Export"),)
    doc.storeToURL(pdf_url, export_props)
    print("Exported PDF:", pdf_path)

    doc.close(False)


if __name__ == "__main__":
    main()
