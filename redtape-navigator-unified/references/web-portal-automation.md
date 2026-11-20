# Digital Web Portal Submission Protocol

Most Indian government applications (FoSCoS FSSAI, KMC Online Enlistment, GST, Udyam, PM-FME, WB e-District, Agri-Direct Benefit Transfer) are **digital web portals** rather than downloadable PDFs.

## Workflow
1. Author a `portal_map.json` (see `assets/portal_map.example.json`) mapping portal steps, labels, optional CSS selectors, and upload requirements to `state.json` paths.
2. Run `python3 scripts/generate_portal_pack.py portal_map.json state.json --out drafts/<portal>_pack.md --manifest drafts/<portal>_manifest.json`.
3. Present the copy-paste sheet in the Human Review Checkpoint.
4. **Optional Browser Draft-Fill (Playwright):** Use the generated manifest to pre-fill non-sensitive text/select fields in a live browser session, then **halt immediately** at the first human gate: login/OTP, CAPTCHA, fee payment, or final Submit button.
