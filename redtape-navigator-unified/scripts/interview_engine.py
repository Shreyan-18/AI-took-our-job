#!/usr/bin/env python3
"""Interactive Multilingual Interview Engine for RedTape Navigator.
Implements:
1. Impact-driven ranking of open_questions based on compliance blockers.
2. PII deferral (withholding PAN/Aadhaar until necessary).
3. Plain-language question generation in the user's preferred language.
4. Typed slot-filling with Indian unit normalization (lakhs/crores/bighas/dates) and provenance.
Compatible with LangGraph state dict and interactive CLI.
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
from _common import effective_value, is_blank, load_json, save_json
from orchestrator_parser import find_api_key

INTERVIEW_QUESTION_PROMPT = """You are the RedTape Navigator Interview Agent.
You are helping a citizen or small-business owner navigate bureaucracy with warmth, clarity, and zero administrative jargon.

Your Task:
Ask at most 2 to 3 related, conversational questions to gather information for the targeted fields.
User's Preferred Language: {language}

Rules:
1. Speak plainly and warmly. Do NOT quote legal statutes, section numbers, or acronyms like FoSCoS/PCB.
2. Explain briefly in one simple sentence WHY this fact matters (e.g., "To see if you qualify for the basic ₹100 food registration rather than a state license...").
3. Ask about tangible lived realities (e.g. ask "What do you anticipate your annual sales or turnover might be?" rather than "State expected annual turnover under Rule 82").
4. If asking multiple items, number them clearly.

Targeted Fields to Gather:
{fields_info}

Return only the natural language question text to display to the citizen.
"""

INTERVIEW_PARSER_PROMPT = """You are the RedTape Navigator Interview Parser.
Your job is to parse the citizen's free-form conversational response into typed values for the targeted profile fields.

Targeted Fields:
{targeted_fields}

Citizen's Response:
\"{user_response}\"

Rules:
1. Strict Provenance: For EVERY extracted non-null field, you MUST record the exact verbatim substring from the citizen's response that provided this fact.
2. Indian Unit & Currency Normalization:
   - Convert Indian currency representations into pure integer INR:
     * "8 lakh" or "8L" or "800000" -> 800000
     * "1.5 crore" or "1.5Cr" -> 15000000
     * "50 thousand" -> 50000
   - Convert dates into ISO format (YYYY-MM-DD).
   - Convert colloquial answers into clean booleans (e.g. "no gas, only electric" for commercial_lpg -> false; "we have 5 stools" for customer_seating -> 5).
3. Zero Fabrication: If the user did not answer or skipped a field, return null for that field.

Return a JSON object with this schema:
{{
  "extracted": {{
    // mapping of dotted path to typed value (or null)
  }},
  "provenance": {{
    // mapping of dotted path to exact substring from citizen response
  }},
  "confirmation_summary": "One polite sentence summarizing what was captured (e.g., 'Got it, an annual turnover around ₹8 Lakhs with no commercial gas cylinders.')"
}}
"""


def set_path(data: dict, dotted: str, value):
    """Sets a value in a nested dictionary using a dotted path."""
    parts = dotted.split(".")
    cur = data
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value


def is_pii_field(field_path: str) -> bool:
    """Check if a field is sensitive personal identification."""
    pii_markers = ("pan", "aadhaar", "bank_account", "dob")
    return any(m in field_path.lower() for m in pii_markers)


def rank_open_questions(state: dict) -> list[str]:
    """Rank open questions by how many Conditional rules they unblock, deferring sensitive PII."""
    matrix = state.get("compliance_matrix", [])
    open_q = set(state.get("open_questions", []))

    # Also add mandatory profile blanks if missing
    for core_field in ("applicant_profile.location.city_or_village", "applicant_profile.activity_type"):
        if is_blank(effective_value(state, core_field)):
            open_q.add(core_field)

    # Count how many conditional rules depend on each field
    impact_score = {}
    for q in open_q:
        # Skip if already populated and not blank
        if not is_blank(effective_value(state, q)):
            continue

        score = 0
        for row in matrix:
            if row.get("status") == "Conditional" and q in row.get("depends_on", []):
                score += 10  # High priority: directly unblocks statutory status

        # PII penalty: defer sensitive ID fields unless nothing else remains
        if is_pii_field(q):
            score -= 100

        impact_score[q] = score

    # Sort descending by impact score
    ranked = sorted(impact_score.keys(), key=lambda k: impact_score[k], reverse=True)
    return ranked


def call_gemini_interview(prompt_text: str, api_key: str = None, json_mode: bool = False):
    """Invoke Gemini for interview generation or parsing."""
    key = api_key or find_api_key()
    if not key:
        raise ValueError("Gemini API key not found in environment or .env file.")

    model = os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    config = {"temperature": 0.2}
    if json_mode:
        config["responseMimeType"] = "application/json"

    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": config,
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
            cand = data.get("candidates", [])
            if cand:
                txt = cand[0]["content"]["parts"][0]["text"].strip()
                return json.loads(txt) if json_mode else txt
    except Exception as e:
        print(f"Notice: Gemini interview call unavailable ({e}); activating fallback.", file=sys.stderr)

    return None


def generate_fallback_question(target_fields: list[str]) -> str:
    """Deterministic plain-language question template when LLM generation is unavailable."""
    field_templates = {
        "applicant_profile.domain_attributes.workers_on_site": "Roughly how many people do you expect will be working on site day-to-day? (This helps check workplace registration rules.)",
        "applicant_profile.domain_attributes.expected_annual_turnover_inr": "What do you anticipate your annual turnover or sales might be in a typical year? (This determines whether you qualify for simple ₹100 basic registration.)",
        "applicant_profile.location.premises_type": "Is the commercial premises rented, leased, or owned by you?",
        "applicant_profile.location.address": "What is the full street address or location of your premises?",
        "applicant_profile.entity_name": "What will be the name of your commercial enterprise or shop?",
        "applicant_profile.applicant.name": "What is the full legal name of the applicant / business owner?",
        "applicant_profile.applicant.phone": "What is your contact mobile phone number?",
    }
    lines = ["Hello! To help get your regulatory paperwork and permits sorted, I just have a couple of quick questions:"]
    for i, f in enumerate(target_fields, 1):
        q_text = field_templates.get(f, f"Could you provide your details for {f.split('.')[-1].replace('_', ' ')}?")
        lines.append(f"\n{i}. {q_text}")
    lines.append("\nWhenever you're ready, just let me know!")
    return "\n".join(lines)


def parse_fallback_answer(user_text: str, fields_targeted: list[str]) -> dict:
    """Deterministic regex slot-filling and provenance extraction when LLM parser is unavailable."""
    extracted = {}
    provenance = {}

    text_lower = user_text.lower()
    # Check targeted fields plus standard candidate profile fields if user volunteered info
    candidates = list(fields_targeted) + [
        "applicant_profile.domain_attributes.expected_annual_turnover_inr",
        "applicant_profile.domain_attributes.workers_on_site",
        "applicant_profile.location.premises_type",
        "applicant_profile.domain_attributes.floor_area_sq_ft",
        "applicant_profile.domain_attributes.uses_commercial_lpg",
        "applicant_profile.domain_attributes.customer_seating",
    ]

    for f in candidates:
        leaf = f.split(".")[-1]
        if "turnover" in leaf:
            # Match 8 lakh / 800000 / 1.5 crore
            m_lakh = re.search(r"(\d+(?:\.\d+)?)\s*(?:lakhs?|l)\b", text_lower)
            m_cr = re.search(r"(\d+(?:\.\d+)?)\s*(?:crores?|cr)\b", text_lower)
            m_num = re.search(r"\b(\d{5,9})\b", text_lower)
            if m_lakh:
                val = int(float(m_lakh.group(1)) * 100000)
                extracted[f] = val
                provenance[f] = m_lakh.group(0)
            elif m_cr:
                val = int(float(m_cr.group(1)) * 10000000)
                extracted[f] = val
                provenance[f] = m_cr.group(0)
            elif m_num:
                val = int(m_num.group(1))
                extracted[f] = val
                provenance[f] = m_num.group(0)

        elif "worker" in leaf:
            m_w = re.search(r"\b(\d+)\s*(?:workers?|staff|people|persons?|employees?)\b", text_lower)
            if m_w and int(m_w.group(1)) < 500:
                extracted[f] = int(m_w.group(1))
                provenance[f] = m_w.group(0)

        elif "premises_type" in leaf or "tenancy" in leaf:
            if re.search(r"\b(rent|rented|lease|leased|tenan)\b", text_lower):
                extracted[f] = "rented"
                provenance[f] = "rented"
            elif re.search(r"\b(own|owned|ownership)\b", text_lower):
                extracted[f] = "owned"
                provenance[f] = "owned"

        elif "floor" in leaf or "area" in leaf:
            m_a = re.search(r"\b(\d+)\s*(?:sq\s*ft|square\s*feet|sqft)\b", text_lower)
            if m_a:
                extracted[f] = int(m_a.group(1))
                provenance[f] = m_a.group(0)

        elif "lpg" in leaf or "gas" in leaf:
            if re.search(r"\bno\s+(?:commercial\s+)?(?:lpg|gas)\b", text_lower) or "electric" in text_lower:
                extracted[f] = False
                provenance[f] = "no commercial gas" if "no" in text_lower else "electric"
            elif re.search(r"\b(?:uses?|commercial|cylinder)\s+(?:lpg|gas)\b", text_lower):
                extracted[f] = True
                provenance[f] = "commercial gas"

        elif "seating" in leaf:
            m_s = re.search(r"\b(\d+)\s*(?:seats?|chairs?|counter\s+seats?|stools?)\b", text_lower)
            if m_s:
                extracted[f] = int(m_s.group(1))
                provenance[f] = m_s.group(0)

    summary_parts = []
    if any("turnover" in k for k in extracted):
        t_val = next(v for k, v in extracted.items() if "turnover" in k)
        summary_parts.append(f"an expected annual turnover of ₹{t_val:,}")
    if any("worker" in k for k in extracted):
        w_val = next(v for k, v in extracted.items() if "worker" in k)
        summary_parts.append(f"{w_val} workers on site")

    summary = f"Got it, captured {' with '.join(summary_parts)}." if summary_parts else "Thank you for the information."

    return {
        "extracted": extracted,
        "provenance": provenance,
        "confirmation_summary": summary,
    }


def generate_question_batch(state: dict) -> dict:
    """Generate the next targeted question turn (at most 3 related fields)."""
    ranked_fields = rank_open_questions(state)
    rounds = state.get("workflow_flags", {}).get("interview_rounds", 0)

    # Check termination condition: no questions or reached 4 rounds cap
    if not ranked_fields or rounds >= 4:
        state.setdefault("workflow_flags", {})["interview_complete"] = True
        return {
            "complete": True,
            "round": rounds,
            "fields_targeted": [],
            "question": "All required information has been gathered. Ready for document generation."
        }

    # Take top 1 to 3 fields for this turn
    target_fields = ranked_fields[:3]
    lang = state.get("preferred_language", "en")

    fields_info = "\n".join([f"- {f}" for f in target_fields])
    prompt = INTERVIEW_QUESTION_PROMPT.format(language=lang, fields_info=fields_info)

    question_text = call_gemini_interview(prompt, json_mode=False)
    if not question_text:
        question_text = generate_fallback_question(target_fields)
        state.setdefault("workflow_flags", {})["interview_question_mode"] = "template_fallback"
        notice = "Notice: Live Gemini interview question generator was unavailable; used deterministic question template."
        if notice not in state.setdefault("errors", []):
            state["errors"].append(notice)

    return {
        "complete": False,
        "round": rounds + 1,
        "fields_targeted": target_fields,
        "question": question_text
    }


def process_user_answer(state: dict, user_text: str, fields_targeted: list[str]) -> dict:
    """Parse user's conversational response into typed profile metrics and provenance."""
    prompt = INTERVIEW_PARSER_PROMPT.format(
        targeted_fields=json.dumps(fields_targeted),
        user_response=user_text
    )

    parsed = call_gemini_interview(prompt, json_mode=True)
    if not parsed:
        parsed = parse_fallback_answer(user_text, fields_targeted)
        state.setdefault("workflow_flags", {})["interview_parser_mode"] = "regex_fallback"
        notice = "Notice: Live Gemini interview parser was unavailable; parsed via deterministic regex slot-filler."
        if notice not in state.setdefault("errors", []):
            state["errors"].append(notice)

    extracted = parsed.get("extracted", {})
    provenance = parsed.get("provenance", {})
    summary = parsed.get("confirmation_summary", "")

    # Create mapping of possible keys (full dotted path and leaf name) to canonical dotted path
    canonical_map = {f: f for f in fields_targeted}
    for f in fields_targeted:
        leaf = f.split(".")[-1]
        canonical_map[leaf] = f
    for f in (
        "applicant_profile.domain_attributes.expected_annual_turnover_inr",
        "applicant_profile.domain_attributes.workers_on_site",
        "applicant_profile.location.premises_type",
        "applicant_profile.domain_attributes.floor_area_sq_ft",
        "applicant_profile.domain_attributes.uses_commercial_lpg",
        "applicant_profile.domain_attributes.customer_seating",
    ):
        canonical_map[f] = f
        canonical_map[f.split(".")[-1]] = f

    # Inject extracted values into state profile
    resolved_extracted = {}
    resolved_provenance = {}

    for k, val in extracted.items():
        if val is None:
            continue
        canon_path = canonical_map.get(k, k)
        # Type coercion for known integer fields
        if any(term in canon_path for term in ("turnover", "seating", "workers", "pin")):
            try:
                if isinstance(val, str):
                    clean_num = re.sub(r"[^\d]", "", val)
                    if clean_num:
                        val = int(clean_num)
                elif isinstance(val, (int, float)):
                    val = int(val)
            except Exception:
                pass
        # Normalize boolean strings if needed
        if isinstance(val, str):
            if val.lower() in ("true", "yes", "y"):
                val = True
            elif val.lower() in ("false", "no", "n"):
                val = False

        set_path(state, canon_path, val)
        resolved_extracted[canon_path] = val
        if canon_path in state.get("open_questions", []):
            state["open_questions"].remove(canon_path)

    # Inject provenance
    for k, phrase in provenance.items():
        if phrase:
            canon_path = canonical_map.get(k, k)
            state.setdefault("provenance", {})[canon_path] = str(phrase)
            resolved_provenance[canon_path] = str(phrase)

    # Update workflow flags
    flags = state.setdefault("workflow_flags", {})
    flags["interview_rounds"] = flags.get("interview_rounds", 0) + 1
    flags["compliance_needs_reeval"] = True  # Signal that Compliance should re-evaluate

    # Check if more questions remain
    remaining = rank_open_questions(state)
    state["open_questions"] = remaining
    flags["interview_complete"] = bool(not remaining or flags.get("interview_rounds", 0) >= 4)

    return {
        "extracted": resolved_extracted,
        "provenance": resolved_provenance,
        "confirmation_summary": summary,
        "open_questions_remaining": len(remaining),
        "interview_complete": flags["interview_complete"]
    }


def interview_turn(state: dict, user_answer: str = None) -> tuple[dict, dict]:
    """Single turn helper for interactive loops or LangGraph node execution."""
    # 1. If an answer was supplied, parse it first
    turn_result = {}
    if user_answer:
        # Determine what was targeted: rank open questions
        active_targets = rank_open_questions(state)[:3]
        turn_result = process_user_answer(state, user_answer, active_targets)

    # 2. Generate next question or completion
    next_q = generate_question_batch(state)
    turn_result["next_turn"] = next_q
    return state, turn_result


def main():
    ap = argparse.ArgumentParser(description="Interview Agent CLI for RedTape Navigator.")
    ap.add_argument("state_file", help="Path to state.json")
    ap.add_argument("--answer", help="Citizen's conversational answer text")
    ap.add_argument("--interactive", action="store_true", help="Run interactive terminal Q&A loop")
    ap.add_argument("--out", help="Path to write updated state.json (defaults to overwriting input)")
    args = ap.parse_args()

    state = load_json(args.state_file)
    out_file = args.out or args.state_file

    if args.interactive:
        print(f"\n--- RedTape Navigator: Interactive Citizen Interview ---")
        print(f"Goal: {state.get('goal')} | Language: {state.get('preferred_language')}")
        while not state.get("workflow_flags", {}).get("interview_complete"):
            batch = generate_question_batch(state)
            if batch["complete"]:
                print(f"\n[Interview Complete]: {batch['question']}")
                break

            print(f"\n[Agent - Round {batch['round']}]:\n{batch['question']}\n")
            user_input = input("You: ").strip()
            if not user_input:
                print("Skipping...")
                break

            res = process_user_answer(state, user_input, batch["fields_targeted"])
            print(f"\n[Agent Confirmation]: {res.get('confirmation_summary')}")
            print(f"Extracted: {json.dumps(res.get('extracted'))}")
            save_json(out_file, state)

        save_json(out_file, state)
        print(f"\nSaved updated state to {out_file}.")
        return

    # Non-interactive / single-step execution
    if args.answer:
        active_targets = rank_open_questions(state)[:3]
        res = process_user_answer(state, args.answer, active_targets)
        print(f"Parsed Answer: {json.dumps(res, indent=2)}")
        next_q = generate_question_batch(state)
        print(f"\nNext Turn: {json.dumps(next_q, indent=2)}")
    else:
        q = generate_question_batch(state)
        print(json.dumps(q, indent=2))

    save_json(out_file, state)


if __name__ == "__main__":
    main()
