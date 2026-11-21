"""
High-Performance PostgreSQL database adapter for RedTape Navigator.
Provides persistent storage for chat sessions, messages, states, and provenance on Neon PostgreSQL.
Features:
- Connection reuse & auto-reconnect
- Non-blocking background worker for persistence
- In-memory hot cache for instant UI rendering
- Zero slowdown to the live demo
"""

import os
import sys
import json
import queue
import logging
import threading
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

logger = logging.getLogger("RedTapePostgres")

def _get_database_url():
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
    url = os.environ.get("DATABASE_URL")
    if not url and os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    if k.strip() == "DATABASE_URL":
                        url = v.strip().strip('"').strip("'")
                        break
    if url:
        url = str(url).strip().strip('"').strip("'")
        # psycopg2 does not support channel_binding - rebuild query string without it
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query, keep_blank_values=True)
            params.pop("channel_binding", None)
            new_query = urlencode({k: v[0] for k, v in params.items()})
            url = urlunparse(parsed._replace(query=new_query))
        except Exception:
            import re
            url = re.sub(r'[&?]channel_binding=[^&]*', '', url)
            url = re.sub(r'\?&', '?', url)
            url = re.sub(r'\?$', '', url)
    return url

DATABASE_URL = _get_database_url()

_SHARED_CONN = None
_CONN_LOCK = threading.Lock()

def get_connection():
    """Returns a shared active psycopg2 connection to PostgreSQL with auto-reconnect."""
    global _SHARED_CONN
    with _CONN_LOCK:
        if _SHARED_CONN is not None and not _SHARED_CONN.closed:
            try:
                with _SHARED_CONN.cursor() as cur:
                    cur.execute("SELECT 1;")
                return _SHARED_CONN
            except Exception:
                try:
                    _SHARED_CONN.close()
                except Exception:
                    pass
                _SHARED_CONN = None

        url = _get_database_url()
        if not url:
            return None
        try:
            conn = psycopg2.connect(url, connect_timeout=4)
            conn.autocommit = True
            _SHARED_CONN = conn
            return conn
        except Exception as e:
            logger.warning(f"Postgres connection failed: {e}")
            return None

def init_db():
    """Verifies and creates tables if they don't exist matching Prisma schema."""
    conn = get_connection()
    if not conn:
        logger.warning("Postgres unavailable, using in-memory mode.")
        return False
    try:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS redtape_sessions (
                id VARCHAR(64) PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                goal TEXT NOT NULL,
                business_type VARCHAR(128),
                trade_category VARCHAR(128),
                location_district VARCHAR(128),
                municipality_block VARCHAR(128),
                state VARCHAR(64) DEFAULT 'West Bengal',
                applicant_profile JSONB DEFAULT '{}'::jsonb,
                compliance_matrix JSONB DEFAULT '[]'::jsonb,
                status VARCHAR(32) DEFAULT 'active',
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS redtape_messages (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(64) REFERENCES redtape_sessions(id) ON DELETE CASCADE,
                role VARCHAR(32) NOT NULL,
                content TEXT NOT NULL,
                thought_process JSONB,
                interview_turn JSONB,
                thinking_summary TEXT,
                duration_seconds NUMERIC(5,2),
                has_artifacts BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS redtape_artifacts (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(64) REFERENCES redtape_sessions(id) ON DELETE CASCADE,
                form_name VARCHAR(128) NOT NULL,
                file_path TEXT NOT NULL,
                completion_percentage INTEGER DEFAULT 0,
                artifact_type VARCHAR(32) DEFAULT 'pdf',
                metadata JSONB,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE INDEX IF NOT EXISTS idx_redtape_messages_session ON redtape_messages(session_id);
            CREATE INDEX IF NOT EXISTS idx_redtape_sessions_updated ON redtape_sessions(updated_at DESC);
            CREATE INDEX IF NOT EXISTS idx_redtape_artifacts_session ON redtape_artifacts(session_id);
            """)
        return True
    except Exception as e:
        logger.error(f"Error initializing Postgres schema: {e}")
        return False

def clear_all_chat_history():
    """Wipes all chat history from database and local caches."""
    _LOCAL_SESSIONS.clear()
    _LOCAL_MESSAGES.clear()
    _DELETED_SESSIONS.clear()
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE redtape_artifacts, redtape_messages, redtape_sessions CASCADE;")
            return True
        except Exception as e:
            logger.error(f"Error truncating tables: {e}")
            return False
    return True

# In-memory hot cache for zero-latency UI responses
_LOCAL_SESSIONS = {}
_LOCAL_MESSAGES = {}
_DELETED_SESSIONS = set()

# Background task queue for non-blocking asynchronous persistence
_WRITE_QUEUE = queue.Queue()

def _bg_worker():
    """Background worker that commits writes to Postgres without delaying HTTP turn responses."""
    while True:
        task = _WRITE_QUEUE.get()
        if task is None:
            break
        action = task.get("action")
        try:
            conn = get_connection()
            if not conn:
                continue
            
            if action == "save_session":
                with conn.cursor() as cur:
                    cur.execute("""
                    INSERT INTO redtape_sessions (
                        id, title, goal, business_type, trade_category, location_district, municipality_block, state, applicant_profile, compliance_matrix, status, user_id, citizen_profile_id, business_entity_id, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (id) DO UPDATE SET
                        title = EXCLUDED.title,
                        goal = EXCLUDED.goal,
                        business_type = EXCLUDED.business_type,
                        trade_category = EXCLUDED.trade_category,
                        location_district = EXCLUDED.location_district,
                        municipality_block = EXCLUDED.municipality_block,
                        applicant_profile = EXCLUDED.applicant_profile,
                        compliance_matrix = EXCLUDED.compliance_matrix,
                        status = EXCLUDED.status,
                        user_id = COALESCE(EXCLUDED.user_id, redtape_sessions.user_id),
                        citizen_profile_id = COALESCE(EXCLUDED.citizen_profile_id, redtape_sessions.citizen_profile_id),
                        business_entity_id = COALESCE(EXCLUDED.business_entity_id, redtape_sessions.business_entity_id),
                        updated_at = NOW();
                    """, (
                        task["id"],
                        task["title"],
                        task["goal"],
                        task.get("business_type"),
                        task.get("trade_category"),
                        task.get("location_district"),
                        task.get("municipality_block"),
                        task.get("state", "West Bengal"),
                        json.dumps(task.get("applicant_profile", {})),
                        json.dumps(task.get("compliance_matrix", [])),
                        task.get("status", "active"),
                        task.get("user_id", "usr_tamajit_01"),
                        task.get("citizen_profile_id", "cit_tamajit_01"),
                        task.get("business_entity_id", "biz_tamajit_01")
                    ))

            elif action == "add_message":
                with conn.cursor() as cur:
                    cur.execute("""
                    INSERT INTO redtape_messages 
                    (session_id, role, content, thought_process, interview_turn, thinking_summary, duration_seconds, has_artifacts)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                    """, (
                        task["session_id"],
                        task["role"],
                        task["content"],
                        json.dumps(task["thought_process"]) if task.get("thought_process") else None,
                        json.dumps(task["interview_turn"]) if task.get("interview_turn") else None,
                        task.get("thinking_summary"),
                        task.get("duration_seconds"),
                        task.get("has_artifacts", False)
                    ))
                    cur.execute("UPDATE redtape_sessions SET updated_at = NOW() WHERE id = %s;", (task["session_id"],))

            elif action == "delete_session":
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM redtape_sessions WHERE id = %s;", (task["id"],))
                _DELETED_SESSIONS.discard(task["id"])

        except Exception as e:
            logger.error(f"Background Postgres task '{action}' failed: {e}")
        finally:
            _WRITE_QUEUE.task_done()

# Start background persistence thread
_WORKER_THREAD = threading.Thread(target=_bg_worker, daemon=True)
_WORKER_THREAD.start()

def save_session(session_id, title, goal, business_type="", trade_category="", location_district="", municipality_block="", state="West Bengal", applicant_profile=None, compliance_matrix=None, state_dict=None):
    """Instantly updates in-memory cache and dispatches async write to Postgres."""
    _LOCAL_SESSIONS[session_id] = {
        "id": session_id,
        "title": title,
        "goal": goal,
        "business_type": business_type,
        "trade_category": trade_category,
        "location_district": location_district,
        "municipality_block": municipality_block,
        "state": state,
        "applicant_profile": applicant_profile or {},
        "compliance_matrix": compliance_matrix or [],
        "state_json": state_dict or {},
        "updated_at": datetime.utcnow().strftime("%b %d, %H:%M"),
        "message_count": len(_LOCAL_MESSAGES.get(session_id, []))
    }
    
    _WRITE_QUEUE.put({
        "action": "save_session",
        "id": session_id,
        "title": title,
        "goal": goal,
        "business_type": business_type,
        "trade_category": trade_category,
        "location_district": location_district,
        "municipality_block": municipality_block,
        "state": state,
        "applicant_profile": applicant_profile or {},
        "compliance_matrix": compliance_matrix or [],
        "state_json": state_dict or {}
    })
    return True

def add_message(session_id, role, content, thought_process=None, duration_seconds=None, has_artifacts=False, interview_turn=None, thinking_summary=None):
    """Instantly updates in-memory messages and dispatches async write to Postgres."""
    msg_obj = {
        "session_id": session_id,
        "role": role,
        "content": content,
        "thought_process": thought_process or [],
        "duration_seconds": duration_seconds,
        "has_artifacts": has_artifacts,
        "interview_turn": interview_turn,
        "thinking_summary": thinking_summary,
        "timestamp": datetime.utcnow().strftime("%H:%M")
    }
    if session_id not in _LOCAL_MESSAGES:
        _LOCAL_MESSAGES[session_id] = []
    _LOCAL_MESSAGES[session_id].append(msg_obj)

    if session_id in _LOCAL_SESSIONS:
        _LOCAL_SESSIONS[session_id]["message_count"] = len(_LOCAL_MESSAGES[session_id])
        _LOCAL_SESSIONS[session_id]["updated_at"] = datetime.utcnow().strftime("%b %d, %H:%M")

    _WRITE_QUEUE.put({
        "action": "add_message",
        "session_id": session_id,
        "role": role,
        "content": content,
        "thought_process": thought_process,
        "duration_seconds": duration_seconds,
        "has_artifacts": has_artifacts,
        "interview_turn": interview_turn,
        "thinking_summary": thinking_summary
    })
    return True

def list_sessions():
    """Returns list of all chat sessions with summary metadata, ordered by recency."""
    conn = get_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                SELECT 
                    s.id, 
                    s.title, 
                    s.goal, 
                    s.business_type, 
                    s.location_district, 
                    s.municipality_block, 
                    s.updated_at,
                    COUNT(m.id) as message_count
                FROM redtape_sessions s
                LEFT JOIN redtape_messages m ON s.id = m.session_id
                GROUP BY s.id, s.title, s.goal, s.business_type, s.location_district, s.municipality_block, s.updated_at
                ORDER BY s.updated_at DESC;
                """)
                rows = cur.fetchall()
                results = []
                for r in rows:
                    if r["id"] in _DELETED_SESSIONS:
                        continue
                    results.append({
                        "id": r["id"],
                        "title": r["title"],
                        "goal": r["goal"],
                        "business_type": r["business_type"],
                        "location_district": r["location_district"],
                        "municipality_block": r["municipality_block"],
                        "updated_at": r["updated_at"].strftime("%b %d, %H:%M") if r["updated_at"] else "Recently",
                        "message_count": int(r["message_count"])
                    })
                # Sync into local cache and include hot uncommitted sessions
                existing_ids = {r["id"] for r in results}
                for s_id, s_data in _LOCAL_SESSIONS.items():
                    if s_id not in existing_ids and s_id not in _DELETED_SESSIONS:
                        results.insert(0, {
                            "id": s_id,
                            "title": s_data.get("title", "Consultation"),
                            "goal": s_data.get("goal", ""),
                            "business_type": s_data.get("business_type"),
                            "location_district": s_data.get("location_district"),
                            "municipality_block": s_data.get("municipality_block"),
                            "updated_at": s_data.get("updated_at", "Just now"),
                            "message_count": s_data.get("message_count", len(_LOCAL_MESSAGES.get(s_id, [])))
                        })
                for res in results:
                    if res["id"] not in _LOCAL_SESSIONS:
                        _LOCAL_SESSIONS[res["id"]] = res
                return results
        except Exception as e:
            logger.warning(f"Error listing sessions from Postgres: {e}")

    # Fallback to in-memory hot cache
    items = list(_LOCAL_SESSIONS.values())
    items.sort(key=lambda x: str(x.get("updated_at", "")), reverse=True)
    return items

def get_session_details(session_id):
    """Retrieves session state and its ordered message stream."""
    conn = get_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM redtape_sessions WHERE id = %s;", (session_id,))
                session_row = cur.fetchone()
                if session_row:
                    cur.execute("""
                    SELECT role, content, thought_process, interview_turn, thinking_summary, duration_seconds, has_artifacts, created_at
                    FROM redtape_messages
                    WHERE session_id = %s
                    ORDER BY id ASC;
                    """, (session_id,))
                    msg_rows = cur.fetchall()

                    messages = []
                    for m in msg_rows:
                        messages.append({
                            "role": m["role"],
                            "content": m["content"],
                            "thought_process": m["thought_process"] or [],
                            "interview_turn": m["interview_turn"],
                            "thinking_summary": m["thinking_summary"],
                            "duration_seconds": float(m["duration_seconds"]) if m["duration_seconds"] is not None else 1.0,
                            "has_artifacts": m["has_artifacts"] or False,
                            "timestamp": m["created_at"].strftime("%H:%M") if m["created_at"] else "Just now"
                        })

                    return {
                        "session": {
                            "id": session_row["id"],
                            "title": session_row["title"],
                            "goal": session_row["goal"],
                            "business_type": session_row["business_type"],
                            "trade_category": session_row["trade_category"],
                            "location_district": session_row["location_district"],
                            "municipality_block": session_row["municipality_block"],
                            "state": session_row["state"],
                            "applicant_profile": session_row["applicant_profile"],
                            "compliance_matrix": session_row["compliance_matrix"],
                            "status": session_row["status"]
                        },
                        "messages": messages
                    }
        except Exception as e:
            logger.warning(f"Error fetching session details from Postgres: {e}")

    # Fallback to local cache
    sess = _LOCAL_SESSIONS.get(session_id)
    msgs = _LOCAL_MESSAGES.get(session_id, [])
    if sess:
        return {
            "session": sess,
            "messages": msgs
        }
    return None

def delete_session(session_id):
    """Deletes a chat session and all cascading messages."""
    _DELETED_SESSIONS.add(session_id)
    _LOCAL_SESSIONS.pop(session_id, None)
    _LOCAL_MESSAGES.pop(session_id, None)

    _WRITE_QUEUE.put({
        "action": "delete_session",
        "id": session_id
    })
    return True
