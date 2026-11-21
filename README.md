# 🏛️ RedTape Navigator

**Autonomous Bureaucratic & Statutory Compliance AI Agent**  
*Navigating Complex Indian Statutory Approvals, Municipal Enlistments, and Portal Filings with Zero Hallucination.*

---

## 🌟 Overview

Starting or expanding a physical business in India involves wading through dense, opaque bureaucratic requirements across central, state, and municipal jurisdictions. A single shop in Kolkata may require simultaneous approvals from the **Kolkata Municipal Corporation (KMC)**, **West Bengal Labour Department (SilpaSathi)**, **Food Safety and Standards Authority of India (FoSCoS)**, **West Bengal Fire and Emergency Services**, **State Directorate of Commercial Taxes (P-Tax)**, and the **Ministry of MSME**.

**RedTape Navigator** is an enterprise-grade, multi-agent AI system powered by local open weights (**Ollama `llama3.1:8b`**), backed by **Neon Lakebase PostgreSQL** and fully observable via **Langfuse**. It conducts an interactive, zero-fabrication interview with the citizen, dynamically maps all required statutory permits, auto-fills official AcroForm PDF applications, generates digital web portal submission packs, and mathematically validates cross-document consistency invariants.

---

## 🏗️ Architecture & Multi-Agent Flow

```
                      +-----------------------------+
                      |   Citizen / Web Interface   |
                      |   (Claude 3.5 Sonnet UI)    |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |     Orchestrator Agent      |
                      |  (interview_engine_v2.py)   |
                      +--------------+--------------+
                                     |
      +------------------------------+------------------------------+
      |                              |                              |
      v                              v                              v
+---------------+             +---------------+             +---------------+
| Research Tier |             |  Compliance   |             | Citizen Memory|
| 1. Verified KB|             |    Engine     |             | & Profile DB  |
| 2. Web Search |             | (Matrix Calc) |             | (Neon Postgres|
| 3. Portal Map |             +-------+-------+             |   + pgvector) |
+-------+-------+                     |                     +---------------+
        |                             v                             |
        +-------------------->+---------------+<--------------------+
                              |Document Engine|
                              | 1. AcroForm   |
                              |    PDF Filler |
                              | 2. Web Portal |
                              |    Manifests  |
                              +-------+-------+
                                      |
                                      v
                              +---------------+
                              |  Validation   |
                              |     Agent     |
                              |  (Invariants) |
                              +-------+-------+
                                      |
                                      v
                      +-------------------------------+
                      | Langfuse Observability Tracing|
                      |  & Downloadable Form Artifacts|
                      +-------------------------------+
```

### Key Components

1. **Interactive Conversational Interviewer**: Asks only targeted, essential questions (turnover, floor area, staff count, premises type, fuel usage) based on unstated fields. Zero guesswork or made-up figures.
2. **Deterministic Research & Compliance Engine**: Evaluates statutory rules against the applicant profile across 9+ regulatory frameworks:
   - KMC Section 199 Certificate of Enlistment (Trade License)
   - WB Municipal Act 1993 Form J (Panihati, Barrackpore, etc.)
   - WB Shops & Establishments Act 1963 (Form B Registration)
   - FSSAI Food Safety Registration (Form A) & State License (Form B)
   - WB Fire Services Act 1950 (Form V NOC & Textile Fire Safety Declarations)
   - WB State Tax on Professions, Trades & Callings (Form II P-Tax)
   - Central GST Registration (Rule 8(1) Form GST REG-01)
   - Ministry of MSME Udyam Registration
3. **Document & PDF Filling Engine**: Injects normalized profile data into official AcroForm PDFs (`pypdf` / `fitz`) and synthesizes markdown portal submission manifests with copy-paste readiness.
4. **Validation Agent**: Enforces strict invariants: name consistency, PAN format, premise matching, turnover thresholds, and fee calculations.
5. **Persistence & Scalability**: Backed by **Neon PostgreSQL** for conversation history, session state, and citizen profile memory with cold-start resilient connection pooling.
6. **Observability**: Live multi-agent tracing dispatched to **Langfuse** capturing reasoning traces, tool inputs, latency, and token throughput.

---

## 💻 Cross-Platform Quickstart Guide

RedTape Navigator is fully compatible with **Windows (10/11)**, **macOS**, and **Linux**.

### Prerequisites

1. **Python 3.10+** installed:
   - *Windows*: Ensure **"Add Python to PATH"** is checked during installation.
2. **Ollama** installed and running locally:
   - Download from [ollama.com](https://ollama.com)
   - Pull the default model:
     ```bash
     ollama pull llama3.1:8b
     ```
   - Verify it is running on `http://127.0.0.1:11434`.

---

### Step-by-Step Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/Shreyan-18/AI-took-our-job.git
cd AI-took-our-job
```

#### 2. Create and Activate a Virtual Environment

- **Windows (PowerShell)**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
  *(If script execution is disabled: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

- **Windows (Command Prompt / CMD)**:
  ```cmd
  python -m venv venv
  venv\Scripts\activate.bat
  ```

- **macOS / Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

#### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Configure Environment Variables
Copy the pre-configured `.env.example` to `.env`:

- **Windows (PowerShell)**:
  ```powershell
  Copy-Item .env.example .env
  ```
- **Windows (CMD)**:
  ```cmd
  copy .env.example .env
  ```
- **macOS / Linux**:
  ```bash
  cp .env.example .env
  ```

> **Note**: `.env.example` comes pre-configured with the production Neon database connection string, Langfuse public/secret keys, and local Ollama endpoint (`127.0.0.1:11434`).

---

## 🚀 Running the Application

### 1. Run the Comprehensive End-to-End Verification Test
Validate that Neon PostgreSQL, Ollama 8B, multi-turn interview, PDF generation, and HTTP server endpoints work together:
```bash
python test_system_e2e.py
```
*(On macOS/Linux you can also use `python3 test_system_e2e.py`)*

Expected output:
```
==========================================
1. TESTING NEON POSTGRESQL & CITIZEN AUTH
 [OK] Direct psycopg2 connection established to Neon
 [OK] Neon schema verified (redtape_sessions, messages, artifacts)
 [OK] Authenticated citizen profile loaded: Tamajit Ghosh (PAN: ABCDE1234F)

==========================================
2. TESTING LOCAL OLLAMA (llama3.1:8b)
 [INFO] Active Ollama model: llama3.1:8b
 [OK] Local Ollama responded in 1.68s (36.3 t/s): OK

==========================================
3. TESTING MULTI-AGENT CONVERSATIONAL FLOW
 [OK] Turn 1 processed. Interview open questions generated targeting: ['turnover', 'workers', 'address']
 [OK] Turn 2 processed. Auto-filled AcroForm PDFs generated: 7
      📄 KMC_Section199_Trade_Enlistment.pdf (100% filled)
      📄 WB_Shops_Establishment_Form_B.pdf (100% filled)
      📄 FSSAI_Registration_Form_A.pdf (88% filled)
      ...
 [OK] Digital Web Portal Manifests generated: 3

==========================================
4. TESTING HTTP SERVER ENDPOINTS
 [OK] GET /api/model -> active: llama3.1:8b
 [OK] GET /api/auth/me -> user: Tamajit Ghosh
 [OK] GET /api/sessions -> persistent sessions in Neon PostgreSQL
 [OK] GET / -> Rendered 2026 Claude-style Web UI HTML

🎉 ALL E2E VERIFICATION TESTS PASSED SUCCESSFULLY!
```

### 2. Start the Live Interactive Web Application
```bash
python demo_server.py
```

Open your browser and navigate to:
```
http://127.0.0.1:8765
```

---

## 🎯 Target Verification Scenarios

You can test any custom business idea or use the 3 built-in reference scenarios:

1. **Artisan Bakery in Park Circus, Kolkata**:
   - *Prompt*: `"I want to open a small bakery in Park Circus, Kolkata with 5 counter seats"`
   - *Applicable Regulations*: KMC Trade License (CE), WB Shops & Establishments Act, FSSAI Food Safety Registration (or State License if turnover > ₹12L), Profession Tax.
2. **Stationery & Book Stall in Sodepur / Panihati**:
   - *Prompt*: `"I want to start a small stationery and book stall near Sodepur station in Panihati"`
   - *Applicable Regulations*: Panihati Municipality Form J Trade License, Signboard Clearance, WB Shops & Establishments Act.
3. **Readymade Garment Boutique in Barrackpore**:
   - *Prompt*: `"I want to launch a readymade garments boutique in Barrackpore with 4 sewing machines"`
   - *Applicable Regulations*: Barrackpore Municipality Trade Enlistment, WB Textile Fire Safety Self-Declaration, WB Shops & Establishments Act.

---

## 📁 Repository Structure

```
.
├── demo_server.py                  # High-performance HTTP server & Claude.ai UI host
├── interview_engine_v2.py          # Multi-agent orchestrator & stateful interview engine
├── ui_template.py                  # Responsive Claude 3.5 Sonnet-style web application
├── postgres_db.py                  # Neon PostgreSQL persistence layer & cold-start handler
├── memory_engine.py                # Citizen profile memory & pgvector semantic retrieval
├── ollama_client.py                # Local Ollama client with IPv4 fallback (127.0.0.1:11434)
├── langfuse_tracer.py              # Asynchronous Langfuse distributed tracing adapter
├── data/
│   └── scenarios_kb.json           # 2026 verified statutory regulations & fee matrices
├── requirements.txt                # Cross-platform Python dependencies (psycopg2-binary, etc.)
├── .gitattributes                  # LF/CRLF line ending normalization rules
├── .env.example                    # Sample environment variables for Neon and Langfuse
├── test_system_e2e.py              # Automated 4-tier end-to-end verification suite
└── redtape-navigator-unified/
    ├── assets/forms/               # Official AcroForm PDFs & field mapping definitions
    ├── drafts/                     # Generated session artifacts & pre-rendered showcase packs
    └── scripts/                    # Specialized engines (research, compliance, document, inspect)
```

---

## 🔒 Security & License

- **Data Privacy**: All conversational LLM processing occurs locally on your machine via Ollama. No citizen details or proprietary business plans leave your device.
- **Cross-Platform Certified**: Tested across macOS Sequoia and Windows 10/11 (PowerShell & CMD).
- **License**: MIT License. Built for national compliance simplification.
