---
name: redtape-compliance
description: Legal-logic rule engine classifying each Research finding as Required, Conditional, Not Applicable, or Needs Verification with auditable thresholds and history tracking.
---

# Compliance Agent

## Classification Rules
- **`Required`**: Confirmed mandatory by an official source; all trigger conditions satisfied.
- **`Conditional`**: Depends on one or more `applicant_profile` paths still `null`. Populate `depends_on[]` with exact dotted paths (e.g., `applicant_profile.domain_attributes.expected_annual_turnover_inr`).
- **`Not Applicable`**: Source states an exemption/threshold that the user's profile clearly falls outside. Quote both threshold and user value in `rationale`.
- **`Needs Verification`**: No official source, conflicting sources (`conflicts[]`), or outdated/ambiguous criteria.

## Re-evaluation & Audit Trail
Whenever the Interview Agent updates any profile field, re-evaluate all `Conditional` rows. When a row changes status (e.g., `Conditional` → `Not Applicable`), append a human-readable entry to `history[]` (e.g., `"2026-11-20: Conditional -> Not Applicable (customer_seating=5, commercial_lpg=false)"`).

## System Prompt
See `prompts/compliance_system.md`.
