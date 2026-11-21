# Graph Report - red-tape  (2026-11-21)

## Corpus Check
- 172 files · ~90,837 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: .ico 4, (none) 2, .example 1)

## Summary
- 910 nodes · 1525 edges · 81 communities (52 shown, 29 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 30 edges (avg confidence: 0.85)
- Token cost: 29,931 input · 1,939 output

## Graph Freshness
- Built from commit: `ed114b8b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- postgres_db.py
- os
- Applicant Profile Schema
- Compliance Matrix Schema
- Workflow Orchestration Testing
- Portal Artifact Schema
- interview_engine_v2.py
- Form Artifact Schema
- AI Agent Skills
- Workflow State Flags
- Schema References
- Validation Results Schema
- Project Configuration Schema
- Research and Findings
- Bakery Application Review
- HITL Application Review
- PDF Form Templates
- FSSAI Registration Pack
- KMC Trade License
- SilpaSathi Registration Pack
- BMC Building Sanction
- Bakery FSSAI Pack
- Bakery KMC License
- Bakery SilpaSathi Pack
- HITL FSSAI Pack
- HITL KMC License
- HITL SilpaSathi Pack
- Project State Schema
- FSSAI_Form_A_Official.pdf
- Data Provenance Schema
- Metadata Fields
- research_engine.py
- start_tunnel.py
- Landlord NOC Documents
- Structural Stability Documents
- Food Safety Declaration
- Land Possession Declaration
- Landlord NOC Template
- Structural Stability Template
- Bakery Landlord NOC
- Structural Stability Draft
- Bakery Hygiene Declaration
- Bakery Landlord NOC
- HITL Hygiene Declaration
- HITL Landlord NOC
- Hygiene Declaration Template
- Land Possession Template
- Sunrise Bakery FSSAI
- Sunrise Bakery KMC
- Sunrise Bakery SilpaSathi
- Building Sanction Pack
- Bakery Review Package
- Portal Submission Pack: KMC Certificate of Enlistment (Trade License)
- Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B)
- Project Documentation
- Agricultural Jurisdictions
- Food Business Jurisdictions
- Zoning Jurisdictions
- Brand Identity
- Portal Submission Pack: KMC Certificate of Enlistment (Trade License)
- Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B)
- demo_bakery_kolkata/draft_food_hygiene_declaration.md
- demo_clothes_barrackpore/draft_landlord_noc.md
- demo_stationery_sodpur/draft_landlord_noc.md
- memory_engine.py
- json
- call_ollama
- build.js
- Portal Submission Pack: FoSCoS FSSAI Basic Food Registration (Form A)
- Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B)
- vercel.json
- benchmark_test/draft_landlord_noc.md
- demo_server.py
- scripts/ollama_client.py
- compliance_engine.py
- 🏛️ RedTape Navigator
- interview_engine.py
- domain
- overrides
- package.json

## God Nodes (most connected - your core abstractions)
1. `RedTapeSession` - 36 edges
2. `load_json()` - 30 edges
3. `save_json()` - 23 edges
4. `call_ollama()` - 20 edges
5. `effective_value()` - 20 edges
6. `is_blank()` - 17 edges
7. `build_workflow()` - 16 edges
8. `RedTape Navigator Unified Skill` - 15 edges
9. `RedTapeState` - 13 edges
10. `RedTapeHTTPHandler` - 12 edges

## Surprising Connections (you probably didn't know these)
- `benchmark_run()` --calls--> `generate_documents()`  [INFERRED]
  benchmark_pipeline_ollama.py → redtape-navigator-unified/scripts/document_engine.py
- `generate_regulatory_briefing_markdown()` --calls--> `has_offline_official_pdf()`  [INFERRED]
  interview_engine_v2.py → redtape-navigator-unified/scripts/document_engine.py
- `generate_completed_filing_markdown()` --calls--> `has_offline_official_pdf()`  [INFERRED]
  interview_engine_v2.py → redtape-navigator-unified/scripts/document_engine.py
- `evaluate_with_gemini()` --calls--> `call_ollama()`  [EXTRACTED]
  redtape-navigator-unified/scripts/compliance_engine.py → ollama_client.py
- `call_gemini_interview()` --calls--> `call_ollama()`  [EXTRACTED]
  redtape-navigator-unified/scripts/interview_engine.py → ollama_client.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Bakery Compliance Flow (Kolkata)** — drafts_demo_bakery_kolkata_foscos_pack, drafts_demo_bakery_kolkata_kmc_trade_license_pack, drafts_demo_bakery_kolkata_silpasathi_pack [INFERRED 0.90]
- **BMC Building Sanction Flow** — drafts_demo_zoning_extension_bmc_building_plan_pack, drafts_demo_zoning_extension_draft_structural_stability [INFERRED 0.90]

## Communities (81 total, 29 thin omitted)

### Community 0 - "postgres_db.py"
Cohesion: 0.12
Nodes (9): add_message(), _bg_worker(), clear_all_chat_history(), get_connection(), _get_database_url(), get_session_details(), init_db(), list_sessions() (+1 more)

### Community 1 - "os"
Cohesion: 0.07
Nodes (42): apply_transform(), effective_value(), get_path(), inr_to_indian_words(), is_blank(), load_json(), mask(), need() (+34 more)

### Community 2 - "Applicant Profile Schema"
Cohesion: 0.04
Nodes (46): type, description, type, type, properties, type, properties, type (+38 more)

### Community 3 - "Compliance Matrix Schema"
Cohesion: 0.05
Nodes (43): type, items, type, items, type, type, items, type (+35 more)

### Community 4 - "Workflow Orchestration Testing"
Cohesion: 0.11
Nodes (18): main(), http_get(), http_post(), main(), start_test_server(), test_langgraph_routing_and_structure(), test_server_endpoints(), build_workflow() (+10 more)

### Community 5 - "Portal Artifact Schema"
Cohesion: 0.06
Nodes (31): maximum, minimum, type, type, description, items, type, type (+23 more)

### Community 6 - "interview_engine_v2.py"
Cohesion: 0.06
Nodes (22): analyze_citizen_goal(), build_dynamic_statutory_matrix(), call_ollama_json(), call_ollama_local(), extract_location_heuristics(), generate_completed_filing_markdown(), generate_regulatory_briefing_markdown(), get_ollama_model() (+14 more)

### Community 7 - "Form Artifact Schema"
Cohesion: 0.08
Nodes (24): maximum, minimum, type, type, type, type, type, items (+16 more)

### Community 8 - "AI Agent Skills"
Cohesion: 0.09
Nodes (22): Compliance Agent Skill, Document Agent Skill, Interview Agent Skill, Orchestrator Agent Skill, Research Agent Skill, Validation Agent Skill, Compliance System Prompt, Document System Prompt (+14 more)

### Community 9 - "Workflow State Flags"
Cohesion: 0.10
Nodes (20): type, type, type, type, minimum, type, compliance_complete, compliance_needs_reeval (+12 more)

### Community 10 - "Schema References"
Cohesion: 0.20
Nodes (10): items, type, items, type, $ref, items, type, compliance_matrix (+2 more)

### Community 11 - "Validation Results Schema"
Cohesion: 0.20
Nodes (10): items, type, type, errors, passed, timestamp, validation, type (+2 more)

### Community 12 - "Project Configuration Schema"
Cohesion: 0.20
Nodes (10): type, default, type, type, properties, goal, preferred_language, project_id (+2 more)

### Community 13 - "Research and Findings"
Cohesion: 0.20
Nodes (10): type, items, type, open_questions, research_findings, warnings, items, type (+2 more)

### Community 14 - "Bakery Application Review"
Cohesion: 0.25
Nodes (7): 1. Compliance Matrix, 2. Audit Trail & Rule Reasoning, 3. Conflicts & System Notices, 4. Filled PDF Drafts & Digital Portal Packs, 5. Supporting Document Checklist, 6. Submission Readiness, Application Review Package: I want to open a small bakery in Park Circus, Kolkata with 5 counter seats

### Community 15 - "HITL Application Review"
Cohesion: 0.25
Nodes (7): 1. Compliance Matrix, 2. Audit Trail & Rule Reasoning, 3. Conflicts & System Notices, 4. Filled PDF Drafts & Digital Portal Packs, 5. Supporting Document Checklist, 6. Submission Readiness, Application Review Package: small bakery

### Community 16 - "PDF Form Templates"
Cohesion: 0.15
Nodes (3): build_all(), build_official_wb_form_j(), _create_pdf_and_map()

### Community 17 - "FSSAI Registration Pack"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: FoSCoS FSSAI Basic Food Registration (Form A), Required Portal Uploads, Step 1: Applicant & Premises Details, Step 2: Kind of Business & Turnover

### Community 18 - "KMC Trade License"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: KMC Certificate of Enlistment (Trade License), Required Portal Uploads, Step 1: Location & Premises Identification, Step 2: Business & Applicant Profile

### Community 19 - "SilpaSathi Registration Pack"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B), Required Portal Uploads, Step 1: Establishment Particulars, Step 2: Employment & Employer

### Community 20 - "BMC Building Sanction"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: Bidhannagar Municipal Corporation (BMC) Building Sanction, Required Portal Uploads, Step 1: Plot & Location Particulars, Step 2: Proposed Construction Details

### Community 21 - "Bakery FSSAI Pack"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: FoSCoS FSSAI Basic Food Registration (Form A), Required Portal Uploads, Step 1: Applicant & Premises Details, Step 2: Kind of Business & Turnover

### Community 22 - "Bakery KMC License"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: KMC Certificate of Enlistment (Trade License), Required Portal Uploads, Step 1: Location & Premises Identification, Step 2: Business & Applicant Profile

### Community 23 - "Bakery SilpaSathi Pack"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B), Required Portal Uploads, Step 1: Establishment Particulars, Step 2: Employment & Employer

### Community 24 - "HITL FSSAI Pack"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: FoSCoS FSSAI Basic Food Registration (Form A), Required Portal Uploads, Step 1: Applicant & Premises Details, Step 2: Kind of Business & Turnover

### Community 25 - "HITL KMC License"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: KMC Certificate of Enlistment (Trade License), Required Portal Uploads, Step 1: Location & Premises Identification, Step 2: Business & Applicant Profile

### Community 26 - "HITL SilpaSathi Pack"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B), Required Portal Uploads, Step 1: Establishment Particulars, Step 2: Employment & Employer

### Community 27 - "Project State Schema"
Cohesion: 0.33
Nodes (5): description, required, $schema, title, type

### Community 28 - "FSSAI_Form_A_Official.pdf"
Cohesion: 0.04
Nodes (45): FSSAI_Form_A_Official.pdf, bytes, has_text, height, ok, pages, sample_text, widgets (+37 more)

### Community 29 - "Data Provenance Schema"
Cohesion: 0.50
Nodes (4): type, provenance, additionalProperties, type

### Community 30 - "Metadata Fields"
Cohesion: 0.67
Nodes (3): format, type, created_at

### Community 31 - "research_engine.py"
Cohesion: 0.12
Nodes (13): build_search_queries(), call_gemini_research(), find_serpapi_key(), get_cache(), get_jurisdiction_baseline_findings(), _is_book_activity(), _is_flammable_activity(), _is_food_activity() (+5 more)

### Community 32 - "start_tunnel.py"
Cohesion: 0.26
Nodes (5): main(), run(), get_ngrok_public_url(), is_port_in_use(), main()

### Community 52 - "Portal Submission Pack: KMC Certificate of Enlistment (Trade License)"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: KMC Certificate of Enlistment (Trade License), Required Portal Uploads, Step 1: Location & Premises Identification, Step 2: Business & Applicant Profile

### Community 53 - "Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B)"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B), Required Portal Uploads, Step 1: Establishment Particulars, Step 2: Employment & Employer

### Community 59 - "Portal Submission Pack: KMC Certificate of Enlistment (Trade License)"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: KMC Certificate of Enlistment (Trade License), Required Portal Uploads, Step 1: Location & Premises Identification, Step 2: Business & Applicant Profile

### Community 60 - "Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B)"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B), Required Portal Uploads, Step 1: Establishment Particulars, Step 2: Employment & Employer

### Community 64 - "memory_engine.py"
Cohesion: 0.19
Nodes (7): generate_embedding_768(), get_citizen_profile(), get_connection(), get_db_url(), search_citizen_memory(), store_citizen_memory(), vector_to_sql_str()

### Community 65 - "json"
Cohesion: 0.20
Nodes (3): download_all(), write_maps(), post()

### Community 66 - "call_ollama"
Cohesion: 0.21
Nodes (6): benchmark_run(), call_ollama(), get_active_model(), set_active_model(), test_local_ollama(), test_server_endpoints()

### Community 67 - "build.js"
Cohesion: 0.20
Nodes (7): favSrc, fs, indexPath, path, PUBLIC_DIR, PUBLIC_STATIC, STATIC_SRC

### Community 69 - "Portal Submission Pack: FoSCoS FSSAI Basic Food Registration (Form A)"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: FoSCoS FSSAI Basic Food Registration (Form A), Required Portal Uploads, Step 1: Applicant & Premises Details, Step 2: Kind of Business & Turnover

### Community 70 - "Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B)"
Cohesion: 0.33
Nodes (5): Human-Only Gates (Agent Stops Here), Portal Submission Pack: SilpaSathi West Bengal Shops & Establishments (Form B), Required Portal Uploads, Step 1: Establishment Particulars, Step 2: Employment & Employer

### Community 71 - "vercel.json"
Cohesion: 0.40
Nodes (4): cleanUrls, outputDirectory, rewrites, trailingSlash

### Community 127 - "demo_server.py"
Cohesion: 0.08
Nodes (16): get_user_from_auth_header(), get_user_from_cookie(), get_user_from_request(), _hash_pw(), _load_users(), login(), logout(), _save_users() (+8 more)

### Community 133 - "scripts/ollama_client.py"
Cohesion: 0.29
Nodes (3): call_ollama(), get_active_model(), set_active_model()

### Community 134 - "compliance_engine.py"
Cohesion: 0.18
Nodes (6): catalog_supporting_documents(), compliance(), evaluate_with_gemini(), find_api_key(), main(), parse_intent()

### Community 136 - "🏛️ RedTape Navigator"
Cohesion: 0.11
Nodes (17): 1. Clone the Repository, 1. Run the Comprehensive End-to-End Verification Test, 2. Create and Activate a Virtual Environment, 2. Start the Live Interactive Web Application, 3. Install Dependencies, 4. Configure Environment Variables, 🏗️ Architecture & Multi-Agent Flow, 💻 Cross-Platform Quickstart Guide (+9 more)

### Community 140 - "interview_engine.py"
Cohesion: 0.15
Nodes (11): call_gemini_interview(), generate_fallback_question(), generate_question_batch(), interview_turn(), is_pii_field(), main(), parse_fallback_answer(), process_user_answer() (+3 more)

### Community 142 - "domain"
Cohesion: 0.67
Nodes (3): enum, type, domain

### Community 143 - "overrides"
Cohesion: 0.67
Nodes (3): additionalProperties, type, overrides

### Community 148 - "package.json"
Cohesion: 0.13
Nodes (14): dependencies, @neon/auth@^0.8.2, @neon/config@^1.14.6, @neon/env@^2.1.9, description, name, scripts, build (+6 more)

## Knowledge Gaps
- **31 isolated node(s):** `Problem Statement`, `India Agricultural Grants Jurisdiction`, `India Food Business Jurisdiction`, `India Residential Zoning Jurisdiction`, `Compliance System Prompt` (+26 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 489 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RedTapeSession` connect `interview_engine_v2.py` to `call_ollama`, `demo_server.py`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **What connects `Problem Statement`, `India Agricultural Grants Jurisdiction`, `India Food Business Jurisdiction` to the rest of the system?**
  _31 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `postgres_db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11688311688311688 - nodes in this community are weakly interconnected._
- **Why does `properties` connect `Project Configuration Schema` to `Applicant Profile Schema`, `Workflow State Flags`, `Schema References`, `Validation Results Schema`, `Research and Findings`, `domain`, `overrides`, `Project State Schema`, `Data Provenance Schema`, `Metadata Fields`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Should `os` be split into smaller, more focused modules?**
  _Cohesion score 0.075 - nodes in this community are weakly interconnected._
- **Should `Applicant Profile Schema` be split into smaller, more focused modules?**
  _Cohesion score 0.043478260869565216 - nodes in this community are weakly interconnected._
- **Should `Compliance Matrix Schema` be split into smaller, more focused modules?**
  _Cohesion score 0.048625792811839326 - nodes in this community are weakly interconnected._