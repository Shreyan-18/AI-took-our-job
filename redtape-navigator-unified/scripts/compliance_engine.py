#!/usr/bin/env python3
"""Compliance Classification Engine for RedTape Navigator.
Evaluates research_findings against applicant_profile (with overrides taking precedence).
Classifies into: Required, Conditional, Not Applicable, or Needs Verification.
Maintains an immutable audit trail in history[], catalogs required_supporting_documents[],
and generates open_questions for Interview.
Compatible with LangGraph state dict signature: compliance(state) -> state.
"""
import argparse
import datetime
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# Add scripts directory to path for common imports
SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPTS_DIR.parent.parent

sys.path.insert(0, str(SCRIPTS_DIR))
from _common import effective_value, load_json, save_json
from orchestrator_parser import find_api_key

COMPLIANCE_SYSTEM_PROMPT = """You are the RedTape Navigator Compliance Agent.
Your job is to evaluate each item in research_findings against applicant_profile (considering any user overrides) and classify each item into one of four statuses:

1. "Required":
   - Mandatory statutory requirement.
   - All conditions/triggers are satisfied by the current applicant_profile.
   - depends_on must be an empty list [].

2. "Conditional":
   - The requirement applies ONLY if certain profile metrics meet thresholds (e.g., turnover, floor area, customer seating, commercial LPG gas, staff count).
   - Crucially: one or more of these required profile metrics are currently NULL in applicant_profile.
   - depends_on MUST list the exact dotted paths to the missing profile fields that must be asked (e.g., ["applicant_profile.domain_attributes.expected_annual_turnover_inr"]).
   - rationale must state the threshold and what is currently unknown.

3. "Not Applicable":
   - The applicant's known profile metrics clearly fall outside the statutory triggers or qualify for an explicit exemption.
   - rationale MUST quote both the statutory threshold and the applicant's specific value (e.g., "Fire NOC not required because seating is 5 (threshold is >= 50) and commercial_lpg is false.").
   - depends_on must be [].

4. "Needs Verification":
   - The requirement has conflicts[] between municipal and state/central sources, lacks verifiable official URLs, or relies on an ambiguous circular.
   - rationale must highlight the exact ambiguity or conflict.
   - depends_on must be [].

Return a JSON array of objects matching this schema:
[
  {
    "id": "lic_id_from_research_findings",
    "name": "Licence Name",
    "authority": "Issuing Body",
    "tier": "municipal" | "state" | "central",
    "status": "Required" | "Conditional" | "Not Applicable" | "Needs Verification",
    "rationale": "Clear legal/administrative rationale quoting statutory thresholds and user metrics.",
    "depends_on": ["applicant_profile.exact.dotted.path"],
    "statutory_fee": "Fee string or null",
    "renewal_period": "Renewal duration or null",
    "submission_channel": "web_portal" | "pdf" | "hybrid",
    "form_version": "Form version or null",
    "official_source_url": "URL string or null",
    "source_verified_at": "ISO date string or null",
    "conflicts": []
  }
]
"""


def evaluate_with_gemini(state: dict, api_key: str = None) -> tuple[list[dict], str]:
    """Evaluate findings with Gemini under strict prompt hygiene."""
    key = api_key or find_api_key()
    if not key:
        raise ValueError("Gemini API key not found in environment or .env file.")

    models_to_try = [
        os.environ.get("GEMINI_COMPLIANCE_MODEL", "gemini-3.5-flash-lite"),
        "gemini-3.8-flash",
        "gemini-3.5-flash",
    ]

    user_prompt = f"""Goal: {state.get('goal')}
Domain: {state.get('domain')}

Applicant Profile (with effective values):
{json.dumps(state.get('applicant_profile', {}), indent=2)}

Overrides:
{json.dumps(state.get('overrides', {}), indent=2)}

Research Findings to Evaluate:
{json.dumps(state.get('research_findings', []), indent=2)}

Evaluate every research finding against the applicant profile. Return only the JSON array adhering to the schema.
"""

    last_error = None
    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"System Instructions:\n{COMPLIANCE_SYSTEM_PROMPT}\n\n{user_prompt}"}
                    ]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.1,
            },
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        for attempt in range(2):
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    candidates = data.get("candidates", [])
                    if candidates:
                        content_text = candidates[0]["content"]["parts"][0]["text"]
                        evaluated = json.loads(content_text)
                        if isinstance(evaluated, list):
                            return evaluated, "gemini_evaluated"
                        if isinstance(evaluated, dict) and "items" in evaluated:
                            return evaluated["items"], "gemini_evaluated"
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8", errors="replace")
                last_error = f"{model} HTTP {e.code}: {err_body}"
                if e.code in (429, 503):
                    time.sleep(2)
                    continue
                break
            except Exception as e:
                last_error = f"{model} error: {e}"
                time.sleep(1)
                continue

    raise RuntimeError(f"All Gemini compliance evaluation attempts failed. Last error: {last_error}")


def catalog_supporting_documents(matrix: list[dict], findings: list[dict]) -> list[dict]:
    """Catalog required attachments across all Required and Conditional permits."""
    doc_map = {}
    finding_dict = {f.get("id"): f for f in findings if f.get("id")}
    finding_by_name = {f.get("name"): f for f in findings if f.get("name")}

    # Standard document categories to normalize disparate raw names
    for row in matrix:
        if row.get("status") not in ("Required", "Conditional"):
            continue

        item_id = row.get("id")
        finding = finding_dict.get(item_id) or finding_by_name.get(row.get("name"), {})
        docs = finding.get("required_documents", [])

        if not docs:
            # Fallback standard proofs required for commercial/zoning/agri permits
            docs = ["Government Photo ID (Aadhaar / PAN / Voter ID)", "Proof of Premises Possession / Rent Agreement", "Recent Utility / Electricity Bill"]

        for d in docs:
            # Normalize doc name
            clean_name = d.strip()
            if re.search(r"photo|identity|id proof", clean_name, re.I):
                clean_name = "Government Photo ID (Aadhaar / PAN / Voter ID)"
            elif re.search(r"rent|tenancy|possession|lease|occupancy", clean_name, re.I):
                clean_name = "Rent Agreement or Landlord NOC"
            elif re.search(r"electric|utility|bill|tax receipt", clean_name, re.I):
                clean_name = "Recent Electricity Bill of Premises (<3 months)"

            if clean_name not in doc_map:
                doc_map[clean_name] = {
                    "name": clean_name,
                    "needed_for": [],
                    "precheck_status": "missing"
                }
            if item_id and item_id not in doc_map[clean_name]["needed_for"]:
                doc_map[clean_name]["needed_for"].append(item_id)

    return list(doc_map.values())


def compliance(state: dict) -> dict:
    """Core LangGraph node: evaluates compliance matrix, maintains audit trail, and generates open_questions."""
    findings = state.get("research_findings", [])
    if not findings:
        print("Warning: compliance called with empty research_findings.", file=sys.stderr)
        return state

    previous_matrix = {item["id"]: item for item in state.get("compliance_matrix", []) if "id" in item}

    evaluated_items, eval_mode = evaluate_with_gemini(state)
    today_iso = datetime.date.today().isoformat()

    new_matrix = []
    open_questions_set = set()

    for item in evaluated_items:
        item_id = item.get("id")
        new_status = item.get("status", "Conditional")
        rationale = item.get("rationale", "")
        depends_on = item.get("depends_on", []) or []

        finding_match = next((f for f in findings if f.get("id") == item_id or f.get("name") == item.get("name")), {})

        prev_entry = previous_matrix.get(item_id, {})
        history = list(prev_entry.get("history", []))

        prev_status = prev_entry.get("status")
        if prev_status and prev_status != new_status:
            transition_log = f"{today_iso}: {prev_status} -> {new_status} ({rationale[:80]})"
            history.append(transition_log)

        if new_status == "Conditional":
            for dep in depends_on:
                open_questions_set.add(dep)
        else:
            depends_on = []

        matrix_row = {
            "id": item_id or finding_match.get("id") or f"lic_{len(new_matrix)+1}",
            "name": item.get("name") or finding_match.get("name", "Requirement"),
            "authority": item.get("authority") or finding_match.get("authority", "Authority"),
            "tier": item.get("tier") or finding_match.get("tier", "state"),
            "status": new_status,
            "rationale": rationale,
            "depends_on": depends_on,
            "statutory_fee": item.get("statutory_fee") or finding_match.get("statutory_fee"),
            "renewal_period": item.get("renewal_period") or finding_match.get("renewal_period"),
            "submission_channel": item.get("submission_channel") or finding_match.get("submission_channel", "web_portal"),
            "form_version": item.get("form_version") or finding_match.get("form_version"),
            "official_source_url": item.get("official_source_url") or finding_match.get("official_source_url"),
            "source_verified_at": item.get("source_verified_at") or finding_match.get("source_verified_at"),
            "conflicts": item.get("conflicts") or finding_match.get("conflicts", []),
            "history": history,
        }
        new_matrix.append(matrix_row)

    # Update state
    state["compliance_matrix"] = new_matrix
    state["open_questions"] = sorted(list(open_questions_set))
    state["required_supporting_documents"] = catalog_supporting_documents(new_matrix, findings)

    if "workflow_flags" not in state:
        state["workflow_flags"] = {}
    state["workflow_flags"]["compliance_complete"] = True
    state["workflow_flags"]["compliance_needs_reeval"] = False
    state["workflow_flags"]["compliance_mode"] = eval_mode

    return state


def main():
    ap = argparse.ArgumentParser(description="Evaluate compliance matrix from state research findings.")
    ap.add_argument("state_file", help="Path to state.json")
    ap.add_argument("--out", help="Path to write updated state.json (defaults to overwriting input)")
    args = ap.parse_args()

    state = load_json(args.state_file)
    print(f"Evaluating compliance for {len(state.get('research_findings', []))} research findings...")
    updated_state = compliance(state)
    out_file = args.out or args.state_file
    save_json(out_file, updated_state)

    matrix = updated_state.get("compliance_matrix", [])
    open_q = updated_state.get("open_questions", [])
    docs = updated_state.get("required_supporting_documents", [])
    mode = updated_state.get("workflow_flags", {}).get("compliance_mode", "unknown")
    print(f"\nCompliance evaluation complete ({mode}). {len(matrix)} items classified.")
    print(f"Open profile questions blocking conditional rules: {len(open_q)}")
    for q in open_q:
        print(f"  ? {q}")
    print(f"Catalogued required supporting documents: {len(docs)}")
    for d in docs:
        print(f"  * {d['name']} (needed for: {', '.join(d['needed_for'])})")

    print("\nCompliance Matrix Summary:")
    for row in matrix:
        dep_info = f" [BLOCKED BY: {', '.join(row['depends_on'])}]" if row["depends_on"] else ""
        print(f" - [{row['tier'].upper()}] {row['name']} -> {row['status']}{dep_info}")
        print(f"   Rationale: {row['rationale']}")


if __name__ == "__main__":
    main()
