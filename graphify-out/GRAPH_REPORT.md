# Graph Report - red-tape  (2026-11-21)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 582 nodes · 953 edges · 59 communities (31 shown, 28 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 27 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `037f723f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- research_engine.py
- _common.py
- properties
- properties
- workflow.py
- properties
- LiveDemoState
- properties
- RedTape Navigator Unified Skill
- properties
- $ref
- properties
- properties
- type
- Application Review Package: I want to open a small bakery in Park Circus, Kolkata with 5 counter seats
- Application Review Package: I want to open a small bakery in Park Circus, Kolkata with 5 counter seats
- Portal Submission Pack: FoSCoS FSSAI Basic Food Registration (Form A)
- Portal Submission Pack: KMC Certificate of Enlistment (Trade License)
- Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B)
- Portal Submission Pack: Bidhannagar Municipal Corporation (BMC) Building Sanction
- Portal Submission Pack: FoSCoS FSSAI Basic Food Registration (Form A)
- Portal Submission Pack: KMC Certificate of Enlistment (Trade License)
- Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B)
- Portal Submission Pack: FoSCoS FSSAI Basic Food Registration (Form A)
- Portal Submission Pack: KMC Certificate of Enlistment (Trade License)
- Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B)
- project_state.json
- test_pipeline.py
- provenance
- created_at
- domain
- overrides
- Landlord NOC Template
- Structural Stability Declaration Template
- food_safety_hygiene_declaration.md
- land_possession_self_declaration.md
- landlord_noc_template.md
- structural_stability_declaration.md
- demo_bakery_kolkata/draft_landlord_noc.md
- draft_structural_stability.md
- proj_business_i_want_to_open_a_small_baker_202611201605/draft_food_hygiene_declaration.md
- proj_business_i_want_to_open_a_small_baker_202611201605/draft_landlord_noc.md
- test_thread_bakery_hitl/draft_food_hygiene_declaration.md
- test_thread_bakery_hitl/draft_landlord_noc.md
- Food Safety Hygiene Declaration Template
- Land Possession Self-Declaration Template
- FoSCoS Portal Pack (Sunrise Bakery)
- KMC Trade License Pack (Sunrise Bakery)
- SilpaSathi Portal Pack (Sunrise Bakery)
- BMC Building Sanction Pack (Priyanka Roy)
- Application Review Package (Park Circus Bakery)
- RedTape AI Emblem
- RedTape AI Full Logo with Tagline
- Problem Statement
- India Agricultural Grants Jurisdiction
- India Food Business Jurisdiction
- India Residential Zoning Jurisdiction
- RedTape AI Full Logo

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
- `main()` --calls--> `build_workflow()`  [EXTRACTED]
  redtape-navigator-unified/scripts/test_langgraph_hitl.py → redtape-navigator-unified/workflow.py
- `test_dynamic_overrides_and_audit_trail()` --calls--> `compliance()`  [EXTRACTED]
  redtape-navigator-unified/scripts/test_phase6_review_overrides.py → redtape-navigator-unified/scripts/compliance_engine.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Bakery Compliance Flow (Kolkata)** — drafts_demo_bakery_kolkata_foscos_pack, drafts_demo_bakery_kolkata_kmc_trade_license_pack, drafts_demo_bakery_kolkata_silpasathi_pack [INFERRED 0.90]
- **BMC Building Sanction Flow** — drafts_demo_zoning_extension_bmc_building_plan_pack, drafts_demo_zoning_extension_draft_structural_stability [INFERRED 0.90]

## Communities (59 total, 28 thin omitted)

### Community 0 - "research_engine.py"
Cohesion: 0.06
Nodes (27): catalog_supporting_documents(), compliance(), evaluate_deterministic(), evaluate_with_gemini(), call_gemini_interview(), generate_fallback_question(), generate_question_batch(), interview_turn() (+19 more)

### Community 1 - "_common.py"
Cohesion: 0.09
Nodes (37): apply_transform(), effective_value(), get_path(), inr_to_indian_words(), is_blank(), load_json(), mask(), need() (+29 more)

### Community 2 - "properties"
Cohesion: 0.04
Nodes (46): type, description, type, type, properties, type, properties, type (+38 more)

### Community 3 - "properties"
Cohesion: 0.05
Nodes (43): type, items, type, items, type, type, items, type (+35 more)

### Community 4 - "workflow.py"
Cohesion: 0.12
Nodes (16): http_get(), http_post(), main(), start_test_server(), test_langgraph_routing_and_structure(), test_server_endpoints(), build_workflow(), node_compliance() (+8 more)

### Community 5 - "properties"
Cohesion: 0.06
Nodes (31): maximum, minimum, type, type, description, items, type, type (+23 more)

### Community 6 - "LiveDemoState"
Cohesion: 0.16
Nodes (3): DemoServerHandler, LiveDemoState, render_ui_html()

### Community 7 - "properties"
Cohesion: 0.08
Nodes (24): maximum, minimum, type, type, type, type, type, items (+16 more)

### Community 8 - "RedTape Navigator Unified Skill"
Cohesion: 0.09
Nodes (22): Compliance Agent Skill, Document Agent Skill, Interview Agent Skill, Orchestrator Agent Skill, Research Agent Skill, Validation Agent Skill, Compliance System Prompt, Document System Prompt (+14 more)

### Community 9 - "properties"
Cohesion: 0.10
Nodes (20): type, type, type, type, minimum, type, compliance_complete, compliance_needs_reeval (+12 more)

### Community 10 - "$ref"
Cohesion: 0.20
Nodes (10): items, type, items, type, $ref, items, type, compliance_matrix (+2 more)

### Community 11 - "properties"
Cohesion: 0.20
Nodes (10): items, type, type, errors, passed, timestamp, validation, type (+2 more)

### Community 12 - "properties"
Cohesion: 0.20
Nodes (10): type, default, type, type, properties, goal, preferred_language, project_id (+2 more)

### Community 13 - "type"
Cohesion: 0.20
Nodes (10): type, items, type, open_questions, research_findings, warnings, items, type (+2 more)

### Community 14 - "Application Review Package: I want to open a small bakery in Park Circus, Kolkata with 5 counter seats"
Cohesion: 0.25
Nodes (7): 1. Compliance Matrix, 2. Audit Trail & Rule Reasoning, 3. Conflicts & System Notices, 4. Filled PDF Drafts & Digital Portal Packs, 5. Supporting Document Checklist, 6. Submission Readiness, Application Review Package: I want to open a small bakery in Park Circus, Kolkata with 5 counter seats

### Community 15 - "Application Review Package: I want to open a small bakery in Park Circus, Kolkata with 5 counter seats"
Cohesion: 0.25
Nodes (7): 1. Compliance Matrix, 2. Audit Trail & Rule Reasoning, 3. Conflicts & System Notices, 4. Filled PDF Drafts & Digital Portal Packs, 5. Supporting Document Checklist, 6. Submission Readiness, Application Review Package: I want to open a small bakery in Park Circus, Kolkata with 5 counter seats

### Community 17 - "Portal Submission Pack: FoSCoS FSSAI Basic Food Registration (Form A)"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: FoSCoS FSSAI Basic Food Registration (Form A), Required Portal Uploads, Step 1: Applicant & Premises Details, Step 2: Kind of Business & Turnover

### Community 18 - "Portal Submission Pack: KMC Certificate of Enlistment (Trade License)"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: KMC Certificate of Enlistment (Trade License), Required Portal Uploads, Step 1: Location & Premises Identification, Step 2: Business & Applicant Profile

### Community 19 - "Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B)"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B), Required Portal Uploads, Step 1: Establishment Particulars, Step 2: Employment & Employer

### Community 20 - "Portal Submission Pack: Bidhannagar Municipal Corporation (BMC) Building Sanction"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: Bidhannagar Municipal Corporation (BMC) Building Sanction, Required Portal Uploads, Step 1: Plot & Location Particulars, Step 2: Proposed Construction Details

### Community 21 - "Portal Submission Pack: FoSCoS FSSAI Basic Food Registration (Form A)"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: FoSCoS FSSAI Basic Food Registration (Form A), Required Portal Uploads, Step 1: Applicant & Premises Details, Step 2: Kind of Business & Turnover

### Community 22 - "Portal Submission Pack: KMC Certificate of Enlistment (Trade License)"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: KMC Certificate of Enlistment (Trade License), Required Portal Uploads, Step 1: Location & Premises Identification, Step 2: Business & Applicant Profile

### Community 23 - "Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B)"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B), Required Portal Uploads, Step 1: Establishment Particulars, Step 2: Employment & Employer

### Community 24 - "Portal Submission Pack: FoSCoS FSSAI Basic Food Registration (Form A)"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: FoSCoS FSSAI Basic Food Registration (Form A), Required Portal Uploads, Step 1: Applicant & Premises Details, Step 2: Kind of Business & Turnover

### Community 25 - "Portal Submission Pack: KMC Certificate of Enlistment (Trade License)"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: KMC Certificate of Enlistment (Trade License), Required Portal Uploads, Step 1: Location & Premises Identification, Step 2: Business & Applicant Profile

### Community 26 - "Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B)"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B), Required Portal Uploads, Step 1: Establishment Particulars, Step 2: Employment & Employer

### Community 27 - "project_state.json"
Cohesion: 0.33
Nodes (5): description, required, $schema, title, type

### Community 29 - "provenance"
Cohesion: 0.50
Nodes (4): type, provenance, additionalProperties, type

### Community 30 - "created_at"
Cohesion: 0.67
Nodes (3): format, type, created_at

### Community 31 - "domain"
Cohesion: 0.67
Nodes (3): enum, type, domain

### Community 32 - "overrides"
Cohesion: 0.67
Nodes (3): additionalProperties, type, overrides

## Knowledge Gaps
- **33 isolated node(s):** `Problem Statement`, `India Agricultural Grants Jurisdiction`, `India Food Business Jurisdiction`, `India Residential Zoning Jurisdiction`, `Compliance System Prompt` (+28 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 313 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `properties` connect `properties` to `overrides`, `properties`, `properties`, `$ref`, `properties`, `type`, `project_state.json`, `provenance`, `created_at`, `domain`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **What connects `Problem Statement`, `India Agricultural Grants Jurisdiction`, `India Food Business Jurisdiction` to the rest of the system?**
  _33 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `research_engine.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05517503805175038 - nodes in this community are weakly interconnected._
- **Why does `applicant_profile` connect `properties` to `properties`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Should `_common.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08853118712273642 - nodes in this community are weakly interconnected._
- **Should `properties` be split into smaller, more focused modules?**
  _Cohesion score 0.043478260869565216 - nodes in this community are weakly interconnected._
- **Should `properties` be split into smaller, more focused modules?**
  _Cohesion score 0.048625792811839326 - nodes in this community are weakly interconnected._