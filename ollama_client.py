"""
Ollama Local LLM Client for RedTape Navigator.
Provides local inference using llama3.1:8b (and ultra-fast llama3.2:3b).
Zero external API costs, zero rate limits, unlimited calls.
Tracks duration, token generation speed, and per-node metrics.
"""

import os
import json
import time
import urllib.request
import urllib.error
import re

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")
FAST_MODEL = "llama3.2:3b"

def get_active_model() -> str:
    """Returns the currently active Ollama model from env or default."""
    return os.environ.get("OLLAMA_MODEL", DEFAULT_MODEL)

def set_active_model(model_name: str):
    """Sets active Ollama model dynamically."""
    os.environ["OLLAMA_MODEL"] = model_name

def call_ollama(
    prompt: str,
    system_prompt: str = None,
    model: str = None,
    json_mode: bool = False,
    temperature: float = 0.1,
    timeout: int = 75,
    fallback_to_fast: bool = True
) -> dict:
    """
    Invokes local Ollama endpoint with error handling and metrics.
    Returns:
    {
        "text": str,
        "json": dict or list or None,
        "duration_seconds": float,
        "eval_count": int,
        "tokens_per_sec": float,
        "model": str,
        "success": bool,
        "error": str or None
    }
    """
    target_model = model or get_active_model()
    
    payload = {
        "model": target_model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature
        }
    }
    if system_prompt:
        payload["system"] = system_prompt
    if json_mode:
        payload["format"] = "json"

    t0 = time.time()
    try:
        req = urllib.request.Request(
            f"{OLLAMA_BASE_URL}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        elapsed = round(time.time() - t0, 2)
        raw_text = data.get("response", "").strip()
        eval_count = data.get("eval_count", 0)
        eval_duration = data.get("eval_duration", 1) / 1e9
        tps = round(eval_count / eval_duration, 1) if eval_duration > 0 else 0.0

        parsed_json = None
        if json_mode and raw_text:
            try:
                parsed_json = json.loads(raw_text)
            except Exception:
                # Try regex extract
                m = re.search(r"(\{.*\}|\[.*\])", raw_text, re.DOTALL)
                if m:
                    try:
                        parsed_json = json.loads(m.group(1))
                    except Exception:
                        parsed_json = None

        return {
            "text": raw_text,
            "json": parsed_json,
            "duration_seconds": elapsed,
            "eval_count": eval_count,
            "tokens_per_sec": tps,
            "model": target_model,
            "success": True,
            "error": None
        }

    except Exception as e:
        elapsed = round(time.time() - t0, 2)
        # If llama3.1:8b took too long or failed, optionally fallback to fast llama3.2:3b
        if fallback_to_fast and target_model != FAST_MODEL:
            print(f"[Ollama] Model {target_model} error or timeout ({e}). Trying fast model {FAST_MODEL}...")
            return call_ollama(
                prompt=prompt,
                system_prompt=system_prompt,
                model=FAST_MODEL,
                json_mode=json_mode,
                temperature=temperature,
                timeout=timeout,
                fallback_to_fast=False
            )
        
        return {
            "text": "",
            "json": None,
            "duration_seconds": elapsed,
            "eval_count": 0,
            "tokens_per_sec": 0.0,
            "model": target_model,
            "success": False,
            "error": str(e)
        }
