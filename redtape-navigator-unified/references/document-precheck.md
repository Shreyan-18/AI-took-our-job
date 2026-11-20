# Supporting Document Pre-Check Protocol

Before the user uploads or submits supporting proofs (rent agreement, landlord NOC, electricity bill, Aadhaar/PAN, land khatian/ror, soil health card):
1. Map every required attachment to the specific licence/grant(s) that demand it (`required_supporting_documents[]`).
2. When the user supplies a scan/photo, verify:
   - **Name consistency** against `applicant_profile.applicant.name` / `entity_name`.
   - **Address consistency** against `applicant_profile.location.address`.
   - **Recency** (e.g., utility bill within 3 months, active rent lease period).
   - **Format & size** (portal limits like PDF/JPG <= 3MB).
3. Record `precheck_status` (`verified`, `mismatch`, `missing`) without echoing full Aadhaar/PAN numbers in logs.
