#!/usr/bin/env python3
"""Fill an official PDF (AcroForm or flat overlay) from state.json using a field map.
Supports dual backend: PyMuPDF (fitz) preferred, with pypdf (+ reportlab overlay) fallback.
Never invents values; --stamp-pending marks missing mandatory fields on BOTH AcroForm and flat PDFs.
Usage: python3 fill_pdf.py form.pdf field_map.json state.json --out draft.pdf [--report r.json] [--stamp-pending]
"""
import argparse
import io
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _common import PENDING, apply_transform, effective_value, is_blank, load_json, need, save_json

try:
    import pymupdf as fitz
    BACKEND = "pymupdf"
except ImportError:
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


def _fill_pymupdf(pdf_path, field_map, state, out_path, stamp_pending):
    doc = fitz.open(pdf_path)
    widgets = {}
    for page in doc:
        for w in page.widgets() or []:
            widgets[w.field_name] = (page, w)
    report = {"form": os.path.basename(pdf_path), "backend": "pymupdf", "filled": [], "pending": [], "unmapped": []}
    mapped_acro = set()
    for f in field_map["fields"]:
        tgt, src = f["target"], f["source"]
        label = tgt.get("acroform") or f"p{tgt.get('page')}@({tgt.get('x')},{tgt.get('y')})"
        raw = effective_value(state, src)
        if "acroform" in tgt:
            mapped_acro.add(tgt["acroform"])
        if f.get("type") == "checkbox":
            val = (raw == f.get("checked_if")) if not is_blank(raw) else None
        else:
            val = None if is_blank(raw) else apply_transform(raw, f.get("transform"))
        if val is None:
            report["pending"].append({"field": label, "source": src, "mandatory": bool(f.get("mandatory"))})
            if stamp_pending and f.get("mandatory"):
                if "acroform" in tgt and tgt["acroform"] in widgets and f.get("type") != "checkbox":
                    _, w = widgets[tgt["acroform"]]
                    w.field_value = PENDING
                    w.update()
                elif "page" in tgt:
                    doc[tgt["page"]].insert_text((tgt["x"], tgt["y"]), PENDING, fontsize=tgt.get("fontsize", 9), color=(0.8, 0, 0))
            continue
        if "acroform" in tgt:
            if tgt["acroform"] not in widgets:
                report["pending"].append({"field": label, "source": src, "mandatory": bool(f.get("mandatory")), "reason": "widget not found"})
                continue
            _, w = widgets[tgt["acroform"]]
            w.field_value = (w.on_state() if val else "Off") if f.get("type") == "checkbox" else str(val)
            w.update()
        else:
            page = doc[tgt["page"]]
            if f.get("type") == "checkbox":
                if val:
                    page.insert_text((tgt["x"], tgt["y"]), "X", fontsize=tgt.get("fontsize", 11))
            else:
                page.insert_text((tgt["x"], tgt["y"]), str(val), fontsize=tgt.get("fontsize", 10), fontname="helv")
        report["filled"].append({"field": label, "source": src})
    report["unmapped"] = [n for n in widgets if n not in mapped_acro]
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    doc.save(out_path)
    return report


def _fill_pypdf(pdf_path, field_map, state, out_path, stamp_pending):
    reader = pypdf.PdfReader(pdf_path)
    writer = pypdf.PdfWriter()
    writer.append(reader)
    existing_fields = reader.get_fields() or {}
    report = {"form": os.path.basename(pdf_path), "backend": "pypdf", "filled": [], "pending": [], "unmapped": []}
    mapped_acro = set()
    acro_updates = {}
    flat_overlays = {}

    for f in field_map["fields"]:
        tgt, src = f["target"], f["source"]
        label = tgt.get("acroform") or f"p{tgt.get('page')}@({tgt.get('x')},{tgt.get('y')})"
        raw = effective_value(state, src)
        if "acroform" in tgt:
            mapped_acro.add(tgt["acroform"])
        if f.get("type") == "checkbox":
            val = (raw == f.get("checked_if")) if not is_blank(raw) else None
        else:
            val = None if is_blank(raw) else apply_transform(raw, f.get("transform"))

        if val is None:
            report["pending"].append({"field": label, "source": src, "mandatory": bool(f.get("mandatory"))})
            if stamp_pending and f.get("mandatory"):
                if "acroform" in tgt and tgt["acroform"] in existing_fields and f.get("type") != "checkbox":
                    acro_updates[tgt["acroform"]] = PENDING
                elif "page" in tgt:
                    flat_overlays.setdefault(tgt["page"], []).append((tgt["x"], tgt["y"], PENDING, tgt.get("fontsize", 9), True))
            continue

        if "acroform" in tgt:
            if tgt["acroform"] not in existing_fields:
                report["pending"].append({"field": label, "source": src, "mandatory": bool(f.get("mandatory")), "reason": "widget not found"})
                continue
            acro_updates[tgt["acroform"]] = ("/Yes" if val else "/Off") if f.get("type") == "checkbox" else str(val)
        else:
            text_val = ("X" if val else "") if f.get("type") == "checkbox" else str(val)
            if text_val:
                flat_overlays.setdefault(tgt["page"], []).append((tgt["x"], tgt["y"], text_val, tgt.get("fontsize", 10), False))
        report["filled"].append({"field": label, "source": src})

    if acro_updates:
        for page in writer.pages:
            writer.update_page_form_field_values(page, acro_updates)

    if flat_overlays:
        try:
            from reportlab.pdfgen import canvas as rl_canvas
            for pno, items in flat_overlays.items():
                page = writer.pages[pno]
                pw, ph = float(page.mediabox.width), float(page.mediabox.height)
                buf = io.BytesIO()
                c = rl_canvas.Canvas(buf, pagesize=(pw, ph))
                for x, y_top, txt, fsize, is_pending in items:
                    c.setFont("Helvetica", fsize)
                    if is_pending:
                        c.setFillColorRGB(0.8, 0, 0)
                    else:
                        c.setFillColorRGB(0, 0, 0)
                    # Convert top-left origin to ReportLab bottom-left origin
                    c.drawString(x, ph - y_top, txt)
                c.save()
                buf.seek(0)
                ov_page = pypdf.PdfReader(buf).pages[0]
                page.merge_page(ov_page)
        except ImportError:
            report["warning"] = "Flat overlays skipped: reportlab not installed."

    report["unmapped"] = [n for n in existing_fields if n not in mapped_acro]
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "wb") as f:
        writer.write(f)
    return report


def fill(pdf_path, field_map, state, out_path, stamp_pending=False):
    rep = _fill_pymupdf(pdf_path, field_map, state, out_path, stamp_pending) if BACKEND == "pymupdf" else _fill_pypdf(pdf_path, field_map, state, out_path, stamp_pending)
    total = len(rep["filled"]) + len(rep["pending"])
    rep["completion_percentage"] = round(100 * len(rep["filled"]) / total) if total else 0
    rep["missing_fields"] = [p["source"] for p in rep["pending"] if p.get("mandatory")]
    rep["file_path"] = out_path
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf"); ap.add_argument("field_map"); ap.add_argument("state")
    ap.add_argument("--out", required=True)
    ap.add_argument("--report")
    ap.add_argument("--stamp-pending", action="store_true")
    a = ap.parse_args()
    rep = fill(a.pdf, load_json(a.field_map), load_json(a.state), a.out, a.stamp_pending)
    if a.report:
        save_json(a.report, rep)
    print(f"{rep['form']} [{rep['backend']}]: {rep['completion_percentage']}% mapped, {len(rep['filled'])} filled, "
          f"{len(rep['pending'])} pending, {len(rep['unmapped'])} unmapped -> {a.out}")


if __name__ == "__main__":
    main()
