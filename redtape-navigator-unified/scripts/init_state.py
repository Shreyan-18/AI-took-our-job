#!/usr/bin/env python3
"""Initialize a fresh unified ProjectState from template.
Usage:
  python3 init_state.py --goal "open a bakery in Kolkata" [--llm] [--domain business|zoning|agriculture|general] [--lang en] --out state.json
"""
import argparse
import copy
import datetime
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _common import DOMAIN_DEFAULTS, load_json, save_json

TEMPLATE = os.path.join(os.path.dirname(__file__), "..", "assets", "state.template.json")


def make_state(goal, domain="business", lang="en", project_id=None, use_llm=False):
    st = load_json(TEMPLATE)
    now = datetime.datetime.now(datetime.timezone.utc)

    parsed = None
    if use_llm:
        try:
            from orchestrator_parser import parse_intent
            parsed = parse_intent(goal)
            if parsed:
                domain = parsed.get("domain", domain)
                lang = parsed.get("preferred_language", lang)
        except Exception as e:
            print(f"Warning: LLM goal parsing failed ({e}); falling back to template initialization.", file=sys.stderr)

    slug = re.sub(r"[^a-z0-9]+", "_", goal.lower()).strip("_")[:28] or "project"
    st["project_id"] = project_id or f"proj_{domain}_{slug}_{now:%Y%m%d%H%M}"
    st["goal"] = goal
    st["domain"] = domain if domain in DOMAIN_DEFAULTS else "general"
    st["preferred_language"] = lang
    st["created_at"] = now.isoformat(timespec="seconds")
    st["applicant_profile"]["domain_attributes"] = copy.deepcopy(DOMAIN_DEFAULTS[st["domain"]])

    if parsed:
        prof = st["applicant_profile"]
        if parsed.get("entity_name"):
            prof["entity_name"] = parsed["entity_name"]
        if parsed.get("activity_type"):
            prof["activity_type"] = parsed["activity_type"]

        # Applicant details
        if parsed.get("applicant"):
            for k in ("name", "phone", "email", "dob"):
                if parsed["applicant"].get(k):
                    prof["applicant"][k] = parsed["applicant"][k]

        # Location details
        if parsed.get("location"):
            for k in ("city_or_village", "district", "state", "municipal_ward_or_block", "address", "pin", "premises_type"):
                if parsed["location"].get(k):
                    prof["location"][k] = parsed["location"][k]

        # Domain attributes
        if parsed.get("domain_attributes"):
            for k, v in parsed["domain_attributes"].items():
                if v is not None and k in prof["domain_attributes"]:
                    prof["domain_attributes"][k] = v

        # Provenance mapping
        if parsed.get("provenance"):
            for k, phrase in parsed["provenance"].items():
                if phrase:
                    # Normalize path key to full state path if needed
                    full_key = k if k.startswith("applicant_profile.") else f"applicant_profile.{k}"
                    st["provenance"][full_key] = str(phrase)

    return st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goal", required=True)
    ap.add_argument("--domain", default="business", choices=["business", "zoning", "agriculture", "general"])
    ap.add_argument("--lang", default="en")
    ap.add_argument("--out", default="state.json")
    ap.add_argument("--project-id")
    ap.add_argument("--llm", action="store_true", help="Use Gemini Orchestrator Parser to extract facts & provenance")
    a = ap.parse_args()

    save_json(a.out, make_state(a.goal, a.domain, a.lang, a.project_id, use_llm=a.llm))
    print(f"Initialized {a.out} (domain={a.domain}, lang={a.lang}, llm={a.llm})")


if __name__ == "__main__":
    main()
