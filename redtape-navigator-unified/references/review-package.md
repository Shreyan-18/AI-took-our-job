# Human Review Checkpoint Spec

`scripts/render_review.py` produces all 6 transparency sections:
1. **Compliance Matrix** (tier, status, channel, fee, official URL, verified date).
2. **Audit Trail & Rule Reasoning** (quotes thresholds, user values, and `history[]` transitions).
3. **Conflicts & System Notices** (contradictory official sources and fallback warnings).
4. **Filled PDF Drafts & Digital Portal Packs** (completion %, missing fields, file paths).
5. **Supporting Document Checklist** (mapped per licence/grant + pre-check status).
6. **Submission Readiness** (blockers, notes, masked PII, and human sign-off prompt).

User edits live in `state.overrides` and win over agent values on any re-run.
