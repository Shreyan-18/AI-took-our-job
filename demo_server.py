#!/usr/bin/env python3
"""RedTape Navigator — Clean Zero-API Claude Replica Server.
Serves the authentic Claude.ai-style interface on http://localhost:8765 backed by:
- Local verified 2026 statutory knowledge base (data/scenarios_kb.json)
- Stateful 4-turn conversational interview engine (interview_engine_v2.py)
- Real local AcroForm PDF auto-filling per session
- Neon PostgreSQL persistence (postgres_db.py)
- Live asynchronous Langfuse multi-agent observability (langfuse_tracer.py)
"""
import json
import os
import sys
import threading
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

import postgres_db
from interview_engine_v2 import RedTapeSession, get_ollama_model, set_ollama_model
from ui_template import render_ui


def _get_available_ollama_models():
    try:
        import urllib.request, json
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=3) as r:
            data = json.loads(r.read())
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        return ["llama3.1:8b", "llama3.2:3b"]

AVAILABLE_MODELS = _get_available_ollama_models()

# Ensure Neon Postgres schema exists asynchronously without blocking socket bind
threading.Thread(target=postgres_db.init_db, daemon=True).start()

# In-memory thread-safe session pool (backed by Neon PostgreSQL)
_SESSION_CACHE: dict[str, RedTapeSession] = {}
_CACHE_LOCK = threading.Lock()


def get_or_create_session(session_id: str = None) -> RedTapeSession:
    """Retrieves session from cache/Postgres, or instantiates a fresh session."""
    with _CACHE_LOCK:
        if session_id and session_id in _SESSION_CACHE:
            return _SESSION_CACHE[session_id]

        if session_id:
            rec = postgres_db.get_session_details(session_id)
            if rec:
                sess = RedTapeSession()
                sess.load_from_db_record(rec)
                _SESSION_CACHE[session_id] = sess
                return sess

        # Create brand-new isolated session
        sess = RedTapeSession()
        sess.user_id = "usr_tamajit_01"
        if session_id:
            sess.session_id = session_id
        else:
            sess.session_id = f"sess_{uuid.uuid4().hex[:10]}"
        _SESSION_CACHE[sess.session_id] = sess
        return sess


def get_active_session_fallback() -> RedTapeSession:
    """Returns the most recent session or an empty one."""
    with _CACHE_LOCK:
        if _SESSION_CACHE:
            return list(_SESSION_CACHE.values())[-1]
    sessions = postgres_db.list_sessions()
    if sessions:
        return get_or_create_session(sessions[0]["id"])
    return get_or_create_session()


class RedTapeHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        sys.stderr.write(f"[RedTape] {self.command} {self.path} - {args[0]}\n")

    def send_json(self, data, code=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _serve_file(self, fpath: Path, cache_header: str = None):
        if not fpath.exists() or not fpath.is_file():
            self.send_response(404)
            self.end_headers()
            return
        ext = fpath.suffix.lower()
        ctype_map = {
            ".png": "image/png",
            ".ico": "image/x-icon",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".svg": "image/svg+xml",
            ".pdf": "application/pdf",
            ".md": "text/plain; charset=utf-8",
            ".txt": "text/plain; charset=utf-8",
            ".json": "application/json; charset=utf-8",
            ".html": "text/html; charset=utf-8",
        }
        data = fpath.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype_map.get(ext, "application/octet-stream"))
        if cache_header:
            self.send_header("Cache-Control", cache_header)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path.startswith("/static/"):
            rel_parts = [p for p in path.strip("/").split("/") if p]
            self._serve_file(ROOT_DIR.joinpath(*rel_parts), cache_header="public, max-age=86400")
            return
        if path == "/favicon.ico":
            self._serve_file(ROOT_DIR / "static" / "favicon.ico", cache_header="public, max-age=86400")
            return
        if path.startswith("/drafts/"):
            rel_parts = [p for p in path.strip("/").split("/") if p]
            fpath = ROOT_DIR.joinpath(*rel_parts)
            if not fpath.exists():
                fpath = ROOT_DIR.joinpath("redtape-navigator-unified", *rel_parts)
            self._serve_file(fpath)
            return

        if path == "/api/state":
            sid = qs.get("session_id", [None])[0]
            sess = get_or_create_session(sid) if sid else get_active_session_fallback()
            self.send_json(sess.to_dict())
        elif path == "/api/model":
            self.send_json({
                "active_model": get_ollama_model(),
                "available_models": AVAILABLE_MODELS,
            })
        elif path == "/api/sessions":
            all_sessions = postgres_db.list_sessions()
            self.send_json({
                "sessions": all_sessions,
                "count": len(all_sessions),
            })
        elif path.startswith("/api/session/"):
            sid = path.split("/api/session/", 1)[1].strip()
            sess = get_or_create_session(sid)
            self.send_json(sess.to_dict())
        elif path == "/api/auth/me":
            try:
                from memory_engine import get_citizen_profile
                prof = get_citizen_profile("usr_tamajit_01")
                self.send_json({
                    "authenticated": True,
                    "provider": "neon_better_auth",
                    "user": {
                        "id": prof["user_id"],
                        "name": prof["name"],
                        "email": prof["email"],
                        "phone": prof["phone_number"],
                        "role": prof["role"]
                    },
                    "citizen_profile": {
                        "legal_name": prof["legal_name"],
                        "pan": prof["pan_number"],
                        "aadhaar_last4": prof["aadhaar_last4"],
                        "primary_mobile": prof["primary_mobile"],
                        "residential_address": prof["residential_address"],
                        "district": prof["district"],
                        "state": prof["state"],
                        "pincode": prof["pincode"]
                    },
                    "business_entities": prof.get("business_entities", [])
                })
            except Exception as e:
                self.send_json({"error": str(e), "authenticated": False}, code=500)
        elif path == "/api/memory":
            try:
                from memory_engine import search_citizen_memory
                query = qs.get("q", [""])[0]
                hits = search_citizen_memory("usr_tamajit_01", query, limit=5) if query else []
                self.send_json({"query": query, "memories": hits})
            except Exception as e:
                self.send_json({"error": str(e), "memories": []}, code=500)
        elif path == "/api/new_chat":
            sess = RedTapeSession()
            sess.user_id = "usr_tamajit_01"
            sess.session_id = f"sess_{uuid.uuid4().hex[:10]}"
            with _CACHE_LOCK:
                _SESSION_CACHE[sess.session_id] = sess
            self.send_json(sess.to_dict())
        elif path in ("/", "/index.html"):
            body = render_ui().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def do_DELETE(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/session/"):
            sid = parsed.path.split("/api/session/", 1)[1].strip()
            postgres_db.delete_session(sid)
            with _CACHE_LOCK:
                _SESSION_CACHE.pop(sid, None)
            self.send_json({"success": True, "deleted_id": sid})
        elif parsed.path == "/api/clear_history":
            postgres_db.clear_all_chat_history()
            with _CACHE_LOCK:
                _SESSION_CACHE.clear()
            self.send_json({"success": True})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            payload = json.loads(raw)
        except Exception:
            payload = {}

        if parsed.path == "/api/chat":
            sid = payload.get("session_id")
            sess = get_or_create_session(sid)
            res = sess.handle_chat(payload.get("message", ""))
            self.send_json(res)
        elif parsed.path == "/api/model":
            req_model = payload.get("model", "")
            if req_model:
                set_ollama_model(req_model)
            self.send_json({
                "active_model": get_ollama_model(),
                "available_models": AVAILABLE_MODELS,
            })
        elif parsed.path == "/api/new_chat":
            sess = RedTapeSession()
            sess.user_id = "usr_tamajit_01"
            sess.session_id = f"sess_{uuid.uuid4().hex[:10]}"
            with _CACHE_LOCK:
                _SESSION_CACHE[sess.session_id] = sess
            self.send_json(sess.to_dict())
        elif parsed.path == "/api/clear_history":
            postgres_db.clear_all_chat_history()
            with _CACHE_LOCK:
                _SESSION_CACHE.clear()
            self.send_json({"success": True})
        elif parsed.path == "/api/session/delete":
            sid = payload.get("id", "")
            postgres_db.delete_session(sid)
            with _CACHE_LOCK:
                _SESSION_CACHE.pop(sid, None)
            self.send_json({"success": True, "deleted_id": sid})
        elif parsed.path == "/api/documents/generate":
            sid = payload.get("session_id")
            sess = get_or_create_session(sid)
            sess.generate_docs()
            self.send_json(sess.to_dict())
        else:
            self.send_response(404)
            self.end_headers()


def main():
    port = int(os.environ.get("PORT", 8765))
    server = HTTPServer(("0.0.0.0", port), RedTapeHTTPHandler)
    print(f"\n====================================================")
    print(f"  RedTape Navigator — Claude Interface Server")
    print(f"  Listening on http://localhost:{port}")
    print(f"====================================================\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        server.server_close()


if __name__ == "__main__":
    main()
