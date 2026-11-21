import urllib.request
import json
import time
import subprocess
import sys
import os

print("Starting demo server on port 8765...")
proc = subprocess.Popen([sys.executable, "demo_server.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
time.sleep(3)
if proc.poll() is not None:
    print("Process exited early!")
    out, err = proc.communicate()
    print("STDOUT:", out.decode())
    print("STDERR:", err.decode())
    sys.exit(1)


BASE_URL = "http://127.0.0.1:8765"

def get(path):
    req = urllib.request.Request(f"{BASE_URL}{path}")
    with urllib.request.urlopen(req) as resp:
        return resp.status, resp.read()

def post(path, data):
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(f"{BASE_URL}{path}", data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

try:
    print("\n1. Testing GET / (HTML UI)...")
    status, html_bytes = get("/")
    html = html_bytes.decode("utf-8")
    assert status == 200
    assert "chat-sidebar" in html
    assert "New Consultation" in html
    assert "open a bakery shop in kolkata park circus, kolkata" in html
    assert "open a stationary book stall in sodpur" in html
    assert "open a clothes shop in barrackpore" in html
    print("   -> PASSED! Sidebar, New Consultation, and 3 prompt cards present in HTML.")

    print("\n2. Testing initial GET /api/state (Clean Welcome State)...")
    status, state_bytes = get("/api/state")
    state = json.loads(state_bytes.decode("utf-8"))
    assert status == 200
    assert state.get("is_empty") is True
    assert len(state.get("chat_history", [])) == 0
    print("   -> PASSED! Server starts in clean, unpopulated welcome state.")

    print("\n3. Testing GET /api/sessions (Postgres Listing)...")
    status, sess_bytes = get("/api/sessions")
    sess_data = json.loads(sess_bytes.decode("utf-8"))
    assert status == 200
    assert "sessions" in sess_data
    initial_count = len(sess_data["sessions"])
    print(f"   -> PASSED! Found {initial_count} existing sessions in Postgres.")

    print("\n4. Testing POST /api/chat with Prompt 1: Bakery in Park Circus...")
    prompt1 = "open a bakery shop in kolkata park circus, kolkata"
    status, res1 = post("/api/chat", {"message": prompt1})
    assert status == 200
    assert len(res1["chat_history"]) == 2
    assert "thought_process" in res1
    assert "AcroForm" in res1["agent_reply"]
    session_id_1 = res1["state"]["session_id"]
    print(f"   -> PASSED! Session created: {session_id_1}, title: {res1['state']['title']}")

    print("\n5. Verifying Session 1 persisted in Postgres...")
    status, sess_bytes = get("/api/sessions")
    sess_data = json.loads(sess_bytes.decode("utf-8"))
    assert any(s["id"] == session_id_1 for s in sess_data["sessions"])
    print("   -> PASSED! Session 1 appears in Postgres sessions list.")

    print("\n6. Testing POST /api/new_chat (Resetting to Clean Screen)...")
    status, new_chat_res = post("/api/new_chat", {})
    assert status == 200
    assert new_chat_res.get("is_empty") is True
    assert len(new_chat_res.get("chat_history", [])) == 0
    print("   -> PASSED! State reset back to clean screen.")

    print("\n7. Testing POST /api/chat with Prompt 2: Book Stall in Sodpur...")
    prompt2 = "open a stationary book stall in sodpur"
    status, res2 = post("/api/chat", {"message": prompt2})
    assert status == 200
    assert "Panihati" in res2["agent_reply"]
    session_id_2 = res2["state"]["session_id"]
    print(f"   -> PASSED! Session 2 created: {session_id_2}, title: {res2['state']['title']}")

    print("\n8. Testing GET /api/session/<id> (Loading Session 1 from Postgres)...")
    status, loaded_bytes = get(f"/api/session/{session_id_1}")
    loaded_state = json.loads(loaded_bytes.decode("utf-8"))
    assert loaded_state["session_id"] == session_id_1
    assert "park circus" in loaded_state["goal"].lower()
    print("   -> PASSED! Session 1 accurately reloaded from Postgres.")

    print("\n9. Clean up test sessions in Postgres...")
    post(f"/api/session/delete", {"id": session_id_1})
    post(f"/api/session/delete", {"id": session_id_2})
    print("   -> Cleaned up test sessions.")

    print("\nALL SERVER TESTS PASSED SUCCESSFULLY!")

finally:
    proc.terminate()
    proc.wait()
