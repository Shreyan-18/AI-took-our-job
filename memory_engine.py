"""
RedTape Citizen Memory & pgvector Retrieval Engine
Connects to Neon PostgreSQL pgvector (0.8.7) to persist and recall citizen attributes,
past statutory declarations, permit history, and consultation insights.
"""

import os
import re
import json
import hashlib
import numpy as np
import psycopg2
from typing import List, Dict, Any, Optional

_DATABASE_URL = None

def get_db_url() -> str:
    global _DATABASE_URL
    if _DATABASE_URL:
        return _DATABASE_URL
    
    # Try reading from .env
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("DATABASE_URL="):
                    _DATABASE_URL = line.strip().split("=", 1)[1].strip("\"'")
                    break
    if not _DATABASE_URL:
        _DATABASE_URL = os.environ.get("DATABASE_URL")
    if _DATABASE_URL:
        _DATABASE_URL = _DATABASE_URL.strip().strip('"').strip("'")
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
        parsed = urlparse(_DATABASE_URL)
        params = parse_qs(parsed.query, keep_blank_values=True)
        params.pop("channel_binding", None)
        new_query = urlencode({k: v[0] for k, v in params.items()})
        _DATABASE_URL = urlunparse(parsed._replace(query=new_query))
    return _DATABASE_URL or ""

def get_connection():
    url = get_db_url()
    if not url:
        raise ValueError("DATABASE_URL is not set.")
    return psycopg2.connect(url, connect_timeout=10)

# Deterministic 768-dimensional feature projection
_SEED = 42
_RNG = np.random.RandomState(_SEED)
_PROJECTION_MATRIX = _RNG.randn(2048, 768).astype(np.float32)

def generate_embedding_768(text: str) -> List[float]:
    """
    Generate a 768-dimensional dense semantic embedding vector.
    Uses sub-word/word n-gram hashing projected onto 768 dimensions with L2 normalization.
    """
    if not text:
        return [0.0] * 768
    
    # Tokenize words and character 3-grams
    clean = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    tokens = clean.split()
    features = np.zeros(2048, dtype=np.float32)
    
    # Word hashing
    for token in tokens:
        idx = int(hashlib.md5(token.encode('utf-8')).hexdigest(), 16) % 2048
        features[idx] += 1.0
        # Add character 3-grams for morphological/statutory keywords
        if len(token) >= 3:
            for i in range(len(token) - 2):
                ngram = token[i:i+3]
                n_idx = int(hashlib.md5(ngram.encode('utf-8')).hexdigest(), 16) % 2048
                features[n_idx] += 0.5
                
    # Normalize features
    norm = np.linalg.norm(features)
    if norm > 0:
        features = features / norm
        
    # Project to 768 dimensions
    dense = np.dot(features, _PROJECTION_MATRIX)
    dense_norm = np.linalg.norm(dense)
    if dense_norm > 0:
        dense = dense / dense_norm
        
    return [round(float(x), 6) for x in dense]

def vector_to_sql_str(vec: List[float]) -> str:
    return "[" + ",".join(f"{x:.6f}" for x in vec) + "]"

def store_citizen_memory(user_id: str, 
                         session_id: Optional[str], 
                         vector_type: str, 
                         content_chunk: str, 
                         metadata: Optional[Dict[str, Any]] = None) -> str:
    """
    Store an embedding chunk into citizen_memory_vectors table in Neon DB.
    """
    conn = get_connection()
    conn.autocommit = True
    cur = conn.cursor()
    try:
        vec = generate_embedding_768(content_chunk)
        vec_str = vector_to_sql_str(vec)
        meta_json = json.dumps(metadata or {})
        
        cur.execute("""
            INSERT INTO citizen_memory_vectors (user_id, session_id, vector_type, content_chunk, embedding, metadata)
            VALUES (%s, %s, %s, %s, %s::vector, %s::jsonb)
            RETURNING id;
        """, (user_id, session_id, vector_type, content_chunk, vec_str, meta_json))
        row = cur.fetchone()
        return str(row[0]) if row else ""
    finally:
        cur.close()
        conn.close()

def search_citizen_memory(user_id: str, query_text: str, limit: int = 4) -> List[Dict[str, Any]]:
    """
    Perform a cosine similarity vector search in Neon DB across citizen memory.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        vec = generate_embedding_768(query_text)
        vec_str = vector_to_sql_str(vec)
        
        cur.execute("""
            SELECT id, vector_type, content_chunk, metadata, 
                   1 - (embedding <=> %s::vector) AS similarity
            FROM citizen_memory_vectors
            WHERE user_id = %s
            ORDER BY embedding <=> %s::vector ASC
            LIMIT %s;
        """, (vec_str, user_id, vec_str, limit))
        
        rows = cur.fetchall()
        results = []
        for r in rows:
            results.append({
                "id": str(r[0]),
                "vector_type": r[1],
                "content_chunk": r[2],
                "metadata": r[3],
                "similarity": float(r[4])
            })
        return results
    finally:
        cur.close()
        conn.close()

def get_citizen_profile(user_id: str = "usr_tamajit_01") -> Optional[Dict[str, Any]]:
    """
    Fetch full citizen profile and associated business entities from Neon DB.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT u.id, u.name, u.email, u.phone_number, u.role,
                   cp.legal_name, cp.pan_number, cp.aadhaar_last4, cp.primary_mobile,
                   cp.primary_email, cp.residential_address, cp.district, cp.state, cp.pincode
            FROM "user" u
            LEFT JOIN citizen_profiles cp ON cp.user_id = u.id
            WHERE u.id = %s;
        """, (user_id,))
        row = cur.fetchone()
        if not row:
            return None
        
        profile = {
            "user_id": row[0],
            "name": row[1] or "",
            "email": row[2] or "",
            "phone_number": row[3] or "",
            "role": row[4] or "citizen",
            "legal_name": row[5] or row[1] or "",
            "pan_number": row[6] or "",
            "aadhaar_last4": row[7] or "",
            "primary_mobile": row[8] or row[3] or "",
            "primary_email": row[9] or row[2] or "",
            "residential_address": row[10] or "",
            "district": row[11] or "South 24 Parganas",
            "state": row[12] or "West Bengal",
            "pincode": row[13] or "700144",
            "business_entities": []
        }
        
        # Fetch business entities
        cur.execute("""
            SELECT id, trade_name, entity_type, registered_address, premises_type,
                   carpet_area_sqft, electricity_consumer_no, nic_code, turnover_bracket
            FROM business_entities
            WHERE citizen_profile_id = (SELECT id FROM citizen_profiles WHERE user_id = %s LIMIT 1);
        """, (user_id,))
        biz_rows = cur.fetchall()
        for b in biz_rows:
            profile["business_entities"].append({
                "id": str(b[0]),
                "trade_name": b[1],
                "entity_type": b[2],
                "registered_address": b[3],
                "premises_type": b[4],
                "carpet_area_sqft": b[5],
                "electricity_consumer_no": b[6],
                "nic_code": b[7],
                "turnover_bracket": b[8]
            })
            
        return profile
    finally:
        cur.close()
        conn.close()
