#!/usr/bin/env python3
"""Generate official-style blank PDF application forms with AcroForm widgets for testing and demonstration."""
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

ASSETS_FORMS = Path(__file__).resolve().parent.parent / "assets" / "forms"
ASSETS_FORMS.mkdir(parents=True, exist_ok=True)


def build_fssai_form_a():
    pdf_path = ASSETS_FORMS / "FSSAI_Registration_Form_A.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, 750, "GOVERNMENT OF INDIA")
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, 732, "FOOD SAFETY AND STANDARDS AUTHORITY OF INDIA")
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, 716, "FORM A — APPLICATION FOR REGISTRATION UNDER FSS ACT, 2006")
    c.line(50, 706, width - 50, 706)

    form = c.acroForm

    # 1. Applicant Name
    c.setFont("Helvetica", 10)
    c.drawString(60, 675, "1. Name of Applicant / Food Business Operator:")
    form.textfield(name="applicant_name", x=60, y=648, width=490, height=22, borderStyle="underlined")

    # 2. Business Entity Name
    c.drawString(60, 625, "2. Name of Business Entity / Enterprise:")
    form.textfield(name="business_name", x=60, y=598, width=490, height=22, borderStyle="underlined")

    # 3. Address
    c.drawString(60, 575, "3. Address of Premises where Food Business is Carried Out:")
    form.textfield(name="premises_address", x=60, y=548, width=490, height=22, borderStyle="underlined")

    # 4. Expected Annual Turnover in Words
    c.drawString(60, 525, "4. Anticipated Annual Turnover (in words):")
    form.textfield(name="annual_turnover_words", x=60, y=498, width=490, height=22, borderStyle="underlined")

    # 5. Contact Mobile & PAN
    c.drawString(60, 475, "5. Mobile Phone Number:")
    form.textfield(name="mobile_number", x=60, y=448, width=220, height=22, borderStyle="underlined")

    c.drawString(330, 475, "6. Permanent Account Number (PAN):")
    form.textfield(name="applicant_pan", x=330, y=448, width=220, height=22, borderStyle="underlined")

    # 7. Premises Ownership Checkbox
    c.drawString(60, 415, "7. Premises Ownership:")
    form.checkbox(name="owns_premises", x=60, y=388, size=16, buttonStyle="check")
    c.drawString(85, 392, "Owned by Applicant (Leave unchecked if rented/leased)")

    # 8. Date of Birth (Flat overlay field)
    c.drawString(60, 350, "8. Date of Birth of Applicant (DD/MM/YYYY):")
    c.rect(60, 322, 200, 22)

    # Footer notice
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(60, 80, "Statutory Notice: Stamped with [PENDING_USER_INPUT] for required preview fields.")
    c.drawString(60, 68, "Submission must be made via official FoSCoS portal (https://foscos.fssai.gov.in).")

    c.save()
    print(f"Generated {pdf_path}")


def build_wb_shops_form_b():
    pdf_path = ASSETS_FORMS / "WB_Shops_Establishment_Form_B.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, 750, "GOVERNMENT OF WEST BENGAL")
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width / 2, 732, "LABOUR COMMISSIONERATE — SILPASATHI SINGLE WINDOW")
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, 716, "FORM B — APPLICATION FOR REGISTRATION OF SHOP OR COMMERCIAL ESTABLISHMENT")
    c.line(50, 706, width - 50, 706)

    form = c.acroForm

    c.setFont("Helvetica", 10)
    c.drawString(60, 675, "1. Name of Shop / Commercial Establishment:")
    form.textfield(name="establishment_name", x=60, y=648, width=490, height=22, borderStyle="underlined")

    c.drawString(60, 625, "2. Category / Nature of Commercial Establishment:")
    form.textfield(name="category_of_establishment", x=60, y=598, width=490, height=22, borderStyle="underlined")

    c.drawString(60, 575, "3. Full Postal Address of Establishment:")
    form.textfield(name="premises_address", x=60, y=548, width=490, height=22, borderStyle="underlined")

    c.drawString(60, 525, "4. Total Number of Workers Employed on Site:")
    form.textfield(name="workers_count", x=60, y=498, width=220, height=22, borderStyle="underlined")

    c.drawString(60, 475, "5. Name of Employer / Managing Agent:")
    form.textfield(name="employer_name", x=60, y=448, width=490, height=22, borderStyle="underlined")

    c.drawString(60, 425, "6. Contact Mobile Number:")
    form.textfield(name="employer_phone", x=60, y=398, width=220, height=22, borderStyle="underlined")

    c.setFont("Helvetica-Oblique", 8)
    c.drawString(60, 80, "Statutory Form B under Rule 4 of the West Bengal Shops and Establishments Rules, 1964.")
    c.drawString(60, 68, "Administered online through the SilpaSathi Single Window Portal.")

    c.save()
    print(f"Generated {pdf_path}")


def build_building_plan_form():
    pdf_path = ASSETS_FORMS / "Building_Plan_Sanction_Application.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, 750, "BIDHANNAGAR MUNICIPAL CORPORATION")
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width / 2, 732, "BUILDING REGULATION & SANCTION DEPARTMENT")
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, 716, "FORM C — NOTICE OF INTENTION TO ERECT / ADD FLOORS UNDER BUILDING RULES")
    c.line(50, 706, width - 50, 706)

    form = c.acroForm

    c.setFont("Helvetica", 10)
    c.drawString(60, 675, "1. Name of Plot Owner / Applicant:")
    form.textfield(name="applicant_name", x=60, y=648, width=490, height=22, borderStyle="underlined")

    c.drawString(60, 625, "2. Premises / Plot Address:")
    form.textfield(name="plot_address", x=60, y=598, width=490, height=22, borderStyle="underlined")

    c.drawString(60, 575, "3. Total Plot Area (in Square Feet):")
    form.textfield(name="plot_area_sqft", x=60, y=548, width=220, height=22, borderStyle="underlined")

    c.drawString(330, 575, "4. Proposed Additional Floors:")
    form.textfield(name="proposed_floors", x=330, y=548, width=220, height=22, borderStyle="underlined")

    c.drawString(60, 525, "5. Width of Front Access Road (Feet):")
    form.textfield(name="road_width_ft", x=60, y=498, width=220, height=22, borderStyle="underlined")

    c.drawString(330, 525, "6. Contact Mobile Number:")
    form.textfield(name="contact_phone", x=330, y=498, width=220, height=22, borderStyle="underlined")

    c.setFont("Helvetica-Oblique", 8)
    c.drawString(60, 80, "Statutory Building Sanction Application under Section 264 of West Bengal Municipal Act.")
    c.drawString(60, 68, "Submission processed through e-District / Bidhannagar Municipal Portal.")

    c.save()
    print(f"Generated {pdf_path}")


def build_pmksy_grant_form():
    pdf_path = ASSETS_FORMS / "PMKSY_Micro_Irrigation_Application.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, 750, "GOVERNMENT OF WEST BENGAL")
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width / 2, 732, "DEPARTMENT OF AGRICULTURE & HORTICULTURE")
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, 716, "PRADHAN MANTRI KRISHI SINCHAYEE YOJANA (PMKSY) — SUBSIDY APPLICATION")
    c.line(50, 706, width - 50, 706)

    form = c.acroForm

    c.setFont("Helvetica", 10)
    c.drawString(60, 675, "1. Name of Farmer / Cultivator:")
    form.textfield(name="farmer_name", x=60, y=648, width=490, height=22, borderStyle="underlined")

    c.drawString(60, 625, "2. Village, Block, and District of Farm Land:")
    form.textfield(name="farm_location", x=60, y=598, width=490, height=22, borderStyle="underlined")

    c.drawString(60, 575, "3. Total Cultivable Landholding (Acres):")
    form.textfield(name="landholding_acres", x=60, y=548, width=220, height=22, borderStyle="underlined")

    c.drawString(330, 575, "4. Principal Crop Types:")
    form.textfield(name="crop_types", x=330, y=548, width=220, height=22, borderStyle="underlined")

    c.drawString(60, 525, "5. Current Irrigation Water Source:")
    form.textfield(name="irrigation_source", x=60, y=498, width=220, height=22, borderStyle="underlined")

    c.drawString(330, 525, "6. Contact Mobile Number:")
    form.textfield(name="mobile_number", x=330, y=498, width=220, height=22, borderStyle="underlined")

    c.setFont("Helvetica-Oblique", 8)
    c.drawString(60, 80, "PMKSY 'Per Drop More Crop' Scheme Guidelines. Subsidy credited via Direct Benefit Transfer.")
    c.drawString(60, 68, "Integrated with Banglar Krishi Portal (https://banglarkrishi.wb.gov.in).")

    c.save()
    print(f"Generated {pdf_path}")


if __name__ == "__main__":
    build_fssai_form_a()
    build_wb_shops_form_b()
    build_building_plan_form()
    build_pmksy_grant_form()
