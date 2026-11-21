#!/usr/bin/env python3
"""RedTape — 1-Click Inference Tunnel Launcher for Vercel / Remote Access.
1. Checks if local demo_server.py is running on port 8765 (starts it if needed).
2. Starts ngrok tunnel on port 8765.
3. Automatically retrieves and displays your public HTTPS tunnel URL and
   generates the exact shareable Vercel link with ?backend= parameter.
"""
import json
import os
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

PORT = int(os.environ.get("PORT", 8765))
ROOT = Path(__file__).resolve().parent


def is_port_in_use(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def get_ngrok_public_url(timeout=10) -> str | None:
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen("http://127.0.0.1:4040/api/tunnels", timeout=2) as r:
                data = json.loads(r.read())
                tunnels = data.get("tunnels", [])
                for t in tunnels:
                    public_url = t.get("public_url", "")
                    if public_url.startswith("https://"):
                        return public_url
                if tunnels:
                    return tunnels[0].get("public_url")
        except Exception:
            time.sleep(0.5)
    return None


def main():
    print("\n" + "=" * 68)
    print("  🚀 RedTape Navigator — Starting Local Inference Tunnel")
    print("=" * 68)

    server_proc = None
    if not is_port_in_use(PORT):
        print(f"[*] Starting local backend demo_server.py on port {PORT}...")
        server_proc = subprocess.Popen(
            [sys.executable, str(ROOT / "demo_server.py")],
            cwd=str(ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(1.5)
        if not is_port_in_use(PORT):
            print(f"[!] Warning: demo_server.py may not have started properly.")
    else:
        print(f"[✓] demo_server.py is already active on http://localhost:{PORT}")

    # Check for ngrok binary
    ngrok_bin = subprocess.run(["which", "ngrok"], capture_output=True, text=True).stdout.strip()
    if not ngrok_bin:
        print("\n[!] Error: 'ngrok' binary not found in PATH.")
        print("    Install it via: brew install ngrok")
        sys.exit(1)

    print("[*] Launching ngrok tunnel...")
    ngrok_proc = subprocess.Popen(
        [ngrok_bin, "http", str(PORT), "--log=stdout"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    try:
        tunnel_url = get_ngrok_public_url(timeout=12)
        if not tunnel_url:
            print("[!] Could not retrieve tunnel URL from ngrok API.")
            print("    Check if ngrok is authenticated or run 'ngrok http 8765' directly.")
            sys.exit(1)

        print("\n" + "=" * 68)
        print("  🎉 INFERENCE TUNNEL ACTIVE & READY FOR REMOTE ACCESS!")
        print("=" * 68)
        print(f"  • Local Endpoint:     http://localhost:{PORT}")
        print(f"  • Public HTTPS:       {tunnel_url}")
        print("-" * 68)
        print("  📱 USE FROM WINDOWS / JUDGE LAPTOPS:")
        print(f"  Option 1: In the RedTape frontend (top-right), click")
        print(f"            'Backend: Local' and enter: {tunnel_url}")
        print()
        print(f"  Option 2 (Instant 1-Click Auto-Connect Link):")
        print(f"  Open your Vercel URL with ?backend= parameter:")
        print(f"  https://<your-project>.vercel.app/?backend={tunnel_url}")
        print("=" * 68)
        print("\n[Press Ctrl+C to terminate tunnel]")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[*] Shutting down tunnel...")
    finally:
        if ngrok_proc and ngrok_proc.poll() is None:
            ngrok_proc.terminate()
        if server_proc and server_proc.poll() is None:
            server_proc.terminate()
        print("[✓] Tunnel stopped cleanly.\n")


if __name__ == "__main__":
    main()
