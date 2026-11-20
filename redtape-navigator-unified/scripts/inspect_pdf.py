#!/usr/bin/env python3
"""Inspect a PDF form (AcroForm widgets or flat text anchors) with dual-backend support:
prefers PyMuPDF (fitz), gracefully falls back to pypdf + pdfplumber/pypdfium2.
Usage: python3 inspect_pdf.py form.pdf [--json] [--render out.png --page 0]
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _common import need

try:
    import fitz
    BACKEND = "pymupdf"
except ImportError:
    fitz = None
    try:
        import pypdf
        BACKEND = "pypdf"
    except ImportError:
        need("pymupdf or pypdf", "pymupdf pypdf")


def inspect(path):
    out = {"file": path, "backend": BACKEND, "coord_origin": "top-left", "pages": 0, "widgets": [], "anchors": []}
    if BACKEND == "pymupdf":
        doc = fitz.open(path)
        out["pages"] = len(doc)
        for pno, page in enumerate(doc):
            for w in page.widgets() or []:
                out["widgets"].append({
                    "page": pno,
                    "name": w.field_name,
                    "type": w.field_type_string,
                    "rect": [round(x, 1) for x in w.rect],
                    "value": w.field_value,
                })
            for b in page.get_text("blocks"):
                x0, y0, x1, y1, text = b[0], b[1], b[2], b[3], b[4].strip().replace("\n", " ")
                if text:
                    out["anchors"].append({
                        "page": pno, "x": round(x0, 1), "y": round(y0, 1),
                        "x1": round(x1, 1), "y1": round(y1, 1), "text": text[:80]
                    })
        out["kind"] = "acroform" if out["widgets"] else "flat"
        return out, doc

    # Fallback: pypdf (+ optional pdfplumber for flat text anchors)
    reader = pypdf.PdfReader(path)
    out["pages"] = len(reader.pages)
    fields = reader.get_fields() or {}
    for name, fobj in fields.items():
        ft = str(fobj.get("/FT", "Text"))
        val = fobj.get("/V", "")
        out["widgets"].append({"page": 0, "name": name, "type": ft, "rect": [], "value": str(val) if val else ""})
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            for pno, page in enumerate(pdf.pages):
                for w in (page.extract_words() or [])[:120]:
                    out["anchors"].append({
                        "page": pno, "x": round(w["x0"], 1), "y": round(w["top"], 1),
                        "x1": round(w["x1"], 1), "y1": round(w["bottom"], 1), "text": w["text"][:80]
                    })
    except ImportError:
        pass
    out["kind"] = "acroform" if out["widgets"] else "flat"
    return out, reader


def render_page(path, page_idx, out_png, doc):
    if BACKEND == "pymupdf":
        doc[page_idx].get_pixmap(dpi=120).save(out_png)
        return True
    try:
        import pypdfium2 as pdfium
        pdf = pdfium.PdfDocument(path)
        pdf[page_idx].render(scale=1.5).to_pil().save(out_png)
        return True
    except Exception:
        print("Render requires pymupdf or pypdfium2.", file=sys.stderr)
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--render")
    ap.add_argument("--page", type=int, default=0)
    a = ap.parse_args()
    info, doc = inspect(a.pdf)
    if a.render and render_page(a.pdf, a.page, a.render, doc):
        print(f"Rendered page {a.page} to {a.render}")
    if a.json:
        print(json.dumps(info, indent=2))
        return
    print(f"{info['file']}: {info['pages']} page(s), kind={info['kind']}, backend={info['backend']}")
    if info["widgets"]:
        for w in info["widgets"]:
            print(f"  [p{w['page']}] {w['name']!r:36} {w['type']:12} rect={w['rect']} value={w['value']!r}")
    else:
        print("  Flat PDF anchors (top-left origin):")
        for t in info["anchors"][:60]:
            print(f"  [p{t['page']}] x={t['x']:6} y={t['y']:6}  {t['text']}")


if __name__ == "__main__":
    main()
