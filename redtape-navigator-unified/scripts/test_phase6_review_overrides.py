#!/usr/bin/env python3
"""Comprehensive Automated Verification Test for Phase 6:
Human Review Checkpoint, State Invariant Validation, & Dynamic Overrides Engine.
Tests:
1. State Invariant Validator:
   - Indian ID formats (valid PAN AAAAA9999A, invalid PAN rejected)
   - 10-digit Indian phone, 6-digit PIN
   - FSSAI statutory threshold enforcement (Basic <= 12L vs > 12L)
2. Dynamic Overrides Engine:
   - Overriding expected_annual_turnover_inr from 8 Lakh to 2.5 Crore
   - Compliance re-evaluation: FSSAI Basic transitions Required -> Not Applicable
   - Overriding customer_seating from 5 to 60
   - Compliance re-evaluation: Fire NOC transitions Not Applicable -> Required
   - History audit trail tracking: [prev_status -> new_status with timestamp]
3. Human Review Checkpoint (review.md):
   - All 6 sections rendered cleanly
   - Sensitive PII (PAN) masked on review summary
   - Audit trail and status change history accurately formatted
4. Document Re-Generation with Overrides:
   - Document engine reflects updated active permits
"""
import copy
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts"))

from _common import effective_value, load_json, mask, save_json
from compliance_engine import compliance as run_compliance
from document_engine import generate_documents
from render_review import render as render_review_md
from validate_state import validate as run_validate


def test_validator_rules():
    print("\n--- [Test 1] Testing Invariant Validator Rules ---")
    base_state = {
        "project_id": "test_val_001",
        "goal": "Open a bakery in Kolkata",
        "domain": "business",
        "preferred_language": "en",
        "applicant_profile": {
            "entity_name": "Test Bakery",
            "activity_type": "bakery",
            "applicant": {
                "name": "Test User",
                "pan": "ABCDE1234F",
                "phone": "9830012345",
                "email": "test@example.com",
            },
            "location": {
                "city_or_village": "Kolkata",
                "state": "West Bengal",
                "district": "Kolkata",
                "pin": "700017",
            },
            "domain_attributes": {
                "expected_annual_turnover_inr": 800000,
                "workers_on_site": 3,
                "customer_seating": 5,
            },
        },
        "compliance_matrix": [
            {
                "id": "lic_fssai_basic",
                "name": "FSSAI Basic Registration",
                "authority": "FSSAI",
                "tier": "central",
                "status": "Required",
                "rationale": "Turnover under 12L",
                "official_source_url": "https://foscos.fssai.gov.in",
                "source_verified_at": "2026-11-20",
            }
        ],
        "required_supporting_documents": [{"name": "Aadhaar Card"}],
        "open_questions": [],
        "overrides": {},
        "form_artifacts": [],
        "portal_artifacts": [],
    }

    # 1. Valid state passes
    v1 = run_validate(base_state)
    assert v1["passed"] is True, f"Expected valid state to pass, errors: {v1['errors']}"
    print("  [PASS] Valid base state passed validation.")

    # 2. Invalid PAN format rejected
    bad_pan_state = copy.deepcopy(base_state)
    bad_pan_state["applicant_profile"]["applicant"]["pan"] = "INVALID123"
    v2 = run_validate(bad_pan_state)
    assert v2["passed"] is False, "Expected invalid PAN to fail validation."
    assert any("pan" in e.lower() for e in v2["errors"]), "Expected PAN format error."
    print("  [PASS] Invalid PAN 'INVALID123' successfully rejected by validator.")

    # 3. Invalid PIN rejected
    bad_pin_state = copy.deepcopy(base_state)
    bad_pin_state["applicant_profile"]["location"]["pin"] = "7000"
    v3 = run_validate(bad_pin_state)
    assert v3["passed"] is False, "Expected 4-digit PIN to fail validation."
    assert any("pin" in e.lower() for e in v3["errors"]), "Expected PIN format error."
    print("  [PASS] Invalid PIN '7000' successfully rejected by validator.")

    # 4. FSSAI threshold check (Basic registration with turnover >= 12L)
    bad_fssai_state = copy.deepcopy(base_state)
    bad_fssai_state["applicant_profile"]["domain_attributes"]["expected_annual_turnover_inr"] = 2500000
    v4 = run_validate(bad_fssai_state)
    assert v4["passed"] is False, "Expected FSSAI turnover violation to fail validation."
    assert any("fssai" in e.lower() and "turnover" in e.lower() for e in v4["errors"]), "Expected FSSAI turnover error."
    print("  [PASS] FSSAI Basic with turnover ₹25 Lakhs successfully flagged as statutory violation.")


def test_dynamic_overrides_and_audit_trail():
    print("\n--- [Test 2] Testing Dynamic Overrides & Audit Trail Re-Evaluation ---")
    snap_path = ROOT_DIR / "examples" / "bakery_kolkata" / "state_snapshot.json"
    state = load_json(snap_path)

    # Initial state verification
    fssai_initial = next((r for r in state["compliance_matrix"] if "fssai" in r["id"].lower()), None)
    assert fssai_initial is not None
    assert fssai_initial["status"] == "Required", f"Expected initial FSSAI status Required, got {fssai_initial['status']}"
    print(f"  [Initial] FSSAI status: {fssai_initial['status']} (Turnover: 800,000)")

    # 1. Apply user override: annual turnover 2.5 Crore (25,000,000)
    print("\n  Applying User Override: expected_annual_turnover_inr = ₹2.5 Crore...")
    state["overrides"]["applicant_profile.domain_attributes.expected_annual_turnover_inr"] = 25000000
    state["overrides"]["applicant_profile.applicant.pan"] = "ABCDE1234F"

    # Re-evaluate compliance with override
    re_evaluated = run_compliance(state)

    fssai_after = next((r for r in re_evaluated["compliance_matrix"] if "fssai" in r["id"].lower()), None)
    assert fssai_after is not None
    assert fssai_after["status"] == "Not Applicable", f"Expected FSSAI Basic to become 'Not Applicable', got {fssai_after['status']}"
    print(f"  [Override Result] FSSAI status dynamically transitioned to: {fssai_after['status']}")
    print(f"  [Rationale] {fssai_after['rationale']}")

    # Verify history audit trail
    assert len(fssai_after.get("history", [])) > 0, "Expected status change logged in history[]"
    latest_hist = fssai_after["history"][-1]
    print(f"  [Audit Trail Recorded] {latest_hist}")
    assert "Required -> Not Applicable" in latest_hist

    # 2. Apply user override: customer seating = 65 (Triggering Fire NOC)
    print("\n  Applying User Override: customer_seating = 65 stools...")
    state["overrides"]["applicant_profile.domain_attributes.customer_seating"] = 65
    re_evaluated2 = run_compliance(state)

    fire_after = next((r for r in re_evaluated2["compliance_matrix"] if "fire" in r["id"].lower()), None)
    assert fire_after is not None
    assert fire_after["status"] == "Required", f"Expected Fire NOC to become 'Required', got {fire_after['status']}"
    print(f"  [Override Result] Fire NOC status dynamically transitioned to: {fire_after['status']}")
    print(f"  [Rationale] {fire_after['rationale']}")
    assert len(fire_after.get("history", [])) > 0, "Expected Fire NOC status change logged in history[]"
    print(f"  [Audit Trail Recorded] {fire_after['history'][-1]}")

    return re_evaluated2


def test_review_markdown_rendering(state):
    print("\n--- [Test 3] Testing Human Review Package Rendering (review.md) ---")
    draft_dir = ROOT_DIR / "drafts" / "test_phase6_review"
    draft_dir.mkdir(parents=True, exist_ok=True)

    # Re-generate documents with overrides active
    doc_state = generate_documents(state, output_dir=str(draft_dir))

    # Render review markdown
    review_text = render_review_md(doc_state)
    review_file = draft_dir / "review.md"
    review_file.write_text(review_text, encoding="utf-8")
    print(f"  [Generated] Human Review Checkpoint -> {review_file}")

    # Check the 6 standardized sections
    sections = [
        "## 1. Compliance Matrix",
        "## 2. Audit Trail & Rule Reasoning",
        "## 3. Conflicts & System Notices",
        "## 4. Filled PDF Drafts & Digital Portal Packs",
        "## 5. Supporting Document Checklist",
        "## 6. Submission Readiness",
    ]
    for sec in sections:
        assert sec in review_text, f"Missing required review section: {sec}"
        print(f"  [PASS] Found section: {sec}")

    # Check sensitive PII masking
    assert "Sensitive IDs masked on summary — PAN on file: `******234F`" in review_text or "ABCDE1234F" not in review_text
    print("  [PASS] Sensitive PAN masked on review summary.")

    # Check audit trail history is rendered
    assert "status change:" in review_text
    print("  [PASS] Status transitions reflected in review audit trail.")

    # Validate resulting state
    v_res = run_validate(doc_state)
    print(f"  [Validation Status] Passed: {v_res['passed']}")
    print(f"  Errors: {len(v_res['errors'])}, Warnings: {len(v_res['warnings'])}")
    assert v_res["passed"] is True, f"Expected state with valid overrides to pass validation, got errors: {v_res['errors']}"
    print("  [PASS] State invariant validation passed with zero blockers.")


def main():
    print("=====================================================================")
    print("PHASE 6 TEST SUITE: HUMAN REVIEW, INVARIANTS & DYNAMIC OVERRIDES")
    print("=====================================================================")
    test_validator_rules()
    updated_state = test_dynamic_overrides_and_audit_trail()
    test_review_markdown_rendering(updated_state)
    print("\n=====================================================================")
    print("ALL PHASE 6 VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("=====================================================================")


if __name__ == "__main__":
    main()
