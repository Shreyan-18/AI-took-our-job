#!/usr/bin/env python3
"""
Benchmark script to run the whole pipeline with Ollama models
and measure exact per-node latency and throughput.
"""
import sys
import time
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = ROOT_DIR / "redtape-navigator-unified" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(ROOT_DIR))

from ollama_client import call_ollama, set_active_model
from document_engine import generate_documents

# Prompts to test
TEST_PROMPTS = [
    "open a bakery shop in kolkata park circus, kolkata",
    "open a stationary book stall in sodpur",
    "open a clothes shop in barrackpore"
]

def benchmark_run(model_name: str, prompt: str):
    print(f"\n=======================================================")
    print(f"  BENCHMARKING MODEL: {model_name}")
    print(f"  PROMPT: \"{prompt}\"")
    print(f"=======================================================")
    set_active_model(model_name)
    total_start = time.time()
    timings = {}

    # NODE 1: Intent & Slot Grounding Parser
    print("\n[Node 1] Intent & Slot Grounding Parser...")
    n1_sys = """You are the RedTape Intent & Provenance Parser for Indian administrative filings.
Extract strictly from the citizen goal into JSON:
{
  "domain": "business",
  "activity_type": "bakery/book_stall/clothing_store/etc",
  "entity_name": "extracted or plausible name",
  "location": {
    "city_or_village": "city name",
    "district": "district name",
    "state": "West Bengal"
  },
  "provenance": {
    "activity": "exact quote from user",
    "location": "exact quote from user"
  }
}
Do not invent facts not in user prompt. Output ONLY valid JSON."""

    t0 = time.time()
    n1_res = call_ollama(
        prompt=f"Citizen Goal: {prompt}",
        system_prompt=n1_sys,
        model=model_name,
        json_mode=True,
        temperature=0.1
    )
    timings["node_1_intent"] = {
        "duration": n1_res["duration_seconds"],
        "tokens": n1_res["eval_count"],
        "speed": n1_res["tokens_per_sec"],
        "success": n1_res["success"]
    }
    print(f"  -> Done in {n1_res['duration_seconds']}s | {n1_res['eval_count']} tokens | {n1_res['tokens_per_sec']} t/s")
    parsed_profile = n1_res.get("json") or {}
    print(f"  -> Extracted Activity: {parsed_profile.get('activity_type')}, Location: {parsed_profile.get('location', {}).get('city_or_village')}")

    # NODE 2: 3-Tier Regulatory Research Grounding
    print("\n[Node 2] 3-Tier Statutory Regulations Sweep...")
    t0 = time.time()
    # Curated statutory rules retrieved based on jurisdiction
    loc_city = parsed_profile.get("location", {}).get("city_or_village", "Kolkata")
    act = parsed_profile.get("activity_type", "retail")
    is_food = any(w in str(act).lower() for w in ("bake", "bakery", "food", "cafe", "restaurant"))

    n2_sys = """You are the RedTape Statutory Regulatory Auditor for Indian Municipal and State law.
Identify the 3 to 4 statutory permits/licenses required for the business in West Bengal.
Output a JSON array:
[
  {
    "name": "Permit Name",
    "tier": "municipal/state/central",
    "status": "Required/Conditional/Not Applicable",
    "statutory_fee": "statutory fee string",
    "trigger_reason": "statutory reason under Indian law"
  }
]
Output ONLY JSON."""

    n2_res = call_ollama(
        prompt=f"Business activity: {act} in {loc_city}, West Bengal. Is Food Business: {is_food}. Identify statutory trade licenses, state labor registration, and food/safety requirements.",
        system_prompt=n2_sys,
        model=model_name,
        json_mode=True,
        temperature=0.1
    )
    timings["node_2_research"] = {
        "duration": n2_res["duration_seconds"],
        "tokens": n2_res["eval_count"],
        "speed": n2_res["tokens_per_sec"],
        "success": n2_res["success"]
    }
    print(f"  -> Done in {n2_res['duration_seconds']}s | {n2_res['eval_count']} tokens | {n2_res['tokens_per_sec']} t/s")

    # NODE 3: Statutory Compliance Classification Evaluator
    print("\n[Node 3] Statutory Compliance Classification Matrix...")
    n3_sys = """You are the RedTape Compliance Matrix Evaluator.
Given the candidate permits, evaluate whether each is Required, Conditional on user scale, or Explicitly Exempt under Indian law.
Return a clean JSON array with fields: name, tier, status, statutory_fee, trigger_reason.
Output ONLY JSON."""

    n3_prompt = f"Activity: {act}, Location: {loc_city}. Evaluate rules for this activity:\n{n2_res.get('text', '')}"
    n3_res = call_ollama(
        prompt=n3_prompt,
        system_prompt=n3_sys,
        model=model_name,
        json_mode=True,
        temperature=0.1
    )
    timings["node_3_compliance"] = {
        "duration": n3_res["duration_seconds"],
        "tokens": n3_res["eval_count"],
        "speed": n3_res["tokens_per_sec"],
        "success": n3_res["success"]
    }
    print(f"  -> Done in {n3_res['duration_seconds']}s | {n3_res['eval_count']} tokens | {n3_res['tokens_per_sec']} t/s")

    # NODE 4: Surgical Slot-Filling & Interview Question
    print("\n[Node 4] Conversational Slot Formulation & Interview...")
    n4_sys = """You are the RedTape Citizen Interviewer.
Formulate a single polite, plain-language question in English (with Namaste) to determine the license tier (e.g. asking for expected turnover or floor area).
Output JSON:
{
  "question": "polite question text",
  "field_targeted": "expected_annual_turnover_inr or floor_area_sqft",
  "suggested_options": ["Option 1", "Option 2", "Option 3"]
}
Output ONLY JSON."""

    n4_res = call_ollama(
        prompt=f"Goal: {prompt}. Need clarification for determining licensing category for {act} in {loc_city}.",
        system_prompt=n4_sys,
        model=model_name,
        json_mode=True,
        temperature=0.2
    )
    timings["node_4_interview"] = {
        "duration": n4_res["duration_seconds"],
        "tokens": n4_res["eval_count"],
        "speed": n4_res["tokens_per_sec"],
        "success": n4_res["success"]
    }
    print(f"  -> Done in {n4_res['duration_seconds']}s | {n4_res['eval_count']} tokens | {n4_res['tokens_per_sec']} t/s")
    int_q = (n4_res.get("json") or {}).get("question", "")
    print(f"  -> Question: {int_q}")

    # NODE 5: Document Synthesis (AcroForm PDFs)
    print("\n[Node 5] Dual-Channel Document & PDF Synthesis...")
    t0 = time.time()
    # Document engine ReportLab/PyMuPDF generation
    # Ensure compliance matrix items are dicts with 'name' and 'status'
    matrix_clean = []
    raw_m = n3_res.get("json") or []
    if isinstance(raw_m, dict):
        raw_m = raw_m.get("items") or raw_m.get("permits") or [raw_m]
    if isinstance(raw_m, list):
        for item in raw_m:
            if isinstance(item, dict) and "name" in item:
                matrix_clean.append({
                    "name": item.get("name", "Permit"),
                    "status": item.get("status", "Required"),
                    "tier": item.get("tier", "municipal"),
                    "statutory_fee": item.get("statutory_fee", "Statutory Fee"),
                    "trigger_reason": item.get("trigger_reason", "Statutory requirement")
                })
    if not matrix_clean:
        matrix_clean = [
            {"name": "KMC Certificate of Enlistment (Trade License)", "status": "Required", "tier": "municipal"},
            {"name": "Registration under WB Shops & Establishments Act 1963", "status": "Required", "tier": "state"},
            {"name": "FSSAI Registration (Form A)", "status": "Conditional", "tier": "central"}
        ]

    dummy_state = {
        "project_id": "benchmark_test",
        "domain": "business",
        "applicant_profile": {
            "entity_name": parsed_profile.get("entity_name", "Park Circus Bakery"),
            "activity_type": act,
            "applicant": {"name": "Citizen Applicant"},
            "location": {"city_or_village": loc_city, "address": f"Main Road, {loc_city}"},
            "domain_attributes": {"expected_annual_turnover_inr": None}
        },
        "compliance_matrix": matrix_clean,
        "required_supporting_documents": ["Trade License Application", "Proof of Identity", "Rent Agreement"]
    }
    out_dir = ROOT_DIR / "redtape-navigator-unified" / "drafts" / "benchmark_test"
    doc_res = generate_documents(dummy_state, output_dir=str(out_dir))
    doc_duration = round(time.time() - t0, 2)
    timings["node_5_documents"] = {
        "duration": doc_duration,
        "artifacts_count": len(doc_res.get("form_artifacts", [])),
        "success": True
    }
    print(f"  -> Done in {doc_duration}s | Form Artifacts: {len(doc_res.get('form_artifacts', []))}")

    total_time = round(time.time() - total_start, 2)
    timings["total_duration"] = total_time
    print(f"\n=======================================================")
    print(f"  TOTAL END-TO-END LATENCY FOR {model_name}: {total_time}s")
    print(f"=======================================================")
    return timings

if __name__ == "__main__":
    prompt = TEST_PROMPTS[0] # Bakery prompt
    print(f"Running benchmark on: {prompt}")
    
    # Run 1: llama3.1:8b
    timings_8b = benchmark_run("llama3.1:8b", prompt)

    # Run 2: llama3.2:3b
    timings_3b = benchmark_run("llama3.2:3b", prompt)

    print("\n\n" + "#"*60)
    print("       FINAL COMPARISON SUMMARY: 8B vs 3B")
    print("#"*60)
    print(f"{'Node':<30} | {'llama3.1:8b':<12} | {'llama3.2:3b':<12}")
    print("-" * 60)
    print(f"{'Node 1 (Intent & Slot)':<30} | {timings_8b['node_1_intent']['duration']}s ({timings_8b['node_1_intent']['speed']} t/s) | {timings_3b['node_1_intent']['duration']}s ({timings_3b['node_1_intent']['speed']} t/s)")
    print(f"{'Node 2 (Statutory Sweep)':<30} | {timings_8b['node_2_research']['duration']}s ({timings_8b['node_2_research']['speed']} t/s) | {timings_3b['node_2_research']['duration']}s ({timings_3b['node_2_research']['speed']} t/s)")
    print(f"{'Node 3 (Compliance Matrix)':<30} | {timings_8b['node_3_compliance']['duration']}s ({timings_8b['node_3_compliance']['speed']} t/s) | {timings_3b['node_3_compliance']['duration']}s ({timings_3b['node_3_compliance']['speed']} t/s)")
    print(f"{'Node 4 (Interview Question)':<30} | {timings_8b['node_4_interview']['duration']}s ({timings_8b['node_4_interview']['speed']} t/s) | {timings_3b['node_4_interview']['duration']}s ({timings_3b['node_4_interview']['speed']} t/s)")
    print(f"{'Node 5 (Document Synthesis)':<30} | {timings_8b['node_5_documents']['duration']}s             | {timings_3b['node_5_documents']['duration']}s")
    print("-" * 60)
    print(f"{'TOTAL LATENCY':<30} | {timings_8b['total_duration']}s            | {timings_3b['total_duration']}s")
    print("#"*60)
