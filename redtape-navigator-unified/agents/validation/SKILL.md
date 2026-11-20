---
name: redtape-validation
description: Deterministic + semantic QA gate auditing schema integrity, government domains, 30-day freshness, Indian ID formats, cross-document consistency, and zero-hallucination compliance.
---

# Validation Agent

## Automated + Semantic Checks (`scripts/validate_state.py`)
1. **Source & Domain Gate:** Every `Required`/`Conditional`/`Not Applicable` row has an `official_source_url` from a verified government domain (`.gov.in`, `.nic.in`, `.gov`, `.org.in` for statutory bodies) and `source_verified_at` within 30 days (otherwise warning).
2. **Conflict & Dependency Integrity:** `Conditional` rows must declare `depends_on[]`; `Needs Verification` rows must explain `conflicts[]` or `note`.
3. **Format Validation:** PAN (`[A-Z]{5}[0-9]{4}[A-Z]`), 10-digit mobile (`[6-9][0-9]{9}`), 6-digit Indian PIN (`[1-9][0-9]{5}`), ISO dates.
4. **Cross-Document & Tier Consistency:**
   - Verify FSSAI tier matches `expected_annual_turnover_inr` (`<12L` Basic Form A, `12L–20Cr` State, `>20Cr` Central).
   - Verify applicant/business name and address are consistent across all generated `form_artifacts[]` and `portal_artifacts[]`.
5. **Completeness & Supporting Docs:** All `Required` items have supporting documents catalogued; all pending mandatory fields are surfaced to the user.

## Severity Policy
- `error`: Blocks Human Review (re-route to Interview or Document Agent).
- `warning`: Passes to Review Dashboard with explicit user callout.

## System Prompt
See `prompts/validation_system.md`.
