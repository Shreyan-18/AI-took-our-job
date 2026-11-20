#!/usr/bin/env python3
"""End-to-end smoke test for RedTape Navigator Unified scripts.
Tests: init_state -> validate_state -> flat PDF create/inspect/fill -> portal pack -> render_review.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def run(cmd):
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("FAILED:", " ".join(cmd))
        print("STDOUT:", res.stdout)
        print("STDERR:", res.stderr)
        sys.exit(1)
    print("OK:", res.stdout.strip())


def main():
    with tempfile.TemporaryDirectory(prefix="redtape_test_") as tmp:
        tmp = Path(tmp)
        # 1. Init state across all 3 domains
        for dom, goal in [
            ("business", "open a small bakery in Kolkata"),
            ("zoning", "add a second floor residential extension in Salt Lake"),
            ("agriculture", "apply for drip irrigation grant in Nadia"),
        ]:
            run([sys.executable, str(SCRIPTS / "init_state.py"), "--goal", goal, "--domain", dom, "--out", str(tmp / f"{dom}.json")])

        # 2. Validate example bakery state
        ex_state = ROOT / "examples" / "bakery_kolkata" / "state_snapshot.json"
        run([sys.executable, str(SCRIPTS / "validate_state.py"), str(ex_state)])

        # 3. Generate portal submission pack
        run([
            sys.executable, str(SCRIPTS / "generate_portal_pack.py"),
            str(ROOT / "assets" / "portal_map.example.json"),
            str(ex_state),
            "--out", str(tmp / "foscos_pack.md"),
            "--manifest", str(tmp / "foscos_manifest.json"),
        ])

        # 4. Create a minimal sample PDF via reportlab (if installed) and test inspect + fill
        try:
            from reportlab.pdfgen import canvas
            sample_pdf = tmp / "sample_form.pdf"
            c = canvas.Canvas(str(sample_pdf))
            c.drawString(72, 740, "Official Application Form")
            c.drawString(72, 700, "Applicant Name:")
            c.drawString(72, 670, "Date of Birth:")
            c.save()
            run([sys.executable, str(SCRIPTS / "inspect_pdf.py"), str(sample_pdf)])
            fmap = tmp / "fmap.json"
            fmap.write_text('{"form":"sample_form.pdf","fields":[{"target":{"page":0,"x":180,"y":92,"fontsize":10},"source":"applicant_profile.entity_name","transform":"upper","mandatory":true},{"target":{"page":0,"x":180,"y":122,"fontsize":10},"source":"applicant_profile.applicant.pan","transform":"pan","mandatory":true}]}')
            run([
                sys.executable, str(SCRIPTS / "fill_pdf.py"),
                str(sample_pdf), str(fmap), str(ex_state),
                "--out", str(tmp / "filled.pdf"),
                "--report", str(tmp / "filled.report.json"),
                "--stamp-pending",
            ])
        except ImportError:
            print("SKIP: reportlab not installed for synthetic PDF test")

        # 5. Render review package
        run([sys.executable, str(SCRIPTS / "render_review.py"), str(ex_state), "--out", str(tmp / "review.md")])
        review_text = (tmp / "review.md").read_text(encoding="utf-8")
        assert "## 1. Compliance Matrix" in review_text and "## 6. Submission Readiness" in review_text
        print("ALL PIPELINE TESTS PASSED")


if __name__ == "__main__":
    main()
