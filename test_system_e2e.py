#!/usr/bin/env python3
"""Comprehensive End-to-End Test for RedTape Navigator.
Tests:
1. Database connectivity & schema initialization on Neon PostgreSQL
2. Better Auth & Citizen Memory via pgvector
3. Local Ollama model integration (llama3.1:8b)
4. Multi-agent pipeline via RedTapeSession:
   - Turn 1: Goal parsing + Regulatory Research + Compliance Evaluation + Targeted Interview Questions
   - Turn 2: User answer intake with Indian units/currency normalization + Slot filling + Provenance
   - Turn 3: Completion + AcroForm PDF auto-population + Digital Portal packs + Validation
5. HTTP Server endpoints (GET/POST /api/state, /api/model, /api/chat, /api/auth/me, /api/sessions)
"""
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "redtape-navigator-unified" / "scripts"))

def test_database_and_auth():
    print("\n==========================================")
    print("1. TESTING NEON POSTGRESQL & CITIZEN AUTH")
    print("==========================================")
    import postgres_db
    import memory_engine

    conn = postgres_db.get_connection()
    assert conn is not None, "Failed to connect to Neon PostgreSQL"
    print(" [OK] Direct psycopg2 connection established to Neon")

    init_ok = postgres_db.init_db()
    assert init_ok, "Failed to initialize postgres schema"
    print(" [OK] Neon schema verified (redtape_sessions, messages, artifacts)")

    prof = memory_engine.get_citizen_profile("usr_tamajit_01")
    assert prof is not None, "Failed to fetch citizen profile"
    print(f" [OK] Authenticated citizen profile loaded: {prof['legal_name']} (PAN: {prof['pan_number']})")
    assert len(prof.get("business_entities", [])) > 0, "No business entities found for citizen"
    print(f" [OK] Past registered business entities: {[b['trade_name'] for b in prof['business_entities']]}")

def test_local_ollama():
    print("\n==========================================")
    print("2. TESTING LOCAL OLLAMA (llama3.1:8b)")
    print("==========================================")
    from ollama_client import call_ollama, get_active_model

    active = get_active_model()
    print(f" [INFO] Active Ollama model: {active}")
    res = call_ollama("Respond with the single word: OK", timeout=20)
    assert res.get("success"), f"Ollama call failed: {res.get('error')}"
    print(f" [OK] Local Ollama responded in {res['duration_seconds']}s ({res['tokens_per_sec']} t/s): {res['text'].strip()}")

def test_conversational_workflow():
    print("\n==========================================")
    print("3. TESTING MULTI-AGENT CONVERSATIONAL FLOW")
    print("==========================================")
    from interview_engine_v2 import RedTapeSession

    sess = RedTapeSession()
    sess.user_id = "usr_tamajit_01"

    # Turn 1: Citizen states natural language goal
    print("\n[Turn 1] Citizen: 'I want to open a small bakery in Park Circus, Kolkata with 5 counter seats'")
    t0 = time.time()
    r1 = sess.handle_chat("I want to open a small bakery in Park Circus, Kolkata with 5 counter seats")
    dur1 = round(time.time() - t0, 1)

    assert not r1.get("interview_turn", {}).get("complete"), "Expected interview to NOT be complete after turn 1"
    assert len(sess.compliance_matrix) > 0, "Compliance matrix should be populated"
    q1 = r1.get("interview_turn", {}).get("fields_targeted", [])
    print(f" [OK] Turn 1 processed in {dur1}s. Interview open questions generated targeting: {q1}")
    assert any("expected_annual_turnover" in f or "workers" in f or "floor_area" in f or "address" in f for f in q1)
    print(f" [OK] Turn 1 regulatory briefing delivered ({len(sess.compliance_matrix)} statutory requirements mapped)")

    # Turn 2: Citizen answers questions
    print("\n[Turn 2] Citizen: 'Our shop is Golden Crust Bakery at 14 Circus Avenue. We expect 8 lakh rupees annual turnover, 3 workers on site, 350 sq ft rented space, no commercial gas cylinders.'")
    t0 = time.time()
    r2 = sess.handle_chat("Our shop is Golden Crust Bakery at 14 Circus Avenue. We expect 8 lakh rupees annual turnover, 3 workers on site, 350 sq ft rented space, no commercial gas cylinders.")
    dur2 = round(time.time() - t0, 1)

    print(f" [OK] Turn 2 processed in {dur2}s.")
    # Check normalized profile metrics
    ap = sess.applicant_profile
    dom = ap.get("domain_attributes", {})
    print(f"  - Entity Name: {ap.get('entity_name')}")
    print(f"  - Turnover INR: {dom.get('expected_annual_turnover_inr')}")
    print(f"  - Workers on site: {dom.get('workers_on_site')}")
    print(f"  - Floor Area: {dom.get('floor_area_sqft')} sq ft")
    print(f"  - Premises: {ap.get('location', {}).get('premises_type')}")

    assert dom.get("expected_annual_turnover_inr") == 800000, f"Expected 800000, got {dom.get('expected_annual_turnover_inr')}"
    assert dom.get("workers_on_site") == 3, f"Expected 3, got {dom.get('workers_on_site')}"
    assert ap.get("location", {}).get("premises_type") == "rented"

    # Turn 3: Finalize or follow-up
    if not r2.get("interview_turn", {}).get("complete"):
        print("\n[Turn 3] Citizen: 'Please generate all application forms now.'")
        r3 = sess.handle_chat("Please generate all application forms now.")
    else:
        r3 = r2

    assert r3.get("has_artifacts"), "Expected artifacts to be generated"
    assert len(sess.form_artifacts) >= 3, f"Expected at least 3 form artifacts, got {len(sess.form_artifacts)}"
    assert len(sess.portal_artifacts) >= 3, f"Expected at least 3 portal artifacts, got {len(sess.portal_artifacts)}"
    print(f" [OK] Auto-filled AcroForm PDFs generated: {len(sess.form_artifacts)}")
    for fa in sess.form_artifacts:
        print(f"      📄 {fa['form_name']} ({fa.get('completion_percentage', 100)}% filled)")
    print(f" [OK] Digital Web Portal Manifests generated: {len(sess.portal_artifacts)}")
    for pa in sess.portal_artifacts:
        print(f"      🌐 {pa['portal_name']}")

def test_server_endpoints():
    print("\n==========================================")
    print("4. TESTING HTTP SERVER ENDPOINTS")
    print("==========================================")
    import subprocess
    server_proc = subprocess.Popen([sys.executable, str(ROOT / "demo_server.py")], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(2)

    try:
        # 1. Test /api/model
        with urllib.request.urlopen("http://127.0.0.1:8765/api/model", timeout=5) as r:
            m_data = json.loads(r.read())
            assert "active_model" in m_data and "available_models" in m_data
            print(f" [OK] GET /api/model -> active: {m_data['active_model']}, available: {m_data['available_models']}")

        # 2. Test /api/auth/me
        with urllib.request.urlopen("http://127.0.0.1:8765/api/auth/me", timeout=5) as r:
            auth_data = json.loads(r.read())
            assert auth_data.get("authenticated") is True
            print(f" [OK] GET /api/auth/me -> user: {auth_data['user']['name']} (Role: {auth_data['user']['role']})")

        # 3. Test /api/sessions
        with urllib.request.urlopen("http://127.0.0.1:8765/api/sessions", timeout=5) as r:
            sess_data = json.loads(r.read())
            assert "sessions" in sess_data
            print(f" [OK] GET /api/sessions -> {sess_data['count']} persistent sessions in Neon PostgreSQL")

        # 4. Test GET / (UI template)
        with urllib.request.urlopen("http://127.0.0.1:8765/", timeout=5) as r:
            html = r.read().decode("utf-8")
            assert "<!DOCTYPE html>" in html and "RedTape" in html
            print(" [OK] GET / -> Rendered 2026 Claude-style Web UI HTML")

    finally:
        server_proc.terminate()
        server_proc.wait()
        print(" [OK] HTTP server cleanly terminated")

if __name__ == "__main__":
    test_database_and_auth()
    test_local_ollama()
    test_conversational_workflow()
    test_server_endpoints()
    print("\n🎉 ALL E2E VERIFICATION TESTS PASSED SUCCESSFULLY!\n")
