#!/usr/bin/env python3
"""RedTape Navigator — Clean Claude-Style Server with Login/Sign-Up & /chat/:id Navigation.
Serves on http://localhost:8765:
- /login, /signup : Clean account login & sign-up (name, email, password only — zero PAN/Aadhaar)
- /               : Home page for the chat interface
- /chat/:id       : Direct URL navigation to any saved consultation session
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

import auth_store
import postgres_db
from interview_engine_v2 import RedTapeSession, get_ollama_model, set_ollama_model
from ui_template import render_ui


def _get_available_ollama_models():
    try:
        import urllib.request
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3) as r:
            data = json.loads(r.read())
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        return ["llama3.1:8b", "llama3.2:3b"]


threading.Thread(target=postgres_db.init_db, daemon=True).start()

_SESSION_CACHE: dict[str, RedTapeSession] = {}
_CACHE_LOCK = threading.Lock()


def get_or_create_session(session_id: str = None, user_id: str = None) -> RedTapeSession:
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

        sess = RedTapeSession()
        sess.user_id = user_id
        sess.session_id = session_id or f"sess_{uuid.uuid4().hex[:10]}"
        _SESSION_CACHE[sess.session_id] = sess
        return sess


class RedTapeHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        sys.stderr.write(f"[RedTape] {self.command} {self.path} - {args[0]}\n")

    def send_json(self, data, code=200, set_cookie: str = None):
        body = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        if set_cookie is not None:
            self.send_header("Set-Cookie", set_cookie)
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

    def _serve_spa(self):
        body = render_ui().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path.startswith("/static/"):
            self._serve_file(ROOT_DIR / path.lstrip("/"), cache_header="public, max-age=86400")
            return
        if path == "/favicon.ico":
            self._serve_file(ROOT_DIR / "static" / "favicon.ico", cache_header="public, max-age=86400")
            return
        if path.startswith("/drafts/"):
            rel = path.lstrip("/")
            fpath = ROOT_DIR / rel
            if not fpath.exists():
                fpath = ROOT_DIR / "redtape-navigator-unified" / rel
            self._serve_file(fpath)
            return

        # Auth state (name + email ONLY — zero PAN/Aadhaar/address)
        if path == "/api/auth/me":
            user = auth_store.get_user_from_cookie(self.headers.get("Cookie", ""))
            if user:
                self.send_json({"authenticated": True, "user": user})
            else:
                self.send_json({"authenticated": False, "user": None})
            return

        if path == "/api/state":
            sid = qs.get("session_id", [None])[0]
            if sid:
                sess = get_or_create_session(sid)
                self.send_json(sess.to_dict())
            else:
                # Home page starts clean (empty welcome state)
                self.send_json(RedTapeSession().to_dict())
            return

        if path == "/api/model":
            self.send_json({
                "active_model": get_ollama_model(),
                "available_models": _get_available_ollama_models(),
            })
            return

        if path == "/api/sessions":
            all_sessions = postgres_db.list_sessions()
            self.send_json({"sessions": all_sessions, "count": len(all_sessions)})
            return

        if path.startswith("/api/session/"):
            sid = path.split("/api/session/", 1)[1].strip()
            sess = get_or_create_session(sid)
            self.send_json(sess.to_dict())
            return

        # SPA routes: Home (/), Login (/login, /signup), and Chat deep links (/chat, /chat/:id)
        if path in ("/", "/index.html", "/login", "/signup", "/chat") or path.startswith("/chat/"):
            self._serve_spa()
            return

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

        if parsed.path == "/api/auth/login":
            res, err = auth_store.login(payload.get("email", ""), payload.get("password", ""))
            if err:
                self.send_json({"authenticated": False, "error": err}, code=401)
            else:
                cookie = f"redtape_auth={res['token']}; Path=/; HttpOnly; SameSite=Lax"
                self.send_json({"authenticated": True, "user": res["user"]}, set_cookie=cookie)
            return

        if parsed.path == "/api/auth/signup":
            res, err = auth_store.signup(payload.get("name", ""), payload.get("email", ""), payload.get("password", ""))
            if err:
                self.send_json({"authenticated": False, "error": err}, code=400)
            else:
                cookie = f"redtape_auth={res['token']}; Path=/; HttpOnly; SameSite=Lax"
                self.send_json({"authenticated": True, "user": res["user"]}, set_cookie=cookie)
            return

        if parsed.path == "/api/auth/logout":
            auth_store.logout(self.headers.get("Cookie", ""))
            self.send_json({"authenticated": False}, set_cookie="redtape_auth=; Path=/; Max-Age=0; HttpOnly")
            return

        if parsed.path == "/api/chat":
            user = auth_store.get_user_from_cookie(self.headers.get("Cookie", ""))
            sid = payload.get("session_id")
            sess = get_or_create_session(sid, user_id=user["id"] if user else None)
            res = sess.handle_chat(payload.get("message", ""))
            # Ensure new session_id (if _start_new_scenario created one) is cached under its real ID
            with _CACHE_LOCK:
                if sess.session_id:
                    _SESSION_CACHE[sess.session_id] = sess
            self.send_json(res)
            return

        if parsed.path == "/api/model":
            req_model = payload.get("model", "")
            if req_model:
                set_ollama_model(req_model)
            self.send_json({
                "active_model": get_ollama_model(),
                "available_models": _get_available_ollama_models(),
            })
            return

        if parsed.path == "/api/new_chat":
            sess = RedTapeSession()
            sess.session_id = f"sess_{uuid.uuid4().hex[:10]}"
            with _CACHE_LOCK:
                _SESSION_CACHE[sess.session_id] = sess
            self.send_json(sess.to_dict())
            return

        if parsed.path == "/api/session/delete":
            sid = payload.get("id", "")
            postgres_db.delete_session(sid)
            with _CACHE_LOCK:
                _SESSION_CACHE.pop(sid, None)
            self.send_json({"success": True, "deleted_id": sid})
            return

        if parsed.path == "/api/documents/generate":
            sid = payload.get("session_id")
            sess = get_or_create_session(sid)
            sess.generate_docs()
            self.send_json(sess.to_dict())
            return

        self.send_response(404)
        self.end_headers()


def main():
    port = int(os.environ.get("PORT", 8765))
    server = HTTPServer(("0.0.0.0", port), RedTapeHTTPHandler)
    print(f"\n====================================================")
    print(f"  RedTape Navigator — Claude Interface Server")
    print(f"  Home:  http://localhost:{port}/")
    print(f"  Login: http://localhost:{port}/login")
    print(f"====================================================\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        server.server_close()


if __name__ == "__main__":
    main()
