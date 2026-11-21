#!/usr/bin/env python3
"""Generate authentic, sector-specific West Bengal & Central AcroForm PDF templates and field maps.
Covers:
1. KMC_Section199_Trade_Enlistment.pdf (Kolkata Municipal Corporation Act 1980, Sec 199)
2. WB_Municipal_Form_J_CE.pdf (WB Municipal Act 1993, Sec 118 Form J — Panihati & Barrackpore)
3. FSSAI_Registration_Form_A.pdf (Basic Registration <= Rs 1.5 Cr, Bakery only)
4. FSSAI_State_License_Form_B.pdf (State License Rs 1.5 Cr - 50 Cr, Bakery only)
5. WB_Shops_Establishment_Form_B.pdf (WB Shops & Establishments Act 1963, Rule 4)
6. WB_Professional_Tax_Form_II.pdf (WB State Tax on Professions, Trades & Callings Rules 1979)
7. GST_REG_01_Application_Draft.pdf (CGST/WBGST Rule 8(1) Form GST REG-01)
8. Udyam_MSME_Registration_Draft.pdf (Ministry of MSME — Udyam Registration)
9. WB_Fire_Safety_NOC_Form.pdf (WB Fire Services Act 1950 — Form V NOC)
10. WB_Textile_Fire_Safety_Declaration.pdf (IS 2190 Textile Combustible Storage Declaration)
11. Panihati_Signboard_Clearance_Form.pdf (Panihati Municipality Commercial Fascia Display)
"""
import json
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

ROOT_DIR = Path(__file__).resolve().parent
FORMS_DIR = ROOT_DIR / "redtape-navigator-unified" / "assets" / "forms"
FORMS_DIR.mkdir(parents=True, exist_ok=True)


def _create_pdf_and_map(filename: str, map_name: str, licence_id: str, headers: list[str], fields: list[dict], footer: list[str]):
    """Helper to generate a crisp, official-style AcroForm PDF + matching field_map JSON."""
    pdf_path = FORMS_DIR / filename
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter

    y = 755
    for idx, line in enumerate(headers):
        c.setFont("Helvetica-Bold" if idx < 2 else "Helvetica", 13 if idx == 0 else (11 if idx == 1 else 9.5))
        c.drawCentredString(width / 2, y, line)
        y -= 17
    c.line(50, y + 6, width - 50, y + 6)
    y -= 20

    form = c.acroForm
    map_fields = []

    for f in fields:
        c.setFont("Helvetica", 9.5)
        c.drawString(58, y, f["label"])
        y -= 24
        if f.get("type") == "checkbox":
            form.checkbox(name=f["name"], x=58, y=y + 2, size=15, buttonStyle="check")
            c.drawString(82, y + 5, f.get("checkbox_label", "Yes"))
        else:
            form.textfield(name=f["name"], x=58, y=y, width=495, height=20, borderStyle="underlined", fontSize=10)
        y -= 22

        entry = {
            "target": {"acroform": f["name"]},
            "source": f["source"],
            "mandatory": f.get("mandatory", True),
        }
        if f.get("transform"):
            entry["transform"] = f["transform"]
        if f.get("type") == "checkbox":
            entry["type"] = "checkbox"
            entry["checked_if"] = f.get("checked_if", "owned")
        map_fields.append(entry)

    # Signature & Verification block
    sig_y = max(110, y - 16)
    c.setFont("Helvetica-Bold", 9.5)
    c.drawString(58, sig_y, "Declaration: I hereby declare that the particulars furnished above are true to the best of my knowledge.")
    c.setFont("Helvetica", 9)
    c.drawString(58, sig_y - 24, "Signature of Applicant / Proprietor: ___________________________        Date: _______________")

    fy = 66
    c.setFont("Helvetica-Oblique", 8)
    for fl in footer:
        c.drawString(58, fy, fl)
        fy -= 12

    c.save()

    fmap = {
        "form": filename,
        "licence_id": licence_id,
        "coord_origin": "top-left",
        "fields": map_fields,
    }
    (FORMS_DIR / map_name).write_text(json.dumps(fmap, indent=2), encoding="utf-8")
    print(f"Built {filename} + {map_name} ({len(fields)} AcroForm fields)")


def build_official_wb_form_j():
    """Faithful 1:1 replica of the official West Bengal Municipal Act, 1993 — FORM J
    (Application for certificate of enlistment, See section 118) matching trade_licence_application.pdf.
    """
    filename = "WB_Municipal_Form_J_CE.pdf"
    map_name = "wb_municipal_form_j_map.json"
    pdf_path = FORMS_DIR / filename
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    form = c.acroForm

    # Top-left Serial No. / Rs. 30/- rounded box
    c.setLineWidth(0.8)
    c.roundRect(36, 705, 195, 62, 10, stroke=1, fill=0)
    c.setFont("Helvetica", 9)
    c.drawString(48, 748, "Serial No.")
    c.setFont("Helvetica-Bold", 9.5)
    c.drawString(178, 748, "Rs. 30/-")

    # Top-right Official Header
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(410, 756, "FORM  J")
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(410, 741, "Application for certificate of enlistment")
    c.setFont("Helvetica", 9.5)
    c.drawCentredString(410, 726, "The West Bengal Municipal Act, 1993 [See section 118]")
    c.setFont("Helvetica-BoldOblique", 8.5)
    c.drawCentredString(410, 713, "(To be filled up in block letters)")

    # Ward No. & Year right-aligned fields
    c.setFont("Helvetica", 9)
    c.drawString(430, 696, "Ward No.")
    form.textfield(name="ward_no", x=474, y=691, width=98, height=15, borderStyle="underlined", fontSize=8.5)
    c.drawString(448, 678, "Year")
    form.textfield(name="enlistment_year", x=474, y=673, width=98, height=15, borderStyle="underlined", fontSize=8.5)

    # Salutation
    c.setFont("Helvetica", 9.5)
    c.drawString(36, 682, "To")
    c.setFont("Helvetica-Bold", 9.5)
    c.drawString(56, 682, "The Chairman / Executive Officer,")
    form.textfield(name="municipality_name", x=222, y=677, width=200, height=15, borderStyle="underlined", fontSize=9)

    c.setFont("Helvetica", 9)
    c.drawString(36, 663, "Sir,")
    c.drawString(56, 649, "I/We hereby apply for a new/renewal of Certificate of Enlistment for carrying on Trade,")
    c.drawString(36, 637, "Profession and Callings as stated below -")

    lx, cx, fx, fw = 42, 232, 244, 328

    def draw_row(num, label_lines, fname, y_pos, field_h=16):
        c.setFont("Helvetica", 8.8)
        c.drawString(lx, y_pos, f"{num}.")
        for i, ltxt in enumerate(label_lines):
            c.drawString(lx + 18, y_pos - i * 11, ltxt)
        c.drawString(cx, y_pos, ":")
        form.textfield(name=fname, x=fx, y=y_pos - 4, width=fw, height=field_h, borderStyle="underlined", fontSize=8.8)

    draw_row("1", ["Name(s) of applicant"], "applicant_name", 614)
    draw_row("2", ["Name of Firm or Company"], "enterprise_name", 590)
    draw_row("3", ["Date/Expected date of", "commencement of business"], "commencement_date", 566)
    draw_row("4", ["Residential address of the", "applicant(s)"], "residential_address", 538)

    y5 = 506
    c.setFont("Helvetica", 8.8)
    c.drawString(lx, y5, "5.")
    for i, ltxt in enumerate([
        "Address of the place of business",
        "where trade / profession / calling",
        "is carried on including its Rent /",
        "Annual Valuation",
    ]):
        c.drawString(lx + 18, y5 - i * 10.5, ltxt)
    c.drawString(cx, y5, ":")
    c.drawString(fx, y5, "Holding No")
    form.textfield(name="holding_no", x=fx + 52, y=y5 - 4, width=85, height=15, borderStyle="underlined", fontSize=8.5)
    c.drawString(fx + 144, y5, "Possession")
    form.textfield(name="premises_type", x=fx + 196, y=y5 - 4, width=132, height=15, borderStyle="underlined", fontSize=8.5)

    c.drawString(fx, y5 - 20, "Road / Street / Lane")
    form.textfield(name="premises_address", x=fx + 92, y=y5 - 24, width=236, height=15, borderStyle="underlined", fontSize=8.5)

    c.drawString(fx, y5 - 39, "Ward / Area")
    form.textfield(name="business_ward", x=fx + 58, y=y5 - 43, width=270, height=15, borderStyle="underlined", fontSize=8.5)

    draw_row("6", ["Nature of Trade / Profession /", "Calling"], "trade_nature", 442)
    draw_row("7", ["(a) Address of workshop, if any"], "workshop_address", 412)
    c.setFont("Helvetica", 8.8)
    c.drawString(lx + 18, 392, "(b) Address of Godown, if any")
    c.drawString(cx, 392, ":")
    form.textfield(name="godown_address", x=fx, y=388, width=fw, height=15, borderStyle="underlined", fontSize=8.5)

    draw_row("8", ["Particulars of immediate", "preceding year's certificate of", "enlistment under section 118 in", "case of renewal"], "previous_ce", 364)

    y9 = 312
    c.setFont("Helvetica", 8.8)
    c.drawString(lx, y9, "9.")
    c.drawString(lx + 18, y9, "Additional information, if any")
    c.drawString(cx, y9, ":")
    form.textfield(name="additional_info", x=fx, y=y9 - 4, width=175, height=15, borderStyle="underlined", fontSize=8.5)
    c.drawString(fx + 182, y9, "Ph.No.")
    form.textfield(name="mobile_number", x=fx + 216, y=y9 - 4, width=112, height=15, borderStyle="underlined", fontSize=8.5)

    yd = 286
    c.setFont("Helvetica-Bold", 8.8)
    c.drawString(52, yd, "I/We solemnly declare that:-")
    c.setFont("Helvetica", 8.5)
    c.drawString(42, yd - 14, "(1) There is no litigation/Court case in my/our above mentioned premises where I/We are conducting business;")
    c.drawString(42, yd - 26, "(2) All information and statements as made above are true to my/our knowledge and belief;")
    c.drawString(42, yd - 38, "(3) Taxes/Fees under all other sections of the West Bengal Municipal Act, 1993 have been cleared by me/us.")
    c.drawString(42, yd - 53, "I/We pray for issue/renewal of Certificate of Enlistment for the year 2026-27 on payment of requisite application fee.")

    c.setFont("Helvetica", 9)
    c.drawString(405, yd - 72, "Yours faithfully,")
    c.drawString(42, yd - 96, "Date..............................")
    c.setFont("Helvetica-Bold", 8.8)
    c.drawString(330, yd - 98, "Signature of the applicant(s) with office seal")

    ty = 172
    c.setFont("Helvetica-Bold", 8.2)
    c.drawString(36, ty + 4, "N.B. Documentary evidence in respect of the following is to be submitted:-")
    c.setLineWidth(0.6)
    c.rect(36, 46, 540, 122, stroke=1, fill=0)
    c.line(306, 46, 306, 168)

    c.setFont("Helvetica-Bold", 8)
    c.drawString(42, 156, "A.  In case of New Enlistment firm,-")
    c.drawString(312, 156, "B.  In case of Renewal Enlistment firm,-")

    c.setFont("Helvetica", 7.8)
    left_docs = [
        "(a) Incorporation Certificate / Proprietorship Proof;",
        "(b) Rent Bill / Lease Agreement;",
        "(c) Up-to-date Municipal tax receipt;",
        "(d) N.O.C / Consent letter of the owner;",
        "(e) Memorandum & Article of Association (if applicable);",
        "(f) Letter Head;",
        "(g) Any Other Documents If Required.",
    ]
    right_docs = [
        "(a) Previous Enlistment Certificate;",
        "(b) Current Professional Tax receipt;",
        "(c) Letter Head;",
        "(d) Rent Bill / Up-to-date tax receipt;",
        "(e) Consent letter of the owner;",
        "(f) Fire license clearance certificate;",
        "(g) Pollution Board Certificate;",
        "(h) Any Other Documents If Required.",
    ]
    for i, item in enumerate(left_docs):
        c.drawString(52, 143 - i * 12.5, item)
    for i, item in enumerate(right_docs):
        c.drawString(322, 143 - i * 12.5, item)

    c.save()

    fmap = {
        "form": filename,
        "licence_id": "lic_municipal_form_j",
        "coord_origin": "top-left",
        "fields": [
            {"target": {"acroform": "municipality_name"}, "source": "applicant_profile.location.municipal_ward_or_block", "mandatory": True},
            {"target": {"acroform": "ward_no"}, "source": "applicant_profile.location.city_or_village", "mandatory": False},
            {"target": {"acroform": "enlistment_year"}, "source": "applicant_profile.domain_attributes.enlistment_year", "mandatory": False},
            {"target": {"acroform": "applicant_name"}, "source": "applicant_profile.applicant.name", "transform": "upper", "mandatory": True},
            {"target": {"acroform": "enterprise_name"}, "source": "applicant_profile.entity_name", "transform": "upper", "mandatory": True},
            {"target": {"acroform": "commencement_date"}, "source": "applicant_profile.domain_attributes.commencement_date", "mandatory": False},
            {"target": {"acroform": "residential_address"}, "source": "applicant_profile.applicant.residential_address", "mandatory": False},
            {"target": {"acroform": "holding_no"}, "source": "applicant_profile.location.holding_no", "mandatory": False},
            {"target": {"acroform": "premises_type"}, "source": "applicant_profile.location.premises_type", "transform": "upper", "mandatory": True},
            {"target": {"acroform": "premises_address"}, "source": "applicant_profile.location.address", "transform": "upper", "mandatory": True},
            {"target": {"acroform": "business_ward"}, "source": "applicant_profile.location.municipal_ward_or_block", "transform": "upper", "mandatory": True},
            {"target": {"acroform": "trade_nature"}, "source": "applicant_profile.activity_type", "transform": "upper", "mandatory": True},
            {"target": {"acroform": "workshop_address"}, "source": "applicant_profile.domain_attributes.workshop_address", "mandatory": False},
            {"target": {"acroform": "godown_address"}, "source": "applicant_profile.domain_attributes.godown_address", "mandatory": False},
            {"target": {"acroform": "previous_ce"}, "source": "applicant_profile.domain_attributes.application_type", "mandatory": False},
            {"target": {"acroform": "additional_info"}, "source": "applicant_profile.domain_attributes.additional_info", "mandatory": False},
            {"target": {"acroform": "mobile_number"}, "source": "applicant_profile.applicant.phone", "transform": "phone_10digit", "mandatory": True},
        ],
    }
    (FORMS_DIR / map_name).write_text(json.dumps(fmap, indent=2), encoding="utf-8")
    print(f"Built official 1:1 {filename} + {map_name} ({len(fmap['fields'])} AcroForm fields)")


def build_all():
    # 1. KMC Section 199 Certificate of Enlistment (Park Circus Bakery)
    _create_pdf_and_map(
        "KMC_Section199_Trade_Enlistment.pdf",
        "kmc_section199_map.json",
        "lic_kmc_ce",
        [
            "KOLKATA MUNICIPAL CORPORATION",
            "LICENCE DEPARTMENT — CERTIFICATE OF ENLISTMENT",
            "Application under Section 199 of the Kolkata Municipal Corporation Act, 1980 (Schedule IV)",
        ],
        [
            {"name": "business_name", "label": "1. Name of Firm / Commercial Establishment:", "source": "applicant_profile.entity_name", "transform": "upper"},
            {"name": "proprietor_name", "label": "2. Name of Applicant / Proprietor:", "source": "applicant_profile.applicant.name", "transform": "title"},
            {"name": "nature_of_trade", "label": "3. Nature of Trade / Profession / Calling:", "source": "applicant_profile.activity_type"},
            {"name": "premises_address", "label": "4. Full Premises Address (Street, Landmark, PIN):", "source": "applicant_profile.location.address"},
            {"name": "ward_borough", "label": "5. KMC Ward & Jurisdiction:", "source": "applicant_profile.location.municipal_ward_or_block"},
            {"name": "premises_type", "label": "6. Occupancy Status (Rented / Owned):", "source": "applicant_profile.location.premises_type", "transform": "title"},
            {"name": "workers_count", "label": "7. Number of Persons Engaged on Premises:", "source": "applicant_profile.domain_attributes.workers_on_site"},
            {"name": "contact_mobile", "label": "8. Mobile Number of Applicant:", "source": "applicant_profile.applicant.phone", "transform": "phone_10digit"},
            {"name": "applicant_pan", "label": "9. Permanent Account Number (PAN):", "source": "applicant_profile.applicant.pan", "transform": "pan"},
        ],
        [
            "Statutory Note: KMC Certificate of Enlistment is filed directly at https://www.kmcgov.in/KMCPortal/jsp/KMCCEHome.jsp.",
            "2026-27 Enlistment Fee capped at Rs. 2,500/year. Missing mandatory fields stamped with [PENDING_USER_INPUT].",
        ],
    )

    # 2. Official 1:1 West Bengal Municipal Act 1993 — FORM J
    build_official_wb_form_j()

    # 3. FSSAI State License Form B (Bakery > Rs 1.5 Crore)
    _create_pdf_and_map(
        "FSSAI_State_License_Form_B.pdf",
        "fssai_form_b_map.json",
        "lic_fssai_state",
        [
            "FOOD SAFETY AND STANDARDS AUTHORITY OF INDIA (FSSAI)",
            "FORM B — APPLICATION FOR STATE FOOD LICENSE",
            "Under FSS (Licensing and Registration of Food Businesses) Regulations (Turnover Rs. 1.5 Cr - 50 Cr)",
        ],
        [
            {"name": "applicant_name", "label": "1. Name of Proprietor / Food Business Operator:", "source": "applicant_profile.applicant.name", "transform": "upper"},
            {"name": "business_name", "label": "2. Name of Bakery / Food Enterprise:", "source": "applicant_profile.entity_name", "transform": "upper"},
            {"name": "premises_address", "label": "3. Address of Food Manufacturing / Retail Premises:", "source": "applicant_profile.location.address"},
            {"name": "kind_of_business", "label": "4. Kind of Business (KoB):", "source": "applicant_profile.activity_type"},
            {"name": "annual_turnover", "label": "5. Anticipated Annual Turnover:", "source": "applicant_profile.domain_attributes.expected_annual_turnover_inr", "transform": "inr_words"},
            {"name": "mobile_number", "label": "6. Contact Mobile Number:", "source": "applicant_profile.applicant.phone", "transform": "phone_10digit"},
            {"name": "applicant_pan", "label": "7. Permanent Account Number (PAN):", "source": "applicant_profile.applicant.pan", "transform": "pan"},
        ],
        [
            "Revised FSSAI Eligibility (effective 01.04.2026): State License Form B (Rs. 5,000/yr) applies for turnover Rs. 1.5 Cr to Rs. 50 Cr.",
            "Online submission portal: https://foscos.fssai.gov.in/apply-for-lic-and-reg",
        ],
    )

    # 4. West Bengal Professional Tax Enrolment Form II
    _create_pdf_and_map(
        "WB_Professional_Tax_Form_II.pdf",
        "wb_ptax_form_ii_map.json",
        "lic_wb_ptax",
        [
            "GOVERNMENT OF WEST BENGAL — DIRECTORATE OF COMMERCIAL TAXES",
            "FORM II — APPLICATION FOR CERTIFICATE OF ENROLMENT (PROFESSION TAX)",
            "Under Rule 4(1) / 6(2) of the WB State Tax on Professions, Trades, Callings & Employments Rules, 1979",
        ],
        [
            {"name": "applicant_name", "label": "1. Name of Applicant / Proprietor:", "source": "applicant_profile.applicant.name", "transform": "upper"},
            {"name": "trade_name", "label": "2. Trade Name / Style of Business:", "source": "applicant_profile.entity_name", "transform": "upper"},
            {"name": "nature_of_trade", "label": "3. Nature of Profession / Trade / Calling:", "source": "applicant_profile.activity_type"},
            {"name": "place_of_work", "label": "4. Principal Place of Business Address:", "source": "applicant_profile.location.address"},
            {"name": "jurisdiction", "label": "5. Municipal Jurisdiction / District:", "source": "applicant_profile.location.municipal_ward_or_block"},
            {"name": "annual_turnover", "label": "6. Estimated Annual Gross Turnover:", "source": "applicant_profile.domain_attributes.expected_annual_turnover_inr", "transform": "inr_words"},
            {"name": "applicant_pan", "label": "7. Permanent Account Number (PAN):", "source": "applicant_profile.applicant.pan", "transform": "pan"},
            {"name": "mobile_number", "label": "8. Mobile Number for e-Payment Alerts:", "source": "applicant_profile.applicant.phone", "transform": "phone_10digit"},
        ],
        [
            "Mandatory for West Bengal business traders exceeding Rs. 5 Lakh annual turnover. Annual payment due by 31st July.",
            "Official Portal: https://egov.wbcomtax.gov.in/PT_Admin",
        ],
    )

    # 5. GST Form REG-01 Application Draft
    _create_pdf_and_map(
        "GST_REG_01_Application_Draft.pdf",
        "gst_reg_01_map.json",
        "lic_gst_reg",
        [
            "GOODS AND SERVICES TAX NETWORK (GSTN) — INDIA",
            "FORM GST REG-01 — APPLICATION FOR REGISTRATION",
            "Under Rule 8(1) of CGST / WBGST Rules (Mandatory for Goods Turnover > Rs. 40 Lakhs)",
        ],
        [
            {"name": "legal_name", "label": "1. Legal Name of Business (As per PAN):", "source": "applicant_profile.applicant.name", "transform": "upper"},
            {"name": "trade_name", "label": "2. Trade Name of Shop / Enterprise:", "source": "applicant_profile.entity_name", "transform": "upper"},
            {"name": "pan_number", "label": "3. Permanent Account Number (PAN):", "source": "applicant_profile.applicant.pan", "transform": "pan"},
            {"name": "state_name", "label": "4. State / UT Jurisdiction:", "source": "applicant_profile.location.state"},
            {"name": "principal_address", "label": "5. Principal Place of Business Address:", "source": "applicant_profile.location.address"},
            {"name": "nature_of_possession", "label": "6. Nature of Possession of Premises (Rented / Owned):", "source": "applicant_profile.location.premises_type", "transform": "title"},
            {"name": "business_activity", "label": "7. Nature of Business Activity / Goods Supplied:", "source": "applicant_profile.activity_type"},
            {"name": "annual_turnover", "label": "8. Expected Aggregate Annual Turnover:", "source": "applicant_profile.domain_attributes.expected_annual_turnover_inr", "transform": "inr_words"},
            {"name": "mobile_number", "label": "9. Authorized Signatory Mobile Number:", "source": "applicant_profile.applicant.phone", "transform": "phone_10digit"},
        ],
        [
            "File online at https://www.gst.gov.in/ (Part A TRN via OTP + Part B verification). No government registration fee.",
            "Garment retail note: GST slab depends on retail sale price per piece; threshold is Rs. 40 Lakh for intra-state goods.",
        ],
    )

    # 6. Udyam MSME Registration Draft
    _create_pdf_and_map(
        "Udyam_MSME_Registration_Draft.pdf",
        "udyam_msme_map.json",
        "lic_udyam_msme",
        [
            "MINISTRY OF MICRO, SMALL AND MEDIUM ENTERPRISES, GOVT. OF INDIA",
            "UDYAM REGISTRATION — MICRO ENTERPRISE DATA SHEET",
            "Free Online Registration under MSMED Act, 2006 (Retail & Micro-Manufacturing Units)",
        ],
        [
            {"name": "entrepreneur_name", "label": "1. Name of Entrepreneur / Proprietor:", "source": "applicant_profile.applicant.name", "transform": "upper"},
            {"name": "enterprise_name", "label": "2. Name of Enterprise:", "source": "applicant_profile.entity_name", "transform": "upper"},
            {"name": "nic_activity", "label": "3. Major Activity / NIC Description:", "source": "applicant_profile.activity_type"},
            {"name": "nic_code", "label": "4. 5-Digit NIC Code:", "source": "applicant_profile.domain_attributes.nic_code"},
            {"name": "unit_address", "label": "5. Official Address of Enterprise / Shop:", "source": "applicant_profile.location.address"},
            {"name": "workers_count", "label": "6. Number of Persons Employed:", "source": "applicant_profile.domain_attributes.workers_on_site"},
            {"name": "annual_turnover", "label": "7. Estimated Annual Turnover:", "source": "applicant_profile.domain_attributes.expected_annual_turnover_inr", "transform": "inr_words"},
            {"name": "pan_number", "label": "8. Proprietor PAN:", "source": "applicant_profile.applicant.pan", "transform": "pan"},
            {"name": "mobile_number", "label": "9. Mobile Number (Linked to Aadhaar):", "source": "applicant_profile.applicant.phone", "transform": "phone_10digit"},
        ],
        [
            "Official Portal: https://udyamregistration.gov.in/ (100% Free, instant digital certificate via Aadhaar OTP).",
        ],
    )

    # 7. WB Fire Safety Recommendation / NOC Form
    _create_pdf_and_map(
        "WB_Fire_Safety_NOC_Form.pdf",
        "wb_fire_noc_map.json",
        "lic_wb_fire",
        [
            "GOVERNMENT OF WEST BENGAL",
            "WEST BENGAL FIRE & EMERGENCY SERVICES (WBFES)",
            "Application for Fire Safety Recommendation (FSR) / NOC under WB Fire Services Act, 1950",
        ],
        [
            {"name": "applicant_name", "label": "1. Name of Applicant / Occupier:", "source": "applicant_profile.applicant.name", "transform": "title"},
            {"name": "establishment_name", "label": "2. Name of Commercial Establishment:", "source": "applicant_profile.entity_name", "transform": "upper"},
            {"name": "premises_address", "label": "3. Full Address of Premises:", "source": "applicant_profile.location.address"},
            {"name": "occupancy_type", "label": "4. Nature of Occupancy / Commercial Activity:", "source": "applicant_profile.activity_type"},
            {"name": "seating_or_area", "label": "5. Customer Seating Capacity (if applicable):", "source": "applicant_profile.domain_attributes.customer_seating", "mandatory": False},
            {"name": "floor_area", "label": "6. Floor Area (Sq. Ft.):", "source": "applicant_profile.domain_attributes.floor_area_sqft", "mandatory": False},
            {"name": "mobile_number", "label": "7. Contact Mobile Number:", "source": "applicant_profile.applicant.phone", "transform": "phone_10digit"},
        ],
        [
            "Submitted online via SilpaSathi / West Bengal Fire & Emergency Services portal. Attach architectural floor layout plan.",
        ],
    )

    # 8. Textile Combustible Storage & Fire Safety Self-Declaration (Barrackpore Clothes Shop)
    _create_pdf_and_map(
        "WB_Textile_Fire_Safety_Declaration.pdf",
        "wb_textile_fire_map.json",
        "lic_wb_fire_advisory",
        [
            "TEXTILE & GARMENT RETAIL — FIRE SAFETY SELF-COMPLIANCE DECLARATION",
            "Under West Bengal Fire Services Act, 1950 & IS 2190 Extinguisher Guidelines",
            "For Commercial Readymade Garment & Apparel Showrooms",
        ],
        [
            {"name": "proprietor_name", "label": "1. Name of Showroom Proprietor:", "source": "applicant_profile.applicant.name", "transform": "title"},
            {"name": "showroom_name", "label": "2. Name of Apparel / Garments Shop:", "source": "applicant_profile.entity_name", "transform": "upper"},
            {"name": "premises_address", "label": "3. Showroom Address:", "source": "applicant_profile.location.address"},
            {"name": "floor_area", "label": "4. Total Carpet Area (Sq. Ft.):", "source": "applicant_profile.domain_attributes.floor_area_sqft"},
            {"name": "workers_count", "label": "5. Staff Trained in Extinguisher Operation:", "source": "applicant_profile.domain_attributes.workers_on_site"},
            {"name": "mobile_number", "label": "6. Emergency Contact Mobile:", "source": "applicant_profile.applicant.phone", "transform": "phone_10digit"},
        ],
        [
            "Mandatory self-compliance: Maintain at least 2x 4kg ABC dry-powder fire extinguishers (IS 2190) and unobstructed exit.",
        ],
    )

    # 9. Panihati Municipal Signboard & Fascia Display Application (Sodpur Book Stall)
    _create_pdf_and_map(
        "Panihati_Signboard_Clearance_Form.pdf",
        "panihati_signboard_map.json",
        "lic_wb_signage",
        [
            "PANIHATI MUNICIPALITY — REVENUE & ADVERTISEMENT DEPARTMENT",
            "APPLICATION FOR COMMERCIAL SIGNBOARD & FASCIA DISPLAY CLEARANCE",
            "Under West Bengal Municipal Act, 1993 — Commercial Display & Signage Rules",
        ],
        [
            {"name": "applicant_name", "label": "1. Name of Stall Proprietor:", "source": "applicant_profile.applicant.name", "transform": "title"},
            {"name": "shop_name", "label": "2. Name to be Displayed on Signboard:", "source": "applicant_profile.entity_name", "transform": "upper"},
            {"name": "premises_address", "label": "3. Stall Location & Ward (Sodpur / Panihati):", "source": "applicant_profile.location.address"},
            {"name": "floor_area", "label": "4. Shop Carpet Area (Sq. Ft.):", "source": "applicant_profile.domain_attributes.floor_area_sqft"},
            {"name": "mobile_number", "label": "5. Proprietor Mobile Number:", "source": "applicant_profile.applicant.phone", "transform": "phone_10digit"},
        ],
        [
            "Submitted alongside Panihati Municipality Certificate of Enlistment (https://panihatimunicipality.org/). Annual fee Rs. 250.",
        ],
    )


if __name__ == "__main__":
    build_all()
