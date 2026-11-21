#!/usr/bin/env python3
"""Unified Document & Digital Web Portal Generation Engine for RedTape Navigator.
Strictly separates:
- Channel A (Offline Submittable Official PDFs): Real government PDFs in assets/official_pdfs/
  filled one-by-one after inspecting their required fields and collecting missing values.
- Channel B (Online Portal-Only Clearances): Digital-only portals (KMC, SilpaSathi, Udyam, FoSCoS)
  where no offline PDF exists — generates field-by-field copy-sheets & manifests.
Zero arbitrary synthetic PDFs for portal-only clearances.
"""
import argparse
import os
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPTS_DIR.parent
ASSETS_DIR = ROOT_DIR / "assets"
OFFICIAL_DIR = ASSETS_DIR / "official_pdfs"
PORTALS_DIR = ASSETS_DIR / "portals"
TEMPLATES_DIR = ASSETS_DIR / "templates"

sys.path.insert(0, str(SCRIPTS_DIR))
from _common import effective_value, is_blank, load_json, save_json
from fill_pdf import fill
from generate_portal_pack import build_portal_pack

# Registry of REAL downloadable offline government PDFs & their calibrated coordinate maps
OFFICIAL_PDF_MAPS = {
    "lic_municipal_form_j": OFFICIAL_DIR / "wb_municipal_form_j_official_map.json",
    "lic_wb_shops_and_establishments": OFFICIAL_DIR / "wb_shops_form_b_official_map.json",
    "lic_fssai_basic_registration": OFFICIAL_DIR / "fssai_form_a_official_map.json",
    "lic_fssai_state": OFFICIAL_DIR / "fssai_form_b_official_map.json",
    "lic_wb_ptax": OFFICIAL_DIR / "wb_ptax_form_ii_official_map.json",
    "lic_gst_reg": OFFICIAL_DIR / "gst_reg_01_official_map.json",
}

PORTAL_MAPS = {
    "lic_fssai_basic_registration": PORTALS_DIR / "foscos_portal_map.json",
    "lic_fssai_state": PORTALS_DIR / "foscos_portal_map.json",
    "lic_kmc_ce": PORTALS_DIR / "kmc_trade_license_portal_map.json",
    "lic_wb_shops_and_establishments": PORTALS_DIR / "silpasathi_portal_map.json",
    "lic_municipal_building_sanction": PORTALS_DIR / "bmc_building_plan_portal_map.json",
    "grant_pmksy_micro_irrigation": PORTALS_DIR / "banglar_krishi_portal_map.json",
}

FIELD_HUMAN_LABELS = {
    "applicant_profile.applicant.name": "Proprietor / Applicant Full Name",
    "applicant_profile.entity_name": "Shop / Business Name",
    "applicant_profile.location.address": "Shop Full Street Address",
    "applicant_profile.location.ward_no": "Municipal Ward Number (e.g. Ward 12)",
    "applicant_profile.applicant.phone": "10-Digit Mobile Number",
    "applicant_profile.applicant.pan": "PAN Number (10 characters, e.g. ABCDE1234F)",
    "applicant_profile.applicant.residential_address": "Proprietor Residential Address",
    "applicant_profile.location.municipal_ward_or_block": "Municipality / Local Body",
    "applicant_profile.location.district": "District",
    "applicant_profile.location.holding_no": "Premises Holding Number",
    "applicant_profile.activity_type": "Nature of Trade / Business",
    "applicant_profile.domain_attributes.expected_annual_turnover_inr": "Expected Annual Turnover (INR)",
    "applicant_profile.domain_attributes.floor_area_sqft": "Shop Floor Area (sq ft)",
    "applicant_profile.domain_attributes.workers_on_site": "Number of Staff on Site",
    "applicant_profile.domain_attributes.weekly_closing_day": "Weekly Closing Day (e.g. Sunday / Open 7 Days)",
    "applicant_profile.location.premises_type": "Premises Ownership (Rented or Owned)",
}


def resolve_permit_target(lic_id: str, name: str = "") -> str:
    combined = f"{lic_id} {name}".lower()
    if lic_id == "lic_fssai_state" or "state food license" in combined or ("form b" in combined and "fssai" in combined):
        return "lic_fssai_state"
    if "fssai" in combined or "food" in combined:
        return "lic_fssai_basic_registration"
    if lic_id == "lic_kmc_ce" or "kmc" in combined:
        return "lic_kmc_ce"
    if lic_id in ("lic_panihati_ce", "lic_barrackpore_ce", "lic_municipal_form_j") or "form j" in combined or "enlistment" in combined or "trade license" in combined:
        return "lic_municipal_form_j"
    if "shop" in combined or "establishment" in combined or "silpasathi" in combined:
        return "lic_wb_shops_and_establishments"
    if lic_id == "lic_wb_ptax" or "professional tax" in combined or "form ii" in combined:
        return "lic_wb_ptax"
    if lic_id == "lic_gst_reg" or "gst" in combined:
        return "lic_gst_reg"
    if lic_id == "lic_udyam_msme" or "udyam" in combined or "msme" in combined:
        return "lic_udyam_msme"
    if lic_id == "lic_wb_fire_advisory" or ("textile" in combined and "fire" in combined):
        return "lic_wb_fire_advisory"
    if lic_id == "lic_wb_fire" or "fire" in combined:
        return "lic_wb_fire"
    if lic_id == "lic_wb_signage" or "signboard" in combined or "fascia" in combined:
        return "lic_wb_signage"
    if "building" in combined or "sanction" in combined or "zoning" in combined or "floor" in combined or "bmc" in combined:
        return "lic_municipal_building_sanction"
    if "pmksy" in combined or "drip" in combined or "micro_irrigation" in combined or "micro irrigation" in combined:
        return "grant_pmksy_micro_irrigation"
    if "kusum" in combined or "solar pump" in combined:
        return "grant_pm_kusum"
    return lic_id


def has_offline_official_pdf(lic_id: str, permit_name: str = "") -> bool:
    """Returns True iff a real downloadable offline official PDF exists for this permit."""
    canon = resolve_permit_target(lic_id, permit_name)
    mp = OFFICIAL_PDF_MAPS.get(canon)
    if not mp or not mp.exists():
        return False
    fmap = load_json(mp)
    return (OFFICIAL_DIR / fmap["form"]).exists()


def get_official_pdf_entry(lic_id: str, permit_name: str = "") -> dict | None:
    """Loads metadata and field map for a single offline official government PDF."""
    canon = resolve_permit_target(lic_id, permit_name)
    mp = OFFICIAL_PDF_MAPS.get(canon)
    if not mp or not mp.exists():
        return None
    fmap = load_json(mp)
    pdf_path = OFFICIAL_DIR / fmap["form"]
    if not pdf_path.exists():
        return None
    return {
        "canon_id": canon,
        "licence_id": lic_id,
        "permit_name": permit_name or fmap["form"],
        "form_name": fmap["form"],
        "official_url": fmap.get("official_url"),
        "pdf_path": str(pdf_path),
        "map_path": str(mp),
        "field_map": fmap,
    }


def get_required_offline_pdfs(state: dict) -> list[dict]:
    """Returns ordered list of offline official PDFs applicable to Required permits in state."""
    queue = []
    seen = set()
    for permit in state.get("compliance_matrix", []):
        if permit.get("status") != "Required":
            continue
        lic_id = permit.get("id", "")
        permit_name = permit.get("name", lic_id)
        entry = get_official_pdf_entry(lic_id, permit_name)
        if entry and entry["form_name"] not in seen:
            seen.add(entry["form_name"])
            queue.append(entry)
    return queue


def inspect_pdf_fields(pdf_entry: dict, state: dict) -> tuple[list[dict], list[dict]]:
    """Inspects a specific official PDF's required fields against current state.
    Returns (known_fields, missing_fields) where each item has {'source', 'label', 'value'}.
    """
    fmap = pdf_entry.get("field_map") or load_json(pdf_entry["map_path"])
    known, missing = [], []
    seen_sources = set()
    for f in fmap.get("fields", []):
        if not f.get("mandatory"):
            continue
        src = f["source"]
        if src in seen_sources:
            continue
        seen_sources.add(src)
        val = effective_value(state, src)
        label = FIELD_HUMAN_LABELS.get(src, src.split(".")[-1].replace("_", " ").title())
        if is_blank(val):
            missing.append({"source": src, "label": label, "value": None})
        else:
            known.append({"source": src, "label": label, "value": val})
    return known, missing


def fill_single_official_pdf(pdf_entry: dict, state: dict, output_dir: str = None) -> dict:
    """Stamps user details directly onto ONE real official government PDF and returns its artifact dict."""
    proj_id = state.get("project_id", "default_project")
    base_out = Path(output_dir) if output_dir else ROOT_DIR / "drafts" / proj_id
    base_out.mkdir(parents=True, exist_ok=True)

    fmap = pdf_entry.get("field_map") or load_json(pdf_entry["map_path"])
    out_pdf_path = base_out / f"filled_{fmap['form']}"
    report_path = base_out / f"filled_{fmap['form']}.report.json"

    report = fill(pdf_entry["pdf_path"], fmap, state, str(out_pdf_path), stamp_pending=True)
    save_json(str(report_path), report)

    completion = report.get("completion_percentage", 0)
    return {
        "form_name": fmap["form"],
        "permit_name": pdf_entry.get("permit_name", fmap["form"]),
        "licence_id": pdf_entry.get("licence_id"),
        "official_source_url": fmap.get("official_url"),
        "is_official_pdf": True,
        "status": "Official_PDF_Filled",
        "completion_percentage": completion,
        "fields_filled": f"{completion}%",
        "missing_fields": report.get("missing_fields", []),
        "file_path": str(out_pdf_path),
        "pdf_path": str(out_pdf_path),
        "report_path": str(report_path),
    }


def precheck_supporting_documents(state: dict, draft_dir: Path) -> list[dict]:
    """Inspect required attachments, annotate precheck_status, and stage legal templates."""
    raw_docs = state.get("required_supporting_documents", [])
    updated_docs = []
    ap = state.get("applicant_profile", {})
    applicant = ap.get("applicant", {})
    location = ap.get("location", {})

    for item in raw_docs:
        doc = dict(item) if isinstance(item, dict) else {"name": str(item), "needed_for": []}
        name_lower = doc.get("name", "").lower()

        if any(term in name_lower for term in ("rent", "noc", "landlord", "possession")):
            noc_tpl = TEMPLATES_DIR / "landlord_noc_template.md"
            if noc_tpl.exists():
                staged_path = draft_dir / "draft_landlord_noc.md"
                content = noc_tpl.read_text(encoding="utf-8")
                content = content.replace("{applicant_name}", applicant.get("name") or "[APPLICANT_NAME]")
                content = content.replace("{entity_name}", ap.get("entity_name") or "[BUSINESS_NAME]")
                content = content.replace("{activity_type}", ap.get("activity_type") or "commercial operations")
                content = content.replace("{city_or_village}", location.get("city_or_village") or "Kolkata")
                staged_path.write_text(content, encoding="utf-8")
                doc["precheck_status"] = "Template_Available"
                doc["template_path"] = str(staged_path)
            else:
                doc["precheck_status"] = "Action_Required"
        elif any(term in name_lower for term in ("food category", "hygiene", "sanitary", "schedule 4")):
            hygiene_tpl = TEMPLATES_DIR / "food_safety_hygiene_declaration.md"
            if hygiene_tpl.exists():
                staged_path = draft_dir / "draft_food_hygiene_declaration.md"
                content = hygiene_tpl.read_text(encoding="utf-8")
                content = content.replace("{applicant_name}", applicant.get("name") or "[APPLICANT_NAME]")
                content = content.replace("{entity_name}", ap.get("entity_name") or "[BUSINESS_NAME]")
                content = content.replace("{activity_type}", ap.get("activity_type") or "bakery operations")
                content = content.replace("{premises_address}", location.get("address") or location.get("municipal_ward_or_block") or "[PREMISES_ADDRESS]")
                content = content.replace("{city_or_village}", location.get("city_or_village") or "Kolkata")
                staged_path.write_text(content, encoding="utf-8")
                doc["precheck_status"] = "Template_Available"
                doc["template_path"] = str(staged_path)
            else:
                doc["precheck_status"] = "Action_Required"
        elif any(term in name_lower for term in ("id", "photo", "pan", "aadhaar")):
            pan_val = effective_value(state, "applicant_profile.applicant.pan")
            doc["precheck_status"] = "Document_On_File" if not is_blank(pan_val) else "Action_Required"
        else:
            doc["precheck_status"] = "Action_Required"
        updated_docs.append(doc)
    return updated_docs


def generate_portal_packs_only(state: dict, output_dir: str = None) -> list[dict]:
    """Generates field-by-field copy-sheets for online-portal-only clearances."""
    proj_id = state.get("project_id", "default_project")
    base_out = Path(output_dir) if output_dir else ROOT_DIR / "drafts" / proj_id
    base_out.mkdir(parents=True, exist_ok=True)

    portal_artifacts = []
    seen = set()
    for permit in state.get("compliance_matrix", []):
        if permit.get("status") != "Required":
            continue
        lic_id = permit.get("id", "")
        canon = resolve_permit_target(lic_id, permit.get("name", ""))
        pmap_path = PORTAL_MAPS.get(canon)
        if not pmap_path or not pmap_path.exists() or pmap_path.name in seen:
            continue
        seen.add(pmap_path.name)
        pmap = load_json(pmap_path)
        clean_name = pmap_path.stem.replace("_portal_map", "")
        out_md_path = base_out / f"{clean_name}_pack.md"
        out_man_path = base_out / f"{clean_name}_manifest.json"
        md_text, manifest = build_portal_pack(pmap, state)
        out_md_path.write_text(md_text, encoding="utf-8")
        save_json(str(out_man_path), manifest)
        completion = manifest.get("completion_percentage", 0)
        portal_artifacts.append({
            "portal_name": pmap["portal_name"],
            "licence_id": lic_id,
            "portal_url": pmap["portal_url"],
            "status": "Ready_For_User_Submit" if completion == 100 else "Pack_Generated",
            "completion_percentage": completion,
            "missing_fields": manifest.get("missing_fields", []),
            "copy_sheet_path": str(out_md_path),
            "file_path": str(out_md_path),
            "manifest_path": str(out_man_path),
            "human_gates": manifest.get("stop_before_gates", []),
        })
    state["required_supporting_documents"] = precheck_supporting_documents(state, base_out)
    return portal_artifacts


def generate_documents(state: dict, output_dir: str = None) -> dict:
    """Batch-fills all applicable REAL offline official PDFs + online portal copy-sheets."""
    proj_id = state.get("project_id", "default_project")
    base_out = Path(output_dir) if output_dir else ROOT_DIR / "drafts" / proj_id
    base_out.mkdir(parents=True, exist_ok=True)

    pdf_queue = get_required_offline_pdfs(state)
    form_artifacts = []
    for entry in pdf_queue:
        art = fill_single_official_pdf(entry, state, output_dir=str(base_out))
        form_artifacts.append(art)

    portal_artifacts = generate_portal_packs_only(state, output_dir=str(base_out))

    state["form_artifacts"] = form_artifacts
    state["portal_artifacts"] = portal_artifacts
    state.setdefault("workflow_flags", {})["documents_generated"] = True
    return state


def main():
    ap = argparse.ArgumentParser(description="Document & Digital Portal Generation Engine.")
    ap.add_argument("state_file", help="Path to state.json")
    ap.add_argument("--out", help="Path to save updated state.json (defaults to overwriting input)")
    ap.add_argument("--drafts-dir", help="Target directory for generated PDFs and portal packs")
    args = ap.parse_args()

    state = load_json(args.state_file)
    updated = generate_documents(state, output_dir=args.drafts_dir)
    out_file = args.out or args.state_file
    save_json(out_file, updated)
    print(f"Saved updated state to {out_file}.")


if __name__ == "__main__":
    main()
