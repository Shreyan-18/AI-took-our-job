# Graph Report - red-tape  (2026-11-20)

## Corpus Check
- 47 files · ~14,352 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 352 nodes · 535 edges · 23 communities (19 shown, 4 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b31bbe03`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- _common.py
- properties
- $ref
- properties
- properties
- RedTape Navigator Unified Skill
- properties
- type
- properties
- properties
- research_engine.py
- sys
- Problem Statement
- India Agricultural Grants Jurisdiction
- India Food Business Jurisdiction
- India Residential Zoning Jurisdiction
- properties
- properties
- project_state.json
- provenance
- created_at
- domain
- overrides

## God Nodes (most connected - your core abstractions)
1. `load_json()` - 17 edges
2. `RedTape Navigator Unified Skill` - 15 edges
3. `save_json()` - 14 edges
4. `effective_value()` - 13 edges
5. `is_blank()` - 10 edges
6. `research()` - 9 edges
7. `apply_transform()` - 8 edges
8. `validate()` - 8 edges
9. `parse_intent()` - 8 edges
10. `search_serpapi_with_circuit_breaker()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `make_state()` --calls--> `parse_intent()`  [EXTRACTED]
  redtape-navigator-unified/scripts/init_state.py → redtape-navigator-unified/scripts/orchestrator_parser.py
- `RedTape Navigator Unified Skill` --references--> `Compliance Agent Skill`  [EXTRACTED]
  redtape-navigator-unified/SKILL.md → redtape-navigator-unified/agents/compliance/SKILL.md
- `RedTape Navigator Unified Skill` --references--> `Document Agent Skill`  [EXTRACTED]
  redtape-navigator-unified/SKILL.md → redtape-navigator-unified/agents/document/SKILL.md
- `RedTape Navigator Unified Skill` --references--> `Interview Agent Skill`  [EXTRACTED]
  redtape-navigator-unified/SKILL.md → redtape-navigator-unified/agents/interview/SKILL.md
- `RedTape Navigator Unified Skill` --references--> `Orchestrator Agent Skill`  [EXTRACTED]
  redtape-navigator-unified/SKILL.md → redtape-navigator-unified/agents/orchestrator/SKILL.md

## Import Cycles
- None detected.

## Communities (23 total, 4 thin omitted)

### Community 0 - "_common.py"
Cohesion: 0.13
Nodes (23): apply_transform(), effective_value(), get_path(), inr_to_indian_words(), is_blank(), load_json(), mask(), save_json() (+15 more)

### Community 1 - "properties"
Cohesion: 0.05
Nodes (43): type, items, type, items, type, type, items, type (+35 more)

### Community 2 - "$ref"
Cohesion: 0.20
Nodes (10): items, type, items, type, $ref, items, type, compliance_matrix (+2 more)

### Community 3 - "properties"
Cohesion: 0.06
Nodes (31): maximum, minimum, type, type, description, items, type, type (+23 more)

### Community 4 - "properties"
Cohesion: 0.08
Nodes (24): maximum, minimum, type, type, type, type, type, items (+16 more)

### Community 5 - "RedTape Navigator Unified Skill"
Cohesion: 0.09
Nodes (22): Compliance Agent Skill, Document Agent Skill, Interview Agent Skill, Orchestrator Agent Skill, Research Agent Skill, Validation Agent Skill, Compliance System Prompt, Document System Prompt (+14 more)

### Community 6 - "properties"
Cohesion: 0.10
Nodes (20): type, type, type, type, minimum, type, compliance_complete, compliance_needs_reeval (+12 more)

### Community 7 - "type"
Cohesion: 0.20
Nodes (10): items, type, type, items, type, errors, open_questions, research_findings (+2 more)

### Community 8 - "properties"
Cohesion: 0.07
Nodes (28): type, description, type, properties, type, properties, type, type (+20 more)

### Community 9 - "properties"
Cohesion: 0.11
Nodes (18): type, type, type, properties, type, type, type, enum (+10 more)

### Community 10 - "research_engine.py"
Cohesion: 0.09
Nodes (14): catalog_supporting_documents(), compliance(), evaluate_with_gemini(), find_api_key(), main(), parse_intent(), build_search_queries(), call_gemini_research() (+6 more)

### Community 11 - "sys"
Cohesion: 0.24
Nodes (6): need(), inspect(), main(), render_page(), main(), run()

### Community 16 - "properties"
Cohesion: 0.20
Nodes (10): type, default, type, type, properties, goal, preferred_language, project_id (+2 more)

### Community 17 - "properties"
Cohesion: 0.20
Nodes (10): type, passed, timestamp, validation, warnings, type, properties, type (+2 more)

### Community 18 - "project_state.json"
Cohesion: 0.33
Nodes (5): description, required, $schema, title, type

### Community 19 - "provenance"
Cohesion: 0.50
Nodes (4): type, provenance, additionalProperties, type

### Community 20 - "created_at"
Cohesion: 0.67
Nodes (3): format, type, created_at

### Community 21 - "domain"
Cohesion: 0.67
Nodes (3): enum, type, domain

### Community 22 - "overrides"
Cohesion: 0.67
Nodes (3): additionalProperties, type, overrides

## Knowledge Gaps
- **19 isolated node(s):** `Problem Statement`, `India Agricultural Grants Jurisdiction`, `India Food Business Jurisdiction`, `India Residential Zoning Jurisdiction`, `Compliance System Prompt` (+14 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 165 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `properties` connect `properties` to `$ref`, `properties`, `type`, `properties`, `properties`, `project_state.json`, `provenance`, `created_at`, `domain`, `overrides`?**
  _High betweenness centrality (0.101) - this node is a cross-community bridge._
- **What connects `Problem Statement`, `India Agricultural Grants Jurisdiction`, `India Food Business Jurisdiction` to the rest of the system?**
  _19 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `_common.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._
- **Why does `properties` connect `properties` to `properties`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Should `properties` be split into smaller, more focused modules?**
  _Cohesion score 0.048625792811839326 - nodes in this community are weakly interconnected._
- **Why does `applicant_profile` connect `properties` to `properties`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Should `properties` be split into smaller, more focused modules?**
  _Cohesion score 0.06451612903225806 - nodes in this community are weakly interconnected._