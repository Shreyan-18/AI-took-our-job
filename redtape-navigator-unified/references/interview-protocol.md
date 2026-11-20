# Interactive Memory & Multilingual Interview Protocol

1. **Pre-Parse Opening Goal:** Extract every stated fact before asking a single question. Record the exact user phrase in `provenance`.
2. **Dependency-Driven Queue:** `open_questions` = unresolved `depends_on[]` of `Conditional` rows + mandatory blank form/portal fields, ranked by how many requirements each field unblocks.
3. **Batch & Cap:** Max **3 related questions per turn**, max **4 rounds** total.
4. **Multilingual Citizen Support:** Converse in the user's preferred language (English, Hindi, Bengali, etc.). Ask plain-language factual questions (never legal jargon). Normalize extracted values to typed English/official formats for forms.
5. **Indian Unit & Currency Parsing:** Convert `"8 lakh"` → `800000`, `"1.5 crore"` → `15000000`, `"DD/MM/YYYY"` → `"YYYY-MM-DD"`. Clarify local land units (`bigha`, `katha`, `guntha`) to acres/sq ft before writing.
6. **Confirm & Handle Contradictions:** Reflect parsed values back before committing. If the user revises an earlier answer, update it, note it in `provenance`, and re-run Compliance.
7. **PII Deferral:** Ask for PAN, Aadhaar last 4, or bank details ONLY after the final licence/grant list is confirmed, explaining which form needs each field.
