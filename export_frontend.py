#!/usr/bin/env python3
"""Export RedTape Navigator Single-Page-Application for zero-config Vercel hosting.
Generates:
- public/index.html & index.html (SPA entry)
- public/static/* & public/favicon.ico (all branded logos & assets)
- vercel.json (SPA routing + optional rewrite config)
"""
import json
import shutil
from pathlib import Path
from ui_template import render_ui

ROOT = Path(__file__).resolve().parent
PUBLIC_DIR = ROOT / "public"
STATIC_SRC = ROOT / "static"
PUBLIC_STATIC = PUBLIC_DIR / "static"


def export():
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    PUBLIC_STATIC.mkdir(parents=True, exist_ok=True)

    # 1. Render SPA HTML
    html = render_ui()
    (PUBLIC_DIR / "index.html").write_text(html, encoding="utf-8")
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    print(f"✓ Wrote public/index.html & index.html ({len(html):,} bytes)")

    # 2. Copy static assets
    if STATIC_SRC.exists():
        for f in STATIC_SRC.iterdir():
            if f.is_file():
                shutil.copy2(f, PUBLIC_STATIC / f.name)
        print(f"✓ Mirrored static assets to public/static/")

        fav = STATIC_SRC / "favicon.ico"
        if fav.exists():
            shutil.copy2(fav, PUBLIC_DIR / "favicon.ico")
            shutil.copy2(fav, ROOT / "favicon.ico")

    # 3. Create vercel.json
    vercel_cfg_path = ROOT / "vercel.json"
    vercel_cfg = {
        "outputDirectory": "public",
        "cleanUrls": True,
        "trailingSlash": False,
        "rewrites": [
            {
                "source": "/(.*)",
                "destination": "/index.html"
            }
        ]
    }
    vercel_cfg_path.write_text(json.dumps(vercel_cfg, indent=2), encoding="utf-8")
    print(f"✓ Generated clean vercel.json for static SPA routing")


if __name__ == "__main__":
    export()
