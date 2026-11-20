# PDF Form Filling Reference

## Dual-Backend Architecture
- **Preferred:** PyMuPDF (`fitz`) — fastest AcroForm + flat coordinate overlay + PNG rendering.
- **Automatic Fallback:** `pypdf` (+ `reportlab` for flat overlays, `pdfplumber` for anchors, `pypdfium2` for PNG rendering) so scripts run cleanly even in lightweight containers without PyMuPDF.

## Coordinate Convention (Important!)
- `inspect_pdf.py` and `field_map.json` ALWAYS use **top-left origin** (`x` right, `y` down from top edge in PDF points).
- When `fill_pdf.py` runs on the `pypdf` + `reportlab` fallback, it automatically converts `y` to ReportLab's bottom-left origin (`page_height - y`).

## Supported Transforms
`upper`, `title`, `digits`, `phone_10digit` (strips `+91`/`0`), `pan` (uppercase, no spaces), `date_ddmmyyyy`, `inr_words` (`800000` → `Rs. 8 Lakhs`), `comma_list`.

## Missing Mandatory Fields
Never guess. Pass `--stamp-pending` for review drafts to stamp `[PENDING_USER_INPUT]` on both AcroForm widgets and flat PDF coordinates.
