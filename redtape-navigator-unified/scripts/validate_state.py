#!/usr/bin/env python3
"""Audit unified state.json against RedTape Navigator rules:
- Strict government domains (.gov.in, .nic.in, .gov, .org.in)
- 30-day source freshness check
- Taxonomy, conflict & dependency integrity
- Indian ID/contact formats (PAN, 10-digit mobile, 6-digit PIN)
- Cross-document & statutory tier consistency (e.g. FSSAI turnover tiers)
- Supporting document coverage & artifact existence
Usage: python3 validate_state.py state.json [--write]
"""
import argparse
import datetime
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _common import effective_value, get_path, is_blank, load_json, save_json

STATUSES = {"Required", "Conditional", "Not Applicable", "Needs Verification"}
STRICT_GOV_SUFFIXES = (".gov.in", ".nic.in", ".gov", ".org.in")
KNOWN_MUNICIPAL_HOSTS = {"kmcgov.in", "www.kmcgov.in"}
PAN_RE = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
MOBILE_RE = re.compile(r"^[6-9][0-9]{9}$")
PIN_RE = re.compile(r"^[1-9][0-9]{5}$")


def _days_old(iso_date_str):
    try:
        d = datetime.date.fromisoformat(str(iso_date_str)[:10])
        return (datetime.date.today() - d).days
    except ValueError:
        return None


def validate(state):
    errors, warnings = [], []
    ids = set()

    # 1. Core profile checks
    for key in ("applicant_profile.location.city_or_village", "applicant_profile.activity_type"):
        if is_blank(effective_value(state, key)):
            errors.append(f"profile field {key} is empty")

    # 2. Format validation on populated Indian identifiers
    pan = effective_value(state, "applicant_profile.applicant.pan")
    if not is_blank(pan) and not PAN_RE.match(str(pan).strip().upper()):
        errors.append("applicant_profile.applicant.pan does not match valid PAN format (AAAAA9999A)")

    phone = effective_value(state, "applicant_profile.applicant.phone")
    if not is_blank(phone):
        digits = re.sub(r"\D", "", str(phone))
        if len(digits) == 12 and digits.startswith("91"):
            digits = digits[2:]
        if not MOBILE_RE.match(digits):
            warnings.append("applicant_profile.applicant.phone is not a standard 10-digit Indian mobile number")

    pin = effective_value(state, "applicant_profile.location.pin")
    if not is_blank(pin) and not PIN_RE.match(str(pin).strip()):
        errors.append(f"applicant_profile.location.pin ({pin}) is not a valid 6-digit Indian PIN code")

    # 3. Compliance matrix checks
    turnover = effective_value(state, "applicant_profile.domain_attributes.expected_annual_turnover_inr")
    for i, r in enumerate(state.get("compliance_matrix", [])):
        tag = r.get("id") or f"row[{i}]"
        if tag in ids:
            errors.append(f"{tag}: duplicate id")
        ids.add(tag)
        st = r.get("status")
        if st not in STATUSES:
            errors.append(f"{tag}: invalid status {st!r}")
            continue
        if is_blank(r.get("rationale")):
            errors.append(f"{tag}: missing rationale")
        url = r.get("official_source_url")
        if is_blank(url):
            if st != "Needs Verification":
                errors.append(f"{tag}: {st} requires official_source_url (otherwise mark Needs Verification)")
        else:
            host = url.split("//")[-1].split("/")[0].lower()
            if not (host.endswith(STRICT_GOV_SUFFIXES) or host in KNOWN_MUNICIPAL_HOSTS):
                warnings.append(f"{tag}: source host '{host}' is not an official government domain (.gov.in/.nic.in/.gov)")
            ver = r.get("source_verified_at")
            if is_blank(ver):
                warnings.append(f"{tag}: not live-verified (source_verified_at empty); flag snapshot warning to user")
            else:
                age = _days_old(ver)
                if age is not None and age > 30:
                    warnings.append(f"{tag}: source verification is {age} days old (>30 days); re-verify before submission")
        if st == "Conditional":
            deps = r.get("depends_on") or []
            if not deps:
                errors.append(f"{tag}: Conditional row must declare depends_on[]")
            for d in deps:
                if is_blank(effective_value(state, d)):
                    warnings.append(f"{tag}: unresolved dependency {d}")
        if st == "Needs Verification" and not (r.get("conflicts") or r.get("note")):
            warnings.append(f"{tag}: Needs Verification should document conflicts[] or a gap note")

        # FSSAI tier consistency check
        if st == "Required" and isinstance(turnover, (int, float)):
            lname = (r.get("name") or "").lower()
            if "fssai" in lname and "basic" in lname and turnover >= 1_200_000:
                errors.append(f"{tag}: FSSAI Basic Registration selected but turnover ({turnover}) >= Rs. 12 Lakhs (requires State/Central License)")
            elif "fssai" in lname and "central" in lname and turnover < 200_000_000:
                warnings.append(f"{tag}: FSSAI Central License selected with turnover ({turnover}) < Rs. 20 Crore — confirm multi-state/export trigger")

    # 4. Open questions hygiene
    for q in state.get("open_questions", []):
        if not is_blank(effective_value(state, q)):
            warnings.append(f"open_questions still lists {q} even though it is already populated")

    # 5. Form & Portal artifact checks
    for fa in state.get("form_artifacts", []):
        name = fa.get("form_name", "?")
        miss = fa.get("missing_fields") or []
        if miss:
            warnings.append(f"{name}: {len(miss)} pending mandatory field(s): {', '.join(miss)}")
        if fa.get("completion_percentage") is None:
            errors.append(f"{name}: completion_percentage missing")
        fp = fa.get("file_path")
        if fp and not os.path.exists(fp):
            warnings.append(f"{name}: draft file not found at {fp}")

    for pa in state.get("portal_artifacts", []):
        name = pa.get("portal_name", "?")
        miss = pa.get("missing_fields") or []
        if miss:
            warnings.append(f"{name} (portal): {len(miss)} pending mandatory field(s): {', '.join(miss)}")
        cp = pa.get("copy_sheet_path")
        if cp and not os.path.exists(cp):
            warnings.append(f"{name}: portal copy sheet not found at {cp}")

    # 6. Supporting document coverage
    if any(r.get("status") in ("Required", "Conditional") for r in state.get("compliance_matrix", []))             and not state.get("required_supporting_documents"):
        errors.append("no required_supporting_documents catalogued")

    return {
        "passed": not errors,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "errors": errors,
        "warnings": warnings,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("state")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    st = load_json(a.state)
    res = validate(st)
    if a.write:
        st["validation"] = res
        st.setdefault("workflow_flags", {})["validation_passed"] = res["passed"]
        save_json(a.state, st)
    print("PASSED" if res["passed"] else "FAILED")
    for e in res["errors"]:
        print("  ERROR:", e)
    for w in res["warnings"]:
        print("  WARN: ", w)
    sys.exit(0 if res["passed"] else 1)


if __name__ == "__main__":
    main()
