#!/usr/bin/env python3
"""Render the 6-part Human Review Checkpoint (markdown) from unified state.json.
Usage: python3 render_review.py state.json --out review.md
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _common import effective_value, is_blank, load_json, mask
from validate_state import validate

ORDER = {"Required": 0, "Conditional": 1, "Needs Verification": 2, "Not Applicable": 3}


def render(state):
    ap = state.get("applicant_profile", {})
    res = validate(state)
    city = effective_value(state, "applicant_profile.location.city_or_village") or "Unknown"
    st_name = effective_value(state, "applicant_profile.location.state") or "Unknown"
    title = ap.get("entity_name") or state.get("goal")

    L = [
        f"# Application Review Package: {title}",
        "",
        f"- **Goal:** {state.get('goal', '')}",
        f"- **Domain:** `{state.get('domain', 'general')}` | **Location:** {city}, {st_name}",
        "",
        "> **Preparation Aid Only:** Verify all fees, rules, and form versions with the issuing authority before paying or submitting. This assistant never submits on your behalf.",
        "",
    ]

    if state.get("workflow_flags", {}).get("source_fallback"):
        L += ["> **Snapshot Warning:** One or more live government portals were unreachable; unverified fallback leads were used. Verify all `NOT VERIFIED` items below before paying fees.", ""]

    rows = sorted(state.get("compliance_matrix", []), key=lambda r: ORDER.get(r.get("status"), 9))
    L += ["## 1. Compliance Matrix", "", "| Requirement | Tier | Authority | Status | Channel | Fee | Source | Verified |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        src = r.get("official_source_url") or "none"
        ver = r.get("source_verified_at") or "NOT VERIFIED"
        L.append(f"| {r.get('name')} | {r.get('tier', '-')} | {r.get('authority', '')} | **{r.get('status')}** | {r.get('submission_channel', 'pdf')} | {r.get('statutory_fee', '-')} | {src} | {ver} |")

    L += ["", "## 2. Audit Trail & Rule Reasoning", ""]
    for r in rows:
        L.append(f"- **{r.get('name')}** (`{r.get('status')}`): {r.get('rationale', '')}")
        for h in r.get("history", []):
            L.append(f"  - status change: {h}")
        if r.get("depends_on") and r.get("status") == "Conditional":
            L.append(f"  - waiting on: `{', '.join(r['depends_on'])}`")

    conflicts = [(r.get("name"), r.get("conflicts", [])) for r in rows if r.get("conflicts")]
    if conflicts or state.get("errors"):
        L += ["", "## 3. Conflicts & System Notices", ""]
        for name, c_list in conflicts:
            L.append(f"- **{name}** (conflicting official sources):")
            for c in c_list:
                L.append(f"  - {c}")
        for err in state.get("errors", []):
            L.append(f"- _Agent notice:_ {err}")
    else:
        L += ["", "## 3. Conflicts & System Notices", "", "_No unresolved regulatory conflicts or system errors recorded._"]

    L += ["", "## 4. Filled PDF Drafts & Digital Portal Packs", ""]
    for fa in state.get("form_artifacts", []):
        L.append(f"- **PDF Draft — {fa.get('form_name')}**: {fa.get('completion_percentage', '?')}% complete (`{fa.get('status')}`) → `{fa.get('file_path')}`")
        for m in fa.get("missing_fields", []) or []:
            L.append(f"  - needs your input: `{m}`")
    for pa in state.get("portal_artifacts", []):
        L.append(f"- **Web Portal Pack — {pa.get('portal_name')}**: {pa.get('completion_percentage', '?')}% ready (`{pa.get('status')}`) → `{pa.get('copy_sheet_path')}` ({pa.get('portal_url')})")
        for m in pa.get("missing_fields", []) or []:
            L.append(f"  - needs your input: `{m}`")
    if not state.get("form_artifacts") and not state.get("portal_artifacts"):
        L.append("_No PDF drafts or portal packs generated yet._")

    L += ["", "## 5. Supporting Document Checklist", ""]
    for d in state.get("required_supporting_documents", []):
        if isinstance(d, dict):
            needed = f" _(for: {', '.join(d['needed_for'])})_" if d.get("needed_for") else ""
            status = f" [{d['precheck_status']}]" if d.get("precheck_status") else ""
            L.append(f"- [ ] {d.get('name')}{needed}{status}")
        else:
            L.append(f"- [ ] {d}")

    L += ["", "## 6. Submission Readiness", ""]
    ready = res["passed"] and not any(("pending" in w.lower() or "unresolved" in w.lower()) for w in res["warnings"])
    L.append("**Ready for your final review, signature, and submission.**" if ready else "**Action needed before submission.** Resolve the items below:")
    for e in res["errors"]:
        L.append(f"- **Blocker:** {e}")
    for w in res["warnings"]:
        L.append(f"- **Note:** {w}")

    pan = effective_value(state, "applicant_profile.applicant.pan")
    if not is_blank(pan):
        L += ["", f"_Sensitive IDs masked on summary — PAN on file: `{mask(pan)}`_"]
    L += ["", "_To correct any field, add it to `state.overrides` and re-run Document + Review._"]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("state")
    ap.add_argument("--out", default="review.md")
    a = ap.parse_args()
    out = render(load_json(a.state))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"Wrote {a.out}")


if __name__ == "__main__":
    main()
