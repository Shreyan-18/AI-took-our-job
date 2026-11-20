# Graph Report - red-tape  (2026-11-21)

## Corpus Check
- 105 files · ~44,081 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 568 nodes · 951 edges · 48 communities (32 shown, 16 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 27 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fb8c1f55`
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
- land_possession_self_declaration.md
- research_engine.py
- test_pipeline.py
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
- workflow.py
- demo_server.py
- interview_engine.py
- Application Review Package: I want to open a small bakery in Park Circus, Kolkata with 5 counter seats
- Application Review Package: I want to open a small bakery in Park Circus, Kolkata with 5 counter seats
- Portal Submission Pack: FoSCoS FSSAI Basic Food Registration (Form A)
- Portal Submission Pack: KMC Certificate of Enlistment (Trade License)
- Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B)
- Portal Submission Pack: FoSCoS FSSAI Basic Food Registration (Form A)
- Portal Submission Pack: KMC Certificate of Enlistment (Trade License)
- Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B)
- food_safety_hygiene_declaration.md
- landlord_noc_template.md
- proj_business_i_want_to_open_a_small_baker_202611201605/draft_food_hygiene_declaration.md
- proj_business_i_want_to_open_a_small_baker_202611201605/draft_landlord_noc.md
- test_thread_bakery_hitl/draft_food_hygiene_declaration.md
- test_thread_bakery_hitl/draft_landlord_noc.md
- structural_stability_declaration.md
- Portal Submission Pack: FoSCoS FSSAI Basic Food Registration (Form A)
- Portal Submission Pack: KMC Certificate of Enlistment (Trade License)
- Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B)
- demo_bakery_kolkata/draft_landlord_noc.md
- Portal Submission Pack: Bidhannagar Municipal Corporation (BMC) Building Sanction
- draft_structural_stability.md

## God Nodes (most connected - your core abstractions)
1. `load_json()` - 26 edges
2. `save_json()` - 22 edges
3. `effective_value()` - 19 edges
4. `LiveDemoState` - 16 edges
5. `is_blank()` - 16 edges
6. `build_workflow()` - 16 edges
7. `RedTape Navigator Unified Skill` - 15 edges
8. `RedTapeState` - 13 edges
9. `generate_documents()` - 13 edges
10. `validate()` - 11 edges

## Surprising Connections (you probably didn't know these)
- `start_test_server()` --uses--> `DemoServerHandler`  [INFERRED]
  redtape-navigator-unified/scripts/test_phase7_server_orchestration.py → demo_server.py
- `node_orchestrator()` --calls--> `parse_intent()`  [INFERRED]
  redtape-navigator-unified/workflow.py → redtape-navigator-unified/scripts/orchestrator_parser.py
- `node_documents()` --calls--> `generate_documents()`  [INFERRED]
  redtape-navigator-unified/workflow.py → redtape-navigator-unified/scripts/document_engine.py
- `node_interview()` --calls--> `generate_question_batch()`  [INFERRED]
  redtape-navigator-unified/workflow.py → redtape-navigator-unified/scripts/interview_engine.py
- `node_interview()` --calls--> `process_user_answer()`  [INFERRED]
  redtape-navigator-unified/workflow.py → redtape-navigator-unified/scripts/interview_engine.py

## Import Cycles
- None detected.

## Communities (48 total, 16 thin omitted)

### Community 0 - "_common.py"
Cohesion: 0.10
Nodes (35): apply_transform(), effective_value(), get_path(), inr_to_indian_words(), is_blank(), load_json(), mask(), need() (+27 more)

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
Cohesion: 0.04
Nodes (46): type, description, type, type, properties, type, properties, type (+38 more)

### Community 10 - "research_engine.py"
Cohesion: 0.08
Nodes (17): catalog_supporting_documents(), compliance(), evaluate_with_gemini(), main(), make_state(), find_api_key(), main(), parse_intent() (+9 more)

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

### Community 23 - "workflow.py"
Cohesion: 0.10
Nodes (18): main(), http_get(), http_post(), main(), start_test_server(), test_langgraph_routing_and_structure(), test_server_endpoints(), build_workflow() (+10 more)

### Community 24 - "demo_server.py"
Cohesion: 0.16
Nodes (3): DemoServerHandler, LiveDemoState, render_ui_html()

### Community 25 - "interview_engine.py"
Cohesion: 0.16
Nodes (10): call_gemini_interview(), generate_fallback_question(), generate_question_batch(), interview_turn(), is_pii_field(), main(), parse_fallback_answer(), process_user_answer() (+2 more)

### Community 26 - "Application Review Package: I want to open a small bakery in Park Circus, Kolkata with 5 counter seats"
Cohesion: 0.25
Nodes (7): 1. Compliance Matrix, 2. Audit Trail & Rule Reasoning, 3. Conflicts & System Notices, 4. Filled PDF Drafts & Digital Portal Packs, 5. Supporting Document Checklist, 6. Submission Readiness, Application Review Package: I want to open a small bakery in Park Circus, Kolkata with 5 counter seats

### Community 27 - "Application Review Package: I want to open a small bakery in Park Circus, Kolkata with 5 counter seats"
Cohesion: 0.25
Nodes (7): 1. Compliance Matrix, 2. Audit Trail & Rule Reasoning, 3. Conflicts & System Notices, 4. Filled PDF Drafts & Digital Portal Packs, 5. Supporting Document Checklist, 6. Submission Readiness, Application Review Package: I want to open a small bakery in Park Circus, Kolkata with 5 counter seats

### Community 28 - "Portal Submission Pack: FoSCoS FSSAI Basic Food Registration (Form A)"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: FoSCoS FSSAI Basic Food Registration (Form A), Required Portal Uploads, Step 1: Applicant & Premises Details, Step 2: Kind of Business & Turnover

### Community 29 - "Portal Submission Pack: KMC Certificate of Enlistment (Trade License)"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: KMC Certificate of Enlistment (Trade License), Required Portal Uploads, Step 1: Location & Premises Identification, Step 2: Business & Applicant Profile

### Community 30 - "Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B)"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B), Required Portal Uploads, Step 1: Establishment Particulars, Step 2: Employment & Employer

### Community 31 - "Portal Submission Pack: FoSCoS FSSAI Basic Food Registration (Form A)"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: FoSCoS FSSAI Basic Food Registration (Form A), Required Portal Uploads, Step 1: Applicant & Premises Details, Step 2: Kind of Business & Turnover

### Community 32 - "Portal Submission Pack: KMC Certificate of Enlistment (Trade License)"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: KMC Certificate of Enlistment (Trade License), Required Portal Uploads, Step 1: Location & Premises Identification, Step 2: Business & Applicant Profile

### Community 33 - "Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B)"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B), Required Portal Uploads, Step 1: Establishment Particulars, Step 2: Employment & Employer

### Community 42 - "Portal Submission Pack: FoSCoS FSSAI Basic Food Registration (Form A)"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: FoSCoS FSSAI Basic Food Registration (Form A), Required Portal Uploads, Step 1: Applicant & Premises Details, Step 2: Kind of Business & Turnover

### Community 43 - "Portal Submission Pack: KMC Certificate of Enlistment (Trade License)"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: KMC Certificate of Enlistment (Trade License), Required Portal Uploads, Step 1: Location & Premises Identification, Step 2: Business & Applicant Profile

### Community 44 - "Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B)"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B), Required Portal Uploads, Step 1: Establishment Particulars, Step 2: Employment & Employer

### Community 46 - "Portal Submission Pack: Bidhannagar Municipal Corporation (BMC) Building Sanction"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: Bidhannagar Municipal Corporation (BMC) Building Sanction, Required Portal Uploads, Step 1: Plot & Location Particulars, Step 2: Proposed Construction Details

## Knowledge Gaps
- **19 isolated node(s):** `Problem Statement`, `India Agricultural Grants Jurisdiction`, `India Food Business Jurisdiction`, `India Residential Zoning Jurisdiction`, `Compliance System Prompt` (+14 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 299 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `properties` connect `properties` to `$ref`, `properties`, `type`, `properties`, `properties`, `project_state.json`, `provenance`, `created_at`, `domain`, `overrides`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **What connects `Problem Statement`, `India Agricultural Grants Jurisdiction`, `India Food Business Jurisdiction` to the rest of the system?**
  _19 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `_common.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09984639016897082 - nodes in this community are weakly interconnected._
- **Why does `applicant_profile` connect `properties` to `properties`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Should `properties` be split into smaller, more focused modules?**
  _Cohesion score 0.048625792811839326 - nodes in this community are weakly interconnected._
- **Should `properties` be split into smaller, more focused modules?**
  _Cohesion score 0.06451612903225806 - nodes in this community are weakly interconnected._
- **Should `properties` be split into smaller, more focused modules?**
  _Cohesion score 0.08 - nodes in this community are weakly interconnected._