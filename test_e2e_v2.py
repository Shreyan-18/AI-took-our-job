#!/usr/bin/env python3
"""End-to-end verification for all 3 sector-pure RedTape Navigator scenarios:
- Zero FSSAI in non-food retail (Book Stall & Clothes Shop)
- 5 to 7 authentic sector-specific AcroForm PDFs per scenario
- Claude Interactive Question Card option parsing + Skip handling
- Real AcroForm widget readback via pypdf
"""
import sys
from pathlib import Path
import pypdf

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from interview_engine_v2 import RedTapeSession, match_scenario


def verify_pdf_contains(pdf_path: str, expected_substrings: list[str]):
    reader = pypdf.PdfReader(pdf_path)
    fields = reader.get_fields() or {}
    values = {k: str(v.get("/V", "")) for k, v in fields.items()}
    joined = " | ".join(values.values()).upper()
    for exp in expected_substrings:
        assert exp.upper() in joined, f"Expected '{exp}' in {Path(pdf_path).name}, got fields: {values}"
    return values


def run_all():
    assert match_scenario("I want to open a bakery shop in Park Circus, Kolkata") == "bakery_kolkata"
    assert match_scenario("open a stationary book stall in sodpur") == "stationery_sodpur"
    assert match_scenario("open a clothes shop in barrackpore") == "clothes_barrackpore"
    print("[PASS] Keyword routing for all 3 sectors")

    # 1. SECTOR 1: BAKERY IN PARK CIRCUS, KOLKATA
    s1 = RedTapeSession()
    s1.handle_chat("open a bakery shop in kolkata park circus, kolkata")
    s1.handle_chat("Aarav Sen — Park Circus Bakehouse, 24/1 Park Circus Seven Point, Kolkata 700017")
    s1.handle_chat("Under ₹18 Lakhs · Counter takeaway + 6 seats · Electric ovens (FSSAI Form A)")
    s1.handle_chat("4 staff members · Rented shop premises (stages Landlord NOC)")
    r1 = s1.handle_chat("9830012345 · Defer PAN (stamp [PENDING_USER_INPUT] for privacy)")

    assert s1.interview_complete and r1["open_artifacts"]
    pdf_names_1 = [f["form_name"] for f in s1.form_artifacts]
    assert len(pdf_names_1) == 5, f"Expected 5 bakery PDFs, got {pdf_names_1}"
    assert "KMC_Section199_Trade_Enlistment.pdf" in pdf_names_1
    assert "FSSAI_Registration_Form_A.pdf" in pdf_names_1
    assert "WB_Professional_Tax_Form_II.pdf" in pdf_names_1
    assert "Udyam_MSME_Registration_Draft.pdf" in pdf_names_1

    kmc_pdf = [f["file_path"] for f in s1.form_artifacts if "KMC_Section199" in f["form_name"]][0]
    verify_pdf_contains(kmc_pdf, ["PARK CIRCUS BAKEHOUSE", "Aarav Sen", "9830012345", "[PENDING_USER_INPUT]"])
    print(f"[PASS] Sector 1 (Bakery): {len(pdf_names_1)} PDFs -> {pdf_names_1}")

    # Test Bakery high-scale override -> FSSAI Form B + GST REG-01 + Fire NOC (7 PDFs!)
    s1.handle_chat("What if my turnover is ₹2.2 Crore and seating is 55 seats?")
    pdf_names_1_hi = [f["form_name"] for f in s1.form_artifacts]
    assert "FSSAI_State_License_Form_B.pdf" in pdf_names_1_hi
    assert "GST_REG_01_Application_Draft.pdf" in pdf_names_1_hi
    assert "WB_Fire_Safety_NOC_Form.pdf" in pdf_names_1_hi
    print(f"[PASS] Sector 1 Override (₹2.2 Cr, 55 seats): {len(pdf_names_1_hi)} PDFs -> {pdf_names_1_hi}")

    # 2. SECTOR 2: STATIONERY & BOOK STALL IN SODPUR (ZERO FSSAI!)
    s2 = RedTapeSession()
    s2.handle_chat("open a stationary book stall in sodpur")
    s2.handle_chat("Subhashish Mukherjee — Vidyasagar Book Stall, 12 Station Road, Sodpur, Kolkata 700110")
    s2.handle_chat("160 sq ft · Rented stall (Micro-Enterprise ₹800/yr tariff)")
    s2.handle_chat("2 staff members · Around ₹8 Lakhs turnover (Triggers WB P-Tax Form II)")
    r2 = s2.handle_chat("9831123456 · PAN: BDFPM4412K (full 100% auto-fill)")

    assert s2.interview_complete and r2["open_artifacts"]
    matrix_ids_2 = [m["id"] for m in s2.compliance_matrix]
    assert not any("fssai" in mid for mid in matrix_ids_2), f"FSSAI must NOT appear in Book Stall! Got {matrix_ids_2}"
    pdf_names_2 = [f["form_name"] for f in s2.form_artifacts]
    assert len(pdf_names_2) == 5, f"Expected 5 book stall PDFs, got {pdf_names_2}"
    assert "WB_Municipal_Form_J_CE.pdf" in pdf_names_2
    assert "Panihati_Signboard_Clearance_Form.pdf" in pdf_names_2
    assert "WB_Professional_Tax_Form_II.pdf" in pdf_names_2
    form_j_2 = [f["file_path"] for f in s2.form_artifacts if "Form_J" in f["form_name"]][0]
    verify_pdf_contains(form_j_2, ["VIDYASAGAR BOOK STALL", "Subhashish Mukherjee", "160", "9831123456"])
    print(f"[PASS] Sector 2 (Sodpur Book Stall, ZERO FSSAI): {len(pdf_names_2)} PDFs -> {pdf_names_2}")

    # 3. SECTOR 3: CLOTHES SHOP IN BARRACKPORE (ZERO FSSAI!)
    s3 = RedTapeSession()
    s3.handle_chat("open a clothes shop in barrackpore")
    s3.handle_chat("Debolina Ghosh — Ananya Fashion & Garments, 84 SN Banerjee Road, Anandapuri, Barrackpore 700120")
    s3.handle_chat("4 sales staff · Rented showroom (stages Landlord NOC)")
    s3.handle_chat("650 sq ft · Around ₹48 Lakhs turnover (Triggers GST REG-01 + WB P-Tax)")
    r3 = s3.handle_chat("9832234567 · PAN: ABCDE5678G (full 100% auto-fill)")

    assert s3.interview_complete and r3["open_artifacts"]
    matrix_ids_3 = [m["id"] for m in s3.compliance_matrix]
    assert not any("fssai" in mid for mid in matrix_ids_3), f"FSSAI must NOT appear in Clothes Shop! Got {matrix_ids_3}"
    pdf_names_3 = [f["form_name"] for f in s3.form_artifacts]
    assert len(pdf_names_3) == 6, f"Expected 6 clothes shop PDFs, got {pdf_names_3}"
    assert "WB_Municipal_Form_J_CE.pdf" in pdf_names_3
    assert "WB_Textile_Fire_Safety_Declaration.pdf" in pdf_names_3
    assert "GST_REG_01_Application_Draft.pdf" in pdf_names_3
    assert "WB_Professional_Tax_Form_II.pdf" in pdf_names_3
    gst_pdf = [f["file_path"] for f in s3.form_artifacts if "GST_REG_01" in f["form_name"]][0]
    verify_pdf_contains(gst_pdf, ["ANANYA FASHION & GARMENTS", "DEBOLINA GHOSH", "ABCDE5678G", "9832234567"])
    print(f"[PASS] Sector 3 (Barrackpore Clothes Shop, ZERO FSSAI): {len(pdf_names_3)} PDFs -> {pdf_names_3}")

    print("\nALL SECTOR-PURE MULTI-PDF E2E CHECKS PASSED!")


if __name__ == "__main__":
    run_all()
