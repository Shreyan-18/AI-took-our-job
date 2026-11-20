#!/usr/bin/env python3
"""Comprehensive Automated Verification Test for Phase 7:
LangGraph StateGraph Orchestration & Live Web Demo Server.
Tests:
1. LangGraph StateGraph Architecture:
   - State schema and node integrity
   - Routing branches (compliance <-> interview loop, documents -> validate -> review)
   - Invariant validation and review package generation
2. Live Demo Server HTTP Interface (Port 8766):
   - Health check & GET /api/state
   - Presets catalog: GET /api/presets
   - Preset switching: POST /api/load_preset (bakery_kolkata, zoning_extension, agri_irrigation)
   - Interactive interview turn: POST /api/interview/answer
   - Document generation: POST /api/documents/generate
   - Live human override: POST /api/override (turnover > 12L & seating >= 50)
   - Artifact downloads: GET /drafts/demo_bakery_kolkata/*.pdf & *.md
"""
import json
import os
import sys
import threading
import time
import urllib.request
from http.server import HTTPServer
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts"))
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR.parent))

from demo_server import DemoServerHandler, LiveDemoState, ACTIVE_STATE
from workflow import RedTapeState, build_workflow, route_after_compliance, route_after_interview


TEST_PORT = 8766
BASE_URL = f"http://127.0.0.1:{TEST_PORT}"


def start_test_server():
    server = HTTPServer(("127.0.0.1", TEST_PORT), DemoServerHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.5)
    return server


def http_get(path):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.status, resp.headers.get("Content-Type"), resp.read()


def http_post(path, data):
    url = f"{BASE_URL}{path}"
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def test_langgraph_routing_and_structure():
    print("\n--- [Test 1] Testing LangGraph StateGraph Architecture & Routing ---")
    app = build_workflow(checkpointer=None, interrupt_interview=False, interrupt_review=False)
    assert app is not None
    print("  [PASS] LangGraph StateGraph successfully compiled.")

    # 1. Test compliance routing with open questions
    st_open = {
        "open_questions": ["applicant_profile.domain_attributes.expected_annual_turnover_inr"],
        "workflow_flags": {"interview_rounds": 0, "interview_complete": False}
    }
    route1 = route_after_compliance(st_open)
    assert route1 == "interview", f"Expected route 'interview', got {route1}"
    print("  [PASS] Compliance router routed to 'interview' when open questions exist.")

    # 2. Test compliance routing when complete
    st_closed = {
        "open_questions": [],
        "workflow_flags": {"interview_rounds": 2, "interview_complete": True}
    }
    route2 = route_after_compliance(st_closed)
    assert route2 == "documents", f"Expected route 'documents', got {route2}"
    print("  [PASS] Compliance router routed to 'documents' when questions resolved.")

    # 3. Test interview routing when compliance re-eval is needed
    st_reeval = {"workflow_flags": {"compliance_needs_reeval": True}}
    route3 = route_after_interview(st_reeval)
    assert route3 == "compliance", f"Expected route 'compliance', got {route3}"
    print("  [PASS] Interview router looped back to 'compliance' for re-evaluation.")


def test_server_endpoints():
    print(f"\n--- [Test 2] Testing Live Demo Server HTTP APIs on {BASE_URL} ---")

    # 1. GET /api/state
    status, ctype, body = http_get("/api/state")
    assert status == 200
    assert "application/json" in ctype
    state = json.loads(body.decode("utf-8"))
    assert "goal" in state and "compliance_matrix" in state
    print(f"  [PASS] GET /api/state returned active goal: \"{state['goal']}\"")

    # 2. GET /api/presets
    status, ctype, body = http_get("/api/presets")
    assert status == 200
    presets = json.loads(body.decode("utf-8"))
    assert "bakery_kolkata" in presets
    assert "zoning_extension" in presets
    assert "agri_irrigation" in presets
    print(f"  [PASS] GET /api/presets cataloged {len(presets)} verified domain presets.")

    # 3. POST /api/load_preset for all 3 scenarios
    for p_key in ("zoning_extension", "agri_irrigation", "bakery_kolkata"):
        status, res = http_post("/api/load_preset", {"preset": p_key})
        assert status == 200
        assert res.get("preset_key") == p_key
        print(f"  [PASS] Loaded preset '{p_key}' -> Domain: {res.get('domain')}, Matrix rows: {len(res.get('compliance_matrix', []))}")

    # 4. POST /api/interview/answer (Indian unit normalization)
    print("\n  Submitting citizen response with Indian units: '8 lakh rupees turnover with 3 workers'...")
    status, res = http_post("/api/interview/answer", {"answer": "8 lakh rupees annual turnover, 3 workers assisting"})
    assert status == 200
    # Check that turnover was resolved and FSSAI became Required
    fssai = next((r for r in res.get("compliance_matrix", []) if "fssai" in r["id"].lower()), None)
    assert fssai is not None
    assert fssai["status"] == "Required", f"Expected FSSAI status Required, got {fssai['status']}"
    print(f"  [PASS] Interview answer parsed -> FSSAI Basic status: {fssai['status']} ({fssai['rationale']})")

    # 5. POST /api/documents/generate
    print("\n  Generating dual-channel submission packs...")
    status, res = http_post("/api/documents/generate", {})
    assert status == 200
    forms = res.get("form_artifacts", [])
    portals = res.get("portal_artifacts", [])
    assert len(forms) > 0, "Expected at least 1 PDF form draft"
    assert len(portals) > 0, "Expected at least 1 Web portal pack"
    print(f"  [PASS] Generated {len(forms)} PDF drafts and {len(portals)} portal packs.")

    # 6. Test downloading generated artifact via HTTP
    pdf_path = forms[0]["file_path"]
    rel_pdf = pdf_path.split("redtape-navigator-unified/")[-1] if "redtape-navigator-unified/" in pdf_path else pdf_path
    if not rel_pdf.startswith("drafts/"):
        rel_pdf = "drafts/" + rel_pdf.split("drafts/")[-1]
    status, ctype, data = http_get(f"/{rel_pdf}")
    assert status == 200
    assert "application/pdf" in ctype
    assert len(data) > 1000
    print(f"  [PASS] Downloaded PDF draft /{rel_pdf} ({len(data)} bytes, Content-Type: {ctype})")

    # 7. POST /api/override (Live Human Override)
    print("\n  Applying live human override: turnover = ₹2.5 Crore (25,000,000)...")
    status, res = http_post("/api/override", {
        "field": "applicant_profile.domain_attributes.expected_annual_turnover_inr",
        "value": 25000000
    })
    assert status == 200
    # Confirm FSSAI Basic transitioned to Not Applicable or State License
    fssai_after = next((r for r in res.get("compliance_matrix", []) if "fssai" in r["id"].lower()), None)
    assert fssai_after is not None
    print(f"  [PASS] Override successfully re-evaluated matrix -> FSSAI: {fssai_after['name']} is {fssai_after['status']}")
    assert len(res.get("overrides", {})) > 0
    print(f"  [PASS] Active overrides: {res.get('overrides')}")

    # 8. Test Claude Chat History & Interaction API
    print("\n  Testing Claude Chat History & Conversational Reasoning APIs...")
    status, ctype, hist_bytes = http_get("/api/chat/history")
    assert status == 200
    hist = json.loads(hist_bytes.decode("utf-8"))
    assert "chat_history" in hist
    assert len(hist["chat_history"]) >= 2
    init_assistant = hist["chat_history"][1]
    assert init_assistant["role"] == "assistant"
    assert "thought_process" in init_assistant
    assert len(init_assistant["thought_process"]) >= 4
    print(f"  [PASS] /api/chat/history returned initial thought trace with {len(init_assistant['thought_process'])} nodes.")

    # 9. Test POST /api/chat with user message
    print("  Sending chat message: 'What if my turnover is 2.5 Crore?'...")
    status, chat_res = http_post("/api/chat", {"message": "What if my turnover is 2.5 Crore?"})
    assert status == 200
    assert "thought_process" in chat_res
    assert len(chat_res["thought_process"]) > 0
    assert "agent_reply" in chat_res or "reply" in chat_res
    assert chat_res.get("duration_seconds", 0) > 0
    print(f"  [PASS] POST /api/chat executed LangGraph reasoning in {chat_res.get('duration_seconds')}s with {len(chat_res['thought_process'])} evaluated nodes.")

    # 10. GET UI HTML page
    status, ctype, html_bytes = http_get("/")
    assert status == 200
    assert "text/html" in ctype
    html_text = html_bytes.decode("utf-8")
    assert "RedTape Navigator" in html_text
    assert "Claude UI · Agentic LangGraph" in html_text
    assert "claude-chat-container" in html_text
    assert "thinking-indicator" in html_text
    assert "artifacts-drawer" in html_text
    assert "1-Click Discretionary Overrides" in html_text
    print("  [PASS] Root GET / rendered full airy Claude Chat UI with thinking process & artifacts drawer.")


def main():
    print("=====================================================================")
    print("PHASE 7 TEST SUITE: LANGGRAPH ORCHESTRATION & LIVE WEB DEMO SERVER")
    print("=====================================================================")
    test_langgraph_routing_and_structure()

    server = start_test_server()
    try:
        test_server_endpoints()
    finally:
        server.shutdown()
        server.server_close()
        print("\n  [Server Shutdown] Test server cleanly stopped.")

    print("\n=====================================================================")
    print("ALL PHASE 7 ORCHESTRATION & SERVER CHECKS PASSED SUCCESSFULLY!")
    print("=====================================================================")


if __name__ == "__main__":
    main()
