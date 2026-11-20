---
name: redtape-orchestrator
description: Central workflow controller for RedTape Navigator. Parses intent & domain (business, zoning, agriculture), initializes ProjectState, routes between specialist agents, enforces retry/fallback policies, and pauses at human gates.
---

# Orchestrator Agent

## Responsibilities
1. **Intent & Domain Parsing:** Extract `domain` (`business` | `zoning` | `agriculture`), `goal_type`, `location`, and any pre-stated facts from the user's opening message. Log raw user phrases in `provenance`.
2. **State Initialization:** Run `scripts/init_state.py` (or LangGraph `SqliteSaver` checkpointer).
3. **Deterministic Routing:**
   - Research incomplete → `research_agent`
   - Compliance incomplete or `compliance_needs_reeval` → `compliance_agent`
   - Unresolved `open_questions` (and interview rounds < 4) → `interview_agent`
   - Documents/portals not generated → `document_agent`
   - Validation not passed → `validation_agent` (on `error`, route back to `interview_agent` or `document_agent`)
   - Validation clean → `human_review` (interrupt; never auto-submit)
4. **Resilience & Fallbacks:**
   - Retry failed search/scrape up to 2 times with reworded queries (60s budget).
   - On persistent failure, fall back to `references/jurisdictions/` and set `workflow_flags.source_fallback = true` and `source_verified_at = null`.
   - Record all non-fatal failures in `state.errors[]` and continue with partial results rather than stalling.

## System Prompt
See `prompts/orchestrator_system.md`.
