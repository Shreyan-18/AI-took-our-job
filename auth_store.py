"""Minimal Account Auth Store (Name + Email + Password ONLY — zero PAN/Aadhaar/address at sign-in).
Stores salted SHA-256 password hashes in data/users.json and manages in-memory session cookies.
"""
import hashlib
import hmac
import json
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parent
USERS_PATH = ROOT / "data" / "users.json"
USERS_PATH.parent.mkdir(parents=True, exist_ok=True)

_SESSIONS: dict[str, dict] = {}


def _hash_pw(password: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()


def _load_users() -> dict:
    if USERS_PATH.exists():
        try:
            return json.loads(USERS_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    # Seed one default demo account (name + email + password ONLY)
    salt = secrets.token_hex(8)
    seeded = {
        "tamajit@redtape.app": {
            "id": "usr_tamajit",
            "name": "Tamajit Ghosh",
            "email": "tamajit@redtape.app",
            "salt": salt,
            "password_hash": _hash_pw("redtape123", salt),
        }
    }
    _save_users(seeded)
    return seeded


def _save_users(users: dict):
    USERS_PATH.write_text(json.dumps(users, indent=2), encoding="utf-8")


def signup(name: str, email: str, password: str) -> tuple[dict | None, str | None]:
    email_norm = (email or "").strip().lower()
    name_clean = (name or "").strip()
    if not name_clean or not email_norm or "@" not in email_norm or len(password or "") < 4:
        return None, "Please enter a valid name, email, and password (at least 4 characters)."
    users = _load_users()
    if email_norm in users:
        return None, "An account with this email already exists. Please sign in."
    salt = secrets.token_hex(8)
    user = {
        "id": f"usr_{secrets.token_hex(5)}",
        "name": name_clean,
        "email": email_norm,
        "salt": salt,
        "password_hash": _hash_pw(password, salt),
    }
    users[email_norm] = user
    _save_users(users)
    token = secrets.token_urlsafe(24)
    pub = {"id": user["id"], "name": user["name"], "email": user["email"]}
    _SESSIONS[token] = pub
    return {"token": token, "user": pub}, None


def login(email: str, password: str) -> tuple[dict | None, str | None]:
    email_norm = (email or "").strip().lower()
    users = _load_users()
    user = users.get(email_norm)
    if not user:
        return None, "Invalid email or password."
    expected = _hash_pw(password or "", user["salt"])
    if not hmac.compare_digest(expected, user["password_hash"]):
        return None, "Invalid email or password."
    token = secrets.token_urlsafe(24)
    pub = {"id": user["id"], "name": user["name"], "email": user["email"]}
    _SESSIONS[token] = pub
    return {"token": token, "user": pub}, None


def get_user_from_cookie(cookie_header: str) -> dict | None:
    if not cookie_header:
        return None
    for part in cookie_header.split(";"):
        part = part.strip()
        if part.startswith("redtape_auth="):
            tok = part.split("=", 1)[1].strip()
            if tok in _SESSIONS:
                return _SESSIONS[tok]
    return None


def get_user_from_auth_header(auth_header: str) -> dict | None:
    if not auth_header:
        return None
    auth_header = auth_header.strip()
    if auth_header.lower().startswith("bearer "):
        tok = auth_header[7:].strip()
        if tok in _SESSIONS:
            return _SESSIONS[tok]
    return None


def get_user_from_request(headers) -> dict | None:
    """Extract authenticated user from Authorization Bearer header or Cookie."""
    if not headers:
        return None
    # 1. Bearer header
    auth_h = headers.get("Authorization") or headers.get("authorization") or ""
    u = get_user_from_auth_header(auth_h)
    if u:
        return u
    # 2. Cookie header
    cookie_h = headers.get("Cookie") or headers.get("cookie") or ""
    return get_user_from_cookie(cookie_h)


def logout(cookie_header: str = "", auth_header: str = ""):
    if auth_header and auth_header.lower().startswith("bearer "):
        tok = auth_header[7:].strip()
        _SESSIONS.pop(tok, None)
    if cookie_header:
        for part in cookie_header.split(";"):
            part = part.strip()
            if part.startswith("redtape_auth="):
                tok = part.split("=", 1)[1].strip()
                _SESSIONS.pop(tok, None)
