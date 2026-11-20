#!/usr/bin/env python3
"""Orchestrator parser module for RedTape Navigator.
Uses Gemini to extract domain, location, pre-stated profile attributes,
and exact provenance phrases from a citizen's natural language goal.
Enforces zero fabrication: unmentioned fields remain null.
"""
import copy
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from _common import DOMAIN_DEFAULTS, load_json

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


def find_api_key():
    """Look for GEMINI_API_KEY or GOOGLE_API_KEY in environment or .env files."""
    for key_name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        val = os.environ.get(key_name)
        if val:
            return val

    for env_path in [ROOT_DIR / ".env", ROOT_DIR / "redtape-navigator-unified" / ".env"]:
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if k in ("GEMINI_API_KEY", "GOOGLE_API_KEY") and v:
                        return v
    return None


SYSTEM_PROMPT = """You are the RedTape Navigator Orchestrator Parser.
Your job is to parse a citizen or small-business owner's bureaucratic goal into structured data.

Rules:
1. Strict Zero Fabrication: Only extract facts explicitly stated or directly implied in the user's text.
   If something is not stated (e.g. PAN, Aadhaar, turnover, exact address, PIN), set it to null. NEVER invent values.
2. Domain Classification: Must be one of:
   - "business": commercial licenses, shops, food stalls, bakeries, cafes, trading, manufacturing, FSSAI, trade license
   - "zoning": building plan sanction, residential additions, floors, setbacks, FAR, land use conversion, municipal building permits
   - "agriculture": farming grants, solar pump subsidy, drip irrigation, crop loans, Kisan credit, PM-KISAN, PM-FME
   - "general": if unclear
3. Provenance: For EVERY extracted non-null field, you MUST record the exact verbatim phrase or substring from the user's input that provided this fact.
4. Preferred Language: Detect the language of the prompt ("en", "hi", "bn", etc.).

Return a clean JSON object with this exact structure:
{
  "domain": "business" | "zoning" | "agriculture" | "general",
  "preferred_language": "en",
  "entity_name": string or null,
  "activity_type": string or null,
  "applicant": {
    "name": string or null,
    "phone": string or null,
    "email": string or null,
    "dob": string or null
  },
  "location": {
    "city_or_village": string or null,
    "district": string or null,
    "state": string or null,
    "municipal_ward_or_block": string or null,
    "address": string or null,
    "pin": string or null,
    "premises_type": "rented" | "owned" | null
  },
  "domain_attributes": {
    "food_prepared_on_site": boolean or null,
    "customer_seating": integer or null,
    "commercial_lpg": boolean or null,
    "expected_annual_turnover_inr": integer or null,
    "workers_on_site": integer or null,
    "food_categories": list of strings or null,
    "plot_area_sqft": number or null,
    "proposed_floors": integer or null,
    "current_land_use": string or null,
    "proposed_land_use": string or null,
    "road_width_ft": number or null,
    "heritage_or_eco_zone": boolean or null,
    "landholding_acres": number or null,
    "crop_types": list of strings or null,
    "irrigation_source": string or null,
    "kisan_credit_card": boolean or null,
    "farmer_category": string or null,
    "bank_account_linked_aadhaar": boolean or null
  },
  "provenance": {
    // map dotted path (e.g. "applicant_profile.location.city_or_village") to exact user phrase
  }
}
"""


def parse_intent(goal_text: str, api_key: str = None) -> dict:
    """Invoke Gemini with retries to parse goal text into domain, profile attributes, and provenance."""
    key = api_key or find_api_key()
    if not key:
        raise ValueError("Gemini API key not found in environment or .env file.")

    model = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"System Instructions:\n{SYSTEM_PROMPT}\n\nUser Goal:\n{goal_text}"}
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

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            candidates = data.get("candidates", [])
            if candidates:
                content_text = candidates[0]["content"]["parts"][0]["text"]
                result = json.loads(content_text)
                dom = result.get("domain", "general")
                if dom not in DOMAIN_DEFAULTS:
                    dom = "general"
                result["domain"] = dom
                if "applicant_profile" not in result:
                    result["applicant_profile"] = {
                        "entity_name": result.get("entity_name"),
                        "activity_type": result.get("activity_type"),
                        "applicant": result.get("applicant", {}),
                        "location": result.get("location", {}),
                        "domain_attributes": result.get("domain_attributes", {}),
                    }
                return result
    except Exception as e:
        print(f"Notice: Gemini orchestrator unavailable ({e}); falling back to heuristic goal parser.", file=sys.stderr)

    # Heuristic fallback for zero-downtime demo protection
    dom = "general"
    g_lower = goal_text.lower()
    if any(k in g_lower for k in ("bakery", "cafe", "restaurant", "food", "shop", "business", "store")):
        dom = "business"
    elif any(k in g_lower for k in ("floor", "extension", "roof", "residential", "zoning", "building")):
        dom = "zoning"
    elif any(k in g_lower for k in ("irrigation", "grant", "farm", "crop", "agriculture", "farmer")):
        dom = "agriculture"

    city = "Kolkata" if "kolkata" in g_lower else None
    ward = "Park Circus" if "park circus" in g_lower else None

    profile = {
        "entity_name": None,
        "activity_type": "bakery" if "bakery" in g_lower else dom,
        "applicant": {
            "name": None, "pan": None, "aadhaar_last4": None,
            "phone": None, "email": None, "dob": None
        },
        "location": {
            "city_or_village": city,
            "district": None,
            "state": "West Bengal" if city == "Kolkata" else None,
            "municipal_ward_or_block": ward,
            "address": None,
            "pin": None,
            "premises_type": None
        },
        "domain_attributes": copy.deepcopy(DOMAIN_DEFAULTS.get(dom, DOMAIN_DEFAULTS["general"]))
    }
    if ward:
        profile["location"]["municipal_ward_or_block"] = ward

    seating_match = re.search(r"(\d+)\s*(?:counter\s+seats?|seats?|chairs?)", g_lower)
    if seating_match:
        cnt = int(seating_match.group(1))
        profile.setdefault("domain_attributes", {})["customer_seating"] = cnt

    provenance = {}
    if city:
        provenance["applicant_profile.location.city_or_village"] = city
    if ward:
        provenance["applicant_profile.location.municipal_ward_or_block"] = ward
    if seating_match:
        provenance["applicant_profile.domain_attributes.customer_seating"] = seating_match.group(0)

    return {
        "domain": dom,
        "applicant_profile": profile,
        "provenance": provenance,
        "raw_goal": goal_text,
    }


def main():
    import argparse

    ap = argparse.ArgumentParser(description="Parse citizen goal into structured domain and profile.")
    ap.add_argument("goal", help="Natural language bureaucratic goal")
    ap.add_argument("--json", action="store_true", help="Print result as indented JSON")
    args = ap.parse_args()

    parsed = parse_intent(args.goal)
    if args.json:
        print(json.dumps(parsed, indent=2, ensure_ascii=False))
    else:
        print(f"Domain: {parsed.get('domain')}")
        print(f"Location: {parsed.get('location')}")
        print(f"Provenance items: {len(parsed.get('provenance', {}))}")


if __name__ == "__main__":
    main()
