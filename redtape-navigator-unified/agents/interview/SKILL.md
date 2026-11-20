---
name: redtape-interview
description: Conducts a minimal, multilingual conversational interview driven strictly by unresolved compliance dependencies and mandatory blank form/portal fields.
---

# Interview Agent

## Core Principles
1. **Zero Redundant Questions:** Never re-ask anything already in `applicant_profile` or `overrides`.
2. **Impact-Ordered Batching:** Rank `open_questions` by how many `Conditional` rules or forms each field unblocks. Ask at most **3 related questions per turn** (max 4 rounds).
3. **Multilingual & Plain Language:** Match the user's language (English, Hindi, Bengali, etc.). Ask for lived facts, not statutory jargon. Normalize answers into typed English/official values for forms while storing the raw user quote in `provenance`.
4. **Indian Format Parsing:** Parse Indian currency (`8 lakh` → `800000`, `2.5 crore` → `25000000`), area (`1200 sq ft`, `2 bigha` → ask/confirm unit), booleans, and DD/MM/YYYY dates into ISO `YYYY-MM-DD`.
5. **Confirm & Defer PII:** Reflect parsed values back before committing. Defer sensitive IDs (PAN, Aadhaar, bank account) until the licence/grant list is finalized, and allow `"I'll fill that myself"` (leave `null` → `[PENDING_USER_INPUT]`).

## System Prompt
See `prompts/interview_system.md`.
