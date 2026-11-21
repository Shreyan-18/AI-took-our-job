#!/usr/bin/env python3
"""Pixel-calibrated coordinate-overlay field maps for all 6 REAL downloaded official government PDFs
in redtape-navigator-unified/assets/official_pdfs/.
Coordinates verified visually against 150-DPI coordinate grids & PyMuPDF text bounding boxes.
Zero fabricated placeholder fields (never stamps 'N/A', 'AS PER RENT/TAX BILL', or city name as Ward No.).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OFFICIAL_DIR = ROOT / "redtape-navigator-unified" / "assets" / "official_pdfs"
OFFICIAL_DIR.mkdir(parents=True, exist_ok=True)


def write_maps():
    # 1. REAL OFFICIAL WB MUNICIPAL ACT, 1993 — FORM J (595 x 842 A4 scan)
    # Verified on WB_Municipal_Form_J_Official_p0_grid.png
    form_j_map = {
        "form": "WB_Municipal_Form_J_Official.pdf",
        "licence_id": "lic_municipal_form_j",
        "official_url": "https://sudawb.org/wbdma_oldversion_old/forms/trade_licence_application.pdf",
        "coord_origin": "top-left",
        "fields": [
            {"target": {"page": 0, "x": 482, "y": 132, "fontsize": 9.5}, "source": "applicant_profile.location.ward_no", "transform": "upper", "mandatory": True},
            {"target": {"page": 0, "x": 468, "y": 146, "fontsize": 9}, "source": "applicant_profile.domain_attributes.enlistment_year", "mandatory": False},
            {"target": {"page": 0, "x": 242, "y": 160, "fontsize": 9.5}, "source": "applicant_profile.location.municipal_ward_or_block", "transform": "upper", "mandatory": True},
            {"target": {"page": 0, "x": 270, "y": 236, "fontsize": 9.5}, "source": "applicant_profile.applicant.name", "transform": "upper", "mandatory": True},
            {"target": {"page": 0, "x": 270, "y": 256, "fontsize": 9.5}, "source": "applicant_profile.entity_name", "transform": "upper", "mandatory": True},
            {"target": {"page": 0, "x": 270, "y": 276, "fontsize": 9}, "source": "applicant_profile.domain_attributes.commencement_date", "mandatory": False},
            {"target": {"page": 0, "x": 270, "y": 304, "fontsize": 8.5}, "source": "applicant_profile.applicant.residential_address", "transform": "upper", "mandatory": True},
            {"target": {"page": 0, "x": 330, "y": 335, "fontsize": 8.5}, "source": "applicant_profile.location.holding_no", "transform": "upper", "mandatory": False},
            {"target": {"page": 0, "x": 268, "y": 354, "fontsize": 8.5}, "source": "applicant_profile.location.address", "transform": "upper", "mandatory": True},
            {"target": {"page": 0, "x": 316, "y": 374, "fontsize": 9}, "source": "applicant_profile.location.ward_no", "transform": "upper", "mandatory": True},
            {"target": {"page": 0, "x": 270, "y": 397, "fontsize": 9}, "source": "applicant_profile.activity_type", "transform": "upper", "mandatory": True},
            {"target": {"page": 0, "x": 270, "y": 514, "fontsize": 8}, "source": "applicant_profile.domain_attributes.additional_info", "mandatory": False},
            {"target": {"page": 0, "x": 428, "y": 514, "fontsize": 9.5}, "source": "applicant_profile.applicant.phone", "transform": "phone_10digit", "mandatory": True},
            {"target": {"page": 0, "x": 415, "y": 614, "fontsize": 9}, "source": "applicant_profile.domain_attributes.enlistment_year", "mandatory": False},
            {"target": {"page": 0, "x": 70, "y": 668, "fontsize": 9}, "source": "applicant_profile.domain_attributes.commencement_date", "mandatory": False},
        ],
    }

    # 2. REAL OFFICIAL WB SHOPS & ESTABLISHMENTS ACT, 1963 — FORM B (3p, 595 x 842)
    # Verified via PyMuPDF text bounding boxes on WB_Shops_Establishment_Form_B_Official.pdf
    shops_form_b_map = {
        "form": "WB_Shops_Establishment_Form_B_Official.pdf",
        "licence_id": "lic_wb_shops_and_establishments",
        "official_url": "https://storage.googleapis.com/firebase-greythr-website.appspot.com/flamelink/media/compliances/SE_AOR/Form%20B%20-%20Application%20for%20Registration.pdf?GoogleAccessId=firebase-adminsdk-jpzmh%40firebase-greythr-website.iam.gserviceaccount.com&Expires=16725205800&Signature=Wu3cR4i2mUSqaCcCNBc%2Ftk%2B8QIq9gNcCaa44ztpb5GcRWSC5uD5G4%2BWzXgzADovmQ8fm1eHBhBB08xGHE2mU6X5E6slPZ%2BaZCaUDFEOmOkXAdsgxWSgb7nZqQnscGY%2FxJCheLFyKvpk7LkzLeRYjqX%2B2QpcNtfNKNGz9kD9k3PBPj7EMvwmnBGoPv63gykOPM8htm8lVnE8DmtkWitAN7XoYDsa3yKgALilqm7GA8unvmjmBqgYbQ5i%2Bw%2FNEFbEQl0SYZn7SHScHNGBYXG2Q%2FnKNDwbtj7mUnHdVYvtVrZptUtrp0XDmwAvQTHXKzWaoeGULsqg7%2BurPjmFVpoEpmw%3D%3D",
        "coord_origin": "top-left",
        "fields": [
            {"target": {"page": 0, "x": 200, "y": 326, "fontsize": 9}, "source": "applicant_profile.location.municipal_ward_or_block", "transform": "upper", "mandatory": True},
            {"target": {"page": 0, "x": 248, "y": 535, "fontsize": 9.5}, "source": "applicant_profile.entity_name", "transform": "upper", "mandatory": True},
            {"target": {"page": 0, "x": 72, "y": 568, "fontsize": 9}, "source": "applicant_profile.location.address", "transform": "upper", "mandatory": True},
            {"target": {"page": 0, "x": 248, "y": 621, "fontsize": 9.5}, "source": "applicant_profile.applicant.name", "transform": "upper", "mandatory": True},
            {"target": {"page": 0, "x": 72, "y": 654, "fontsize": 9}, "source": "applicant_profile.applicant.residential_address", "transform": "upper", "mandatory": True},
            {"target": {"page": 1, "x": 72, "y": 106, "fontsize": 9}, "source": "applicant_profile.activity_type", "transform": "upper", "mandatory": True},
            {"target": {"page": 1, "x": 180, "y": 134, "fontsize": 9}, "source": "applicant_profile.activity_type", "transform": "upper", "mandatory": False},
            {"target": {"page": 1, "x": 250, "y": 152, "fontsize": 9}, "source": "applicant_profile.domain_attributes.commencement_date", "mandatory": False},
            {"target": {"page": 1, "x": 418, "y": 468, "fontsize": 9.5}, "source": "applicant_profile.domain_attributes.workers_on_site", "mandatory": True},
            {"target": {"page": 1, "x": 72, "y": 519, "fontsize": 9}, "source": "applicant_profile.domain_attributes.weekly_closing_day", "transform": "upper", "mandatory": True},
            {"target": {"page": 1, "x": 96, "y": 631, "fontsize": 9}, "source": "applicant_profile.domain_attributes.commencement_date", "mandatory": False},
        ],
    }

    # 3. REAL OFFICIAL FSSAI FORM A (5p, 595 x 842)
    # Verified on FSSAI_Form_A_Official_p0_grid.png and p1_grid.png
    fssai_a_map = {
        "form": "FSSAI_Form_A_Official.pdf",
        "licence_id": "lic_fssai_basic_registration",
        "official_url": "https://foscos.fssai.gov.in/assets/docs/registrationForm_A.pdf",
        "coord_origin": "top-left",
        "fields": [
            {"target": {"page": 0, "x": 355, "y": 496, "fontsize": 9.5}, "source": "applicant_profile.activity_type", "transform": "upper", "mandatory": True},
            {"target": {"page": 0, "x": 85, "y": 572, "fontsize": 10}, "source": "applicant_profile.entity_name", "transform": "upper", "mandatory": True},
            {"target": {"page": 0, "x": 73, "y": 674, "fontsize": 10}, "source": "applicant_profile.applicant.name", "transform": "upper", "mandatory": False},
            {"target": {"page": 1, "x": 265, "y": 82, "fontsize": 9.5}, "source": "applicant_profile.applicant.pan", "transform": "pan", "mandatory": False},
            {"target": {"page": 1, "x": 70, "y": 200, "fontsize": 9}, "source": "applicant_profile.applicant.residential_address", "transform": "upper", "mandatory": True},
            {"target": {"page": 1, "x": 262, "y": 300, "fontsize": 9.5}, "source": "applicant_profile.applicant.phone", "transform": "phone_10digit", "mandatory": True},
            {"target": {"page": 1, "x": 235, "y": 329, "fontsize": 9}, "source": "applicant_profile.applicant.email", "mandatory": False},
            {"target": {"page": 1, "x": 70, "y": 474, "fontsize": 9}, "source": "applicant_profile.location.address", "transform": "upper", "mandatory": True},
            {"target": {"page": 1, "x": 110, "y": 638, "fontsize": 8.5}, "source": "applicant_profile.activity_type", "transform": "upper", "mandatory": False},
        ],
    }

    # 4. REAL OFFICIAL FSSAI FORM B (5p, 595 x 842)
    fssai_b_map = {
        "form": "FSSAI_Form_B_Official.pdf",
        "licence_id": "lic_fssai_state",
        "official_url": "https://foscos.fssai.gov.in/assets/docs/stateForm_b.pdf",
        "coord_origin": "top-left",
        "fields": [
            {"target": {"page": 1, "x": 220, "y": 150, "fontsize": 9.5}, "source": "applicant_profile.applicant.name", "transform": "upper", "mandatory": True},
            {"target": {"page": 1, "x": 220, "y": 188, "fontsize": 9.5}, "source": "applicant_profile.entity_name", "transform": "upper", "mandatory": True},
            {"target": {"page": 1, "x": 220, "y": 235, "fontsize": 9}, "source": "applicant_profile.location.address", "transform": "upper", "mandatory": True},
            {"target": {"page": 1, "x": 220, "y": 310, "fontsize": 9.5}, "source": "applicant_profile.applicant.phone", "transform": "phone_10digit", "mandatory": True},
            {"target": {"page": 1, "x": 220, "y": 355, "fontsize": 9}, "source": "applicant_profile.domain_attributes.expected_annual_turnover_inr", "transform": "inr_words", "mandatory": True},
        ],
    }

    # 5. REAL OFFICIAL WB PROFESSIONAL TAX FORM II (3p, 595 x 842)
    # Verified on WB_Professional_Tax_Form_II_Official_p0_grid.png
    ptax_map = {
        "form": "WB_Professional_Tax_Form_II_Official.pdf",
        "licence_id": "lic_wb_ptax",
        "official_url": "https://raniganjchamber.com/usefulforms/professional%20tax%20enrolment.pdf",
        "coord_origin": "top-left",
        "fields": [
            {"target": {"page": 0, "x": 42, "y": 176, "fontsize": 9}, "source": "applicant_profile.location.district", "transform": "upper", "mandatory": False},
            {"target": {"page": 0, "x": 250, "y": 302, "fontsize": 9.5}, "source": "applicant_profile.applicant.name", "transform": "upper", "mandatory": True},
            {"target": {"page": 0, "x": 250, "y": 328, "fontsize": 9.5}, "source": "applicant_profile.entity_name", "transform": "upper", "mandatory": True},
            {"target": {"page": 0, "x": 250, "y": 354, "fontsize": 8.5}, "source": "applicant_profile.location.address", "transform": "upper", "mandatory": True},
            {"target": {"page": 0, "x": 250, "y": 410, "fontsize": 8.5}, "source": "applicant_profile.location.district", "transform": "upper", "mandatory": False},
            {"target": {"page": 0, "x": 250, "y": 448, "fontsize": 8.5}, "source": "applicant_profile.applicant.residential_address", "transform": "upper", "mandatory": True},
            {"target": {"page": 0, "x": 250, "y": 498, "fontsize": 8.5}, "source": "applicant_profile.location.district", "transform": "upper", "mandatory": False},
            {"target": {"page": 0, "x": 250, "y": 560, "fontsize": 9}, "source": "applicant_profile.domain_attributes.commencement_date", "mandatory": False},
            {"target": {"page": 0, "x": 305, "y": 682, "fontsize": 9}, "source": "applicant_profile.domain_attributes.expected_annual_turnover_inr", "transform": "inr_words", "mandatory": False},
        ],
    }

    # 6. REAL OFFICIAL GST FORM GST REG-01 (12p, 595 x 842)
    # Verified on GST_REG_01_Official_p0_grid.png
    gst_map = {
        "form": "GST_REG_01_Official.pdf",
        "licence_id": "lic_gst_reg",
        "official_url": "https://taxindiaonline.com/RC2/pdfnoti/gst/gst_forms/2017/GST%20REG-01.pdf",
        "coord_origin": "top-left",
        "fields": [
            {"target": {"page": 0, "x": 378, "y": 248, "fontsize": 8.5}, "source": "applicant_profile.location.state", "transform": "upper", "mandatory": False},
            {"target": {"page": 0, "x": 470, "y": 248, "fontsize": 8.5}, "source": "applicant_profile.location.district", "transform": "upper", "mandatory": False},
            {"target": {"page": 0, "x": 462, "y": 276, "fontsize": 9}, "source": "applicant_profile.applicant.name", "transform": "upper", "mandatory": True},
            {"target": {"page": 0, "x": 462, "y": 318, "fontsize": 9.5}, "source": "applicant_profile.applicant.pan", "transform": "pan", "mandatory": True},
            {"target": {"page": 0, "x": 462, "y": 356, "fontsize": 8.5}, "source": "applicant_profile.applicant.email", "mandatory": False},
            {"target": {"page": 0, "x": 462, "y": 378, "fontsize": 9}, "source": "applicant_profile.applicant.phone", "transform": "phone_10digit", "mandatory": True},
            {"target": {"page": 0, "x": 250, "y": 474, "fontsize": 9.5}, "source": "applicant_profile.entity_name", "transform": "upper", "mandatory": True},
        ],
    }

    maps = {
        "wb_municipal_form_j_official_map.json": form_j_map,
        "wb_shops_form_b_official_map.json": shops_form_b_map,
        "fssai_form_a_official_map.json": fssai_a_map,
        "fssai_form_b_official_map.json": fssai_b_map,
        "wb_ptax_form_ii_official_map.json": ptax_map,
        "gst_reg_01_official_map.json": gst_map,
    }
    for fname, data in maps.items():
        (OFFICIAL_DIR / fname).write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"Wrote calibrated official map: {fname} ({len(data['fields'])} fields)")


if __name__ == "__main__":
    write_maps()
