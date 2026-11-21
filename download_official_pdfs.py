#!/usr/bin/env python3
"""Download real official Indian / West Bengal government PDF forms into assets/official_pdfs/
and inspect their page dimensions and text anchor coordinates for direct PyMuPDF overlay filling.
"""
import json
import ssl
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OFFICIAL_DIR = ROOT / "redtape-navigator-unified" / "assets" / "official_pdfs"
OFFICIAL_DIR.mkdir(parents=True, exist_ok=True)

OFFICIAL_PDFS = {
    "WB_Municipal_Form_J_Official.pdf": {
        "url": "https://sudawb.org/wbdma_oldversion_old/forms/trade_licence_application.pdf",
        "licence_id": "lic_municipal_form_j",
        "title": "WB Municipal Act 1993 — Official Form J",
    },
    "FSSAI_Form_A_Official.pdf": {
        "url": "https://foscos.fssai.gov.in/assets/docs/registrationForm_A.pdf",
        "licence_id": "lic_fssai_basic_registration",
        "title": "FSSAI Official Form A (Basic Registration)",
    },
    "FSSAI_Form_B_Official.pdf": {
        "url": "https://foscos.fssai.gov.in/assets/docs/stateForm_b.pdf",
        "licence_id": "lic_fssai_state",
        "title": "FSSAI Official Form B (State License)",
    },
    "WB_Professional_Tax_Form_II_Official.pdf": {
        "url": "https://raniganjchamber.com/usefulforms/professional%20tax%20enrolment.pdf",
        "licence_id": "lic_wb_ptax",
        "title": "WB Profession Tax Official Form II",
    },
    "GST_REG_01_Official.pdf": {
        "url": "https://taxindiaonline.com/RC2/pdfnoti/gst/gst_forms/2017/GST%20REG-01.pdf",
        "licence_id": "lic_gst_reg",
        "title": "GSTN Official Form GST REG-01",
    },
}


def download_all():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    results = {}
    for fname, meta in OFFICIAL_PDFS.items():
        dest = OFFICIAL_DIR / fname
        url = meta["url"]
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"},
            )
            with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
                data = resp.read()
            if data[:4] == b"%PDF":
                dest.write_bytes(data)
                import pymupdf
                doc = pymupdf.open(str(dest))
                p0 = doc[0]
                widgets = list(p0.widgets() or [])
                txt = p0.get_text("text")[:180].replace("\n", " ")
                results[fname] = {
                    "ok": True,
                    "bytes": len(data),
                    "pages": len(doc),
                    "width": round(p0.rect.width, 1),
                    "height": round(p0.rect.height, 1),
                    "widgets": len(widgets),
                    "has_text": len(txt.strip()) > 20,
                    "sample_text": txt[:120],
                }
                print(f"[OK] {fname}: {len(data):,} bytes, {len(doc)}p, {p0.rect.width:.0f}x{p0.rect.height:.0f}, widgets={len(widgets)}, text={len(txt.strip())>20}")
            else:
                results[fname] = {"ok": False, "error": f"Not a PDF (header={data[:20]!r})"}
                print(f"[SKIP] {fname}: response was not a PDF")
        except Exception as e:
            results[fname] = {"ok": False, "error": str(e)}
            print(f"[ERR] {fname}: {e}")

    (OFFICIAL_DIR / "manifest.json").write_text(json.dumps(results, indent=2), encoding="utf-8")


if __name__ == "__main__":
    download_all()
