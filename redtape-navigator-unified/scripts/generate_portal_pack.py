#!/usr/bin/env python3
"""Generate a Digital Web Portal submission pack (human copy-paste sheet + Playwright draft-fill manifest).
Never auto-submits; always preserves explicit human gates (OTP, CAPTCHA, payment, final submit).
Usage: python3 generate_portal_pack.py portal_map.json state.json --out drafts/portal_pack.md [--manifest drafts/portal_manifest.json]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _common import PENDING, apply_transform, effective_value, is_blank, load_json, mask, save_json

SENSITIVE_KEYS = ("pan", "aadhaar", "bank", "account")


def build_portal_pack(portal_map, state):
    md = [
        f"# Portal Submission Pack: {portal_map['portal_name']}",
        "",
        f"- **Official Portal:** {portal_map['portal_url']}",
        "- **Mode:** Preparation & Draft-Fill Only (stops strictly before OTP / CAPTCHA / Payment / Submit)",
        "",
    ]
    manifest = {
        "portal_name": portal_map["portal_name"],
        "licence_id": portal_map.get("licence_id"),
        "portal_url": portal_map["portal_url"],
        "stop_before_gates": portal_map.get("human_gates", ["OTP", "CAPTCHA", "Payment", "Final Submit"]),
        "actions": [],
        "missing_fields": [],
    }
    filled_count, total_count = 0, 0
    for step in portal_map.get("steps", []):
        md += [f"## {step['step_name']}", "", "| Portal Field | Value to Enter | Status |", "|---|---|---|"]
        for f in step.get("fields", []):
            total_count += 1
            raw = effective_value(state, f["source"])
            if is_blank(raw):
                val_display = PENDING if f.get("mandatory") else "_(optional — leave blank)_"
                status = "PENDING (Required)" if f.get("mandatory") else "Optional Blank"
                if f.get("mandatory"):
                    manifest["missing_fields"].append(f["source"])
            else:
                filled_count += 1
                val = apply_transform(raw, f.get("transform"))
                is_sens = any(k in f["source"].lower() for k in SENSITIVE_KEYS)
                val_display = f"`{mask(val)}` _(masked in summary)_" if is_sens else f"`{val}`"
                status = "Ready"
                manifest["actions"].append({
                    "action": "fill",
                    "label": f["label"],
                    "selector": f.get("selector"),
                    "source": f["source"],
                    "value_masked": is_sens,
                    "value": None if is_sens else str(val),
                })
            md.append(f"| {f['label']} | {val_display} | {status} |")
        md.append("")

    if portal_map.get("uploads"):
        md += ["## Required Portal Uploads", ""]
        for u in portal_map["uploads"]:
            req = "Required" if u.get("mandatory") else "Optional"
            md.append(f"- [ ] **{u['label']}** ({u.get('accepted_formats', 'Check portal')}) — _{req}_")
        md.append("")

    md += ["## Human-Only Gates (Agent Stops Here)", ""]
    for g in manifest["stop_before_gates"]:
        md.append(f"- {g}")

    pct = round(100 * filled_count / total_count) if total_count else 0
    manifest["completion_percentage"] = pct
    return "\n".join(md) + "\n", manifest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("portal_map")
    ap.add_argument("state")
    ap.add_argument("--out", required=True)
    ap.add_argument("--manifest")
    a = ap.parse_args()
    md_text, manifest = build_portal_pack(load_json(a.portal_map), load_json(a.state))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(md_text)
    if a.manifest:
        os.makedirs(os.path.dirname(os.path.abspath(a.manifest)), exist_ok=True)
        save_json(a.manifest, manifest)
    print(f"{manifest['portal_name']}: {manifest['completion_percentage']}% ready, "
          f"{len(manifest['missing_fields'])} mandatory missing -> {a.out}")


if __name__ == "__main__":
    main()
