---
name: redtape-document
description: Dual-channel Document & Portal Agent that populates official PDF forms (AcroForm + flat overlay with dual-backend fallback) and generates structured Digital Web Portal submission packs.
---

# Document & Portal Agent

## Channel A: Official PDF Forms
1. Inspect with `python3 scripts/inspect_pdf.py <form.pdf> --json`.
2. Map PDF AcroForm keys or flat coordinates to dotted `state.json` paths (`assets/field_map.example.json`).
3. Fill with `python3 scripts/fill_pdf.py <form.pdf> <field_map.json> state.json --out drafts/<name>.pdf --report drafts/<name>.report.json --stamp-pending`.
4. Supported transforms: `upper`, `title`, `digits`, `phone_10digit`, `pan`, `date_ddmmyyyy`, `inr_words`, `comma_list`.
5. Never invent mandatory values; `--stamp-pending` marks both AcroForm widgets and flat coordinates with `[PENDING_USER_INPUT]` for preview.

## Channel B: Digital Web Portals
Most modern government portals (FoSCoS, KMC, GST, Udyam, PM-FME, e-District) are web-only. For every portal-based application:
1. Build a `portal_map.json` (`assets/portal_map.example.json`) listing portal URL, login/OTP requirements, step-by-step fields, CSS selectors (optional), and upload slots.
2. Run `python3 scripts/generate_portal_pack.py portal_map.json state.json --out drafts/<portal>_pack.md --manifest drafts/<portal>_manifest.json`.
3. If browser automation is used, fill draft fields ONLY and **stop strictly before OTP, CAPTCHA, payment, or final submit**.

## System Prompt
See `prompts/document_system.md`.
