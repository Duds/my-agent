# MyAgent: Roadmap & TODO

This document tracks the development of the **Secure Personal Agentic Platform**, structured around core **System Capabilities** that solve specific user pain points.

## 🎯 Philosophy: Pain-Point Driven

Development is prioritized by "Jobs to Be Done"—building foundational engines that enable specific lifestyle improvements, rather than just collecting features.

---

## ✅ Recently Completed

| Date       | Item                                        | Notes                                                                                                                                                                                                                                                                                                                             |
| :--------- | :------------------------------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 09/02/2026 | **Roadmap Plan Implementation**             | PBI-016, 039, 040, 036: Complete. PBI-014: E2E tests (projects CRUD, agent-processes, conversations); frontend Jest + RTL setup; Button and utils component tests.                                                                                                                                 |
| 08/02/2026 | **UX/UI Review & Gap Analysis**             | Identified model selector broken (missing type/status), Automation Hub empty state, dead components. See [docs/UX_UI_REVIEW_AND_GAP_ANALYSIS.md](docs/UX_UI_REVIEW_AND_GAP_ANALYSIS.md).                                                                                                                                           |
| 08/02/2026 | **Model Metadata in API** (PBI-033)         | Added type, status, contextWindow to /api/models. Chat model selector and Settings panel now work for manual model override.                                                                                                                                                                                                      |
| 08/02/2026 | **Automation Hub Empty State** (PBI-034)     | Added helpful empty-state messages when Agents, Cron Jobs, or Automations lists are empty.                                                                                                                                                                                                                                       |
| 08/02/2026 | **MCP Server Discovery** (PBI-027)           | Config-driven MCP list from data/mcp_servers.json, status check (HTTP probe / stdio=configured), Add button with config instructions, docs/MCP_CONFIG.md.                                                                                                                                                                       |
| 07/02/2026 | **Router Initialization Bug Fix** (PBI-002) | Fixed router initialization order bug in `core/main.py`.                                                                                                                                                                                                                                                                          |
| 07/02/2026 | **Codebase Review Plan Implementation**     | Mode-only UX: integrated Mode/Model controls in chat input, StatusBar model only when overridden, /api/modes, query params (model_id, mode_id, session_id), skills PATCH, projects/conversations CRUD (in-memory), Automation Hub section, context-display, automation placeholders. PBIs 023, 025, 026, 028, 029, 032 addressed. |
| 07/02/2026 | **IDE Workspace Configuration** (PBI-024)   | Updated `.vscode/settings.json` and `.cursorignore`: excluded `my-agent-venv` from explorer/files/search, disabled Python analysis indexing, excluded venvs/node_modules from analysis for better Cursor/VS Code performance.                                                                                                     |
| 07/02/2026 | **README Startup Instructions**             | Added clear backend (port 8001) and frontend (port 3000) startup instructions.                                                                                                                                                                                                                                                    |
| 07/02/2026 | **Phase 2: Production Readiness**           | Implemented robust error handling, retry logic, async memory system with encryption, and frontend type safety. Fixed port mismatches. (PBIs 008, 009, 010, 011, 012, 018)                                                                                                                                                         |

---

## 🏗 MoSCoW Prioritization

**M**: Must Have | **S**: Should Have | **C**: Could Have | **W**: Won't Have

### 👁️ capability.context_awareness (The "Shoulder Angel")

_Solves: Focus drift, "Getting sidetracked", Real-time intervention._
| Priority | Feature | Description |
| :--- | :--- | :--- |
| **M** | **Window Poller Service** | Background daemon to detect active window/process contexts. |
| **M** | **Context Classifier** | Local LLM capability to judge "Current Activity" vs "Stated Goal". |
| **M** | **Mode & Context Controls** | User activity mode (Focus, Relax), context display, intervention toasts. Model selection: best-fit default; manual override is deliberate opt-in only. Subtle model indicator per response in chat. ✅ PBI-023 |
| **S** | **Intervention Toasts** | Non-blocking OS notifications to nudge users back on track. |
| **S** | **Modes** | Activity modes (General, Private, Focus, Relax) for routing/behaviour. Per research: Mode replaces Persona. ✅ PBI-025 |

### 🤖 capability.automation_engine (The "Timesheet Terminator")

_Solves: Administrative friction, Repetitive web tasks._
| Priority | Feature | Description |
| :--- | :--- | :--- |
| **M** | **Headless Browser Core** | Robust Playwright/Selenium wrapper for background web navigation. |
| **M** | **Credential Vault** | Secure, local storage for target site credentials. |
| **M** | **Automation Hub** | UI for agents, cron jobs, automations, scripts, status logs, and error reports. ✅ PBI-032 (UI structure; backend stubbed) |
| **C** | **Human-in-the-Loop UX** | Secure pop-up for OTP entry or final submission approval. |

### 🛡️ capability.sentinel (The "Digital Janitor")

_Solves: File clutter, Inbox overload, Organization overhead._
| Priority | Feature | Description |
| :--- | :--- | :--- |
| **M** | **File Watchdog** | Service to monitor `~/Downloads` and `~/Projects` for new files. |
| **M** | **Content Classifier** | LLM-based inspection of file contents for auto-sorting rules. |
| **S** | **Review Queue UX** | "Tinder for Files" interface to approve/reject agent sorting suggestions. PBI-022 |
| **S** | **Inbox Zero Connector** | GMail adapter for classifying and archiving newsletters/spam. |
| **S** | **Privacy Vault indicator** | UI to show/manage local-only sensitive data. PBI-030 |

### 🧠 capability.knowledge_graph (The "Connector")

_Solves: Project abandonment, Idea loss, Relationship tracking._
| Priority | Feature | Description |
| :--- | :--- | :--- |
| **M** | **Vector Store Core** | Local vector db (Chroma) for long-term semantic storage. |
| **S** | **Knowledge Graph UI** | Design vector store browser, inspiration sidebar interface. PBI-020 |
| **S** | **Pinterest Adapter** | Scraper to ingest boards into the user profile. |
| **C** | **Inspiration Sidebar** | IDE/Desktop widget suggesting relevant past ideas/notes. |

---

### 🌐 capability.distributed_mesh (The "Hive Mind")

_Solves: Resource constraints, Work/Home continuity._
| Priority | Feature | Description |
| :--- | :--- | :--- |
| **M** | **Mesh Networking** | Secure overlay network (Tailscale/ZeroTier) to connect nodes. |
| **M** | **Remote RPC Layer** | API for Node A to trigger function on Node B (e.g., "Run Model"). |
| **M** | **State Synchronization** | Syncing Vector DB / Task State between nodes. |
| **S** | **Distributed Mesh UI** | Design mesh health visualization, node manager view. PBI-021 |
| **S** | **Resource Discovery** | Auto-detection of available GPUs/Tools on the mesh. |

### 🏗️ Foundation & Infrastructure

| Priority | Feature                | Description                                                                                                                    |
| :------- | :--------------------- | :----------------------------------------------------------------------------------------------------------------------------- |
| **M**    | **Settings Schema**    | Centralized `settings.yaml` / Pydantic models for all engine config.                                                           |
| **M**    | **Event Bus**          | Pub/Sub system for engines to communicate (e.g., Sentinel -> Knowledge).                                                       |
| **M**    | **Frontend Core**      | Next.js Dashboard to host the UI for all above capabilities.                                                                   |
| **S**    | **Integrations**       | External connectors: Google Workspace (Gmail, Calendar, Drive), Pinterest, deployment, database. Single capability. ✅ PBI-028 |
| **S**    | **Projects**           | Organisational grouping for conversations (scaffold concept). ✅ PBI-029                                                       |
| **S**    | **Skills Registry**    | Agent capabilities/tools, enable/disable. ✅ PBI-026                                                                           |
| **S**    | **MCP Server Config**  | MCP discovery and configuration. PBI-027                                                                                       |
| **C**    | **Approval UX Design** | Shared approve/reject/undo for Sentinel + HITL. PBI-031                                                                        |

---

## 🔧 Technical Debt & Critical Fixes (From Codebase Review)

### 🚨 Phase 1: Critical Fixes (Week 1)

_Priority: CRITICAL - System stability and security_

| Priority | Feature                               | Description                                                                       | Backlog ID |
| :------- | :------------------------------------ | :-------------------------------------------------------------------------------- | :--------- |
| ✅       | **Router Initialization Bug Fix**     | Fix router initialization order in `core/main.py` - system won't start otherwise. | PBI-002    |
| ✅       | **Security Validator Implementation** | Implement or remove security validator placeholder in `core/security.py`.         | PBI-003    |
| ✅       | **API Authentication**                | Add API key authentication, secure CORS, and rate limiting.                       | PBI-004    |
| ✅       | **Adapter Instance Management**       | Fix adapter instantiation pattern - use singleton or factory.                     | PBI-005    |
| ✅       | **Logging Framework**                 | Replace `print()` with proper logging framework throughout codebase.              | PBI-006    |

### ⚙️ Phase 2: Production Readiness (Week 2-3)

_Priority: HIGH - Make system production-ready_

| Priority | Feature                       | Description                                                                | Backlog ID |
| :------- | :---------------------------- | :------------------------------------------------------------------------- | :--------- |
| ✅       | **Configuration Management**  | Create `config.py` with Pydantic settings, centralize all configuration.   | PBI-007    |
| ✅       | **Error Handling**            | Add comprehensive try/except blocks, retry logic, and fallback mechanisms. | PBI-008    |
| ✅       | **Testing Infrastructure**    | Convert tests to pytest, add pytest.ini, conftest.py, and coverage.        | PBI-009    |
| ✅       | **UI Scaffold Integration**   | Merge UI scaffold from `.temp/scaffold_unzipped/` into frontend.           | PBI-010    |
| ✅       | **Frontend Type Safety**      | Define TypeScript interfaces for API, fix `any` types, add error handling. | PBI-011    |
| ✅       | **Memory System Integration** | Connect memory to router, add vault encryption, implement sessions.        | PBI-012    |

### 🎯 Phase 3: Feature Completion (Week 4-6) - **IN PROGRESS**

_Priority: MEDIUM - Complete MVP features_

| Priority | Feature                            | Description                                                             | Backlog ID |
| :------- | :--------------------------------- | :---------------------------------------------------------------------- | :--------- |
| **S**    | ~~**Enhanced Intent Classification**~~ | ~~Keyword matching.~~ **Done** — SentenceTransformer-based, confidence scores. | PBI-013 ✅ |
| **S**    | **Comprehensive Testing**          | Add adapter tests, integration tests, E2E tests, frontend tests.        | PBI-014    |
| **S**    | ~~**API Documentation**~~           | ~~OpenAPI/Swagger.~~ **Done** — /docs, /redoc via FastAPI.              | PBI-015 ✅ |
| **S**    | ~~**Monitoring & Observability**~~ | ~~/health, /ready.~~ **Done** — /metrics Prometheus endpoint added. | PBI-016 ✅ |

### 🧹 Quick Wins (High Impact, Low Effort)

| Priority | Feature                       | Description                                                          | Backlog ID |
| :------- | :---------------------------- | :------------------------------------------------------------------- | :--------- |
| ✅       | **Code Cleanup**              | Remove duplicate Telegram adapter, add `.temp/` to `.gitignore`.       | PBI-017    |
| ✅       | **Port Mismatch Fix**         | Fix frontend port mismatch (8000 vs 8001).                           | PBI-018    |
| ✅       | **Frontend Metadata**         | Update frontend metadata in layout.tsx, remove default Next.js text. | PBI-019    |
| ✅       | **Model Metadata in API**     | Add type, status, contextWindow so model selector works.              | PBI-033    |
| ✅       | **Automation Hub Empty State**| Helpful messages when Agents/Cron/Automations lists are empty.       | PBI-034    |
| ✅       | **Model Metadata in Settings**| Models tab in Settings with tags, benefits, HoverCard pros/cons.      | PBI-038    |
| ✅       | **Automation Hub APIs**       | Config-driven cron/automations from data/*.json.                       | PBI-039    |
| ✅       | **Project Management UI**     | New project, edit project (name, colour) in sidebar.                   | PBI-040    |

### 🎨 Phase 4: UI Components for Missing Capabilities

_Priority: LOW - Advanced features_

| Priority | Feature                            | Description                                                                                      | Backlog ID |
| :------- | :--------------------------------- | :----------------------------------------------------------------------------------------------- | :--------- |
| **C**    | **Knowledge Graph UI**             | Design vector store browser, inspiration sidebar interface.                                      | PBI-020    |
| **C**    | **Distributed Mesh UI**            | Design mesh health visualization, node manager view.                                             | PBI-021    |
| **C**    | **Sentinel Review Queue UI**       | Design "Tinder for Files" approval interface.                                                    | PBI-022    |
| **C**    | ~~**Mode & Context Controls UI**~~ | ~~User activity mode, context display, toasts.~~ **Done** — integrated Mode/Model in chat input. | PBI-023 ✅ |
| **C**    | ~~**Automation Hub UI**~~          | ~~Agents, cron, automations, scripts, logs, reports.~~ **Done** — section header + placeholders. | PBI-032 ✅ |

### 📋 Reconciled Scaffold Features (from codebase review)

| Priority | Feature                       | Description                                                                        | Backlog ID |
| :------- | :---------------------------- | :--------------------------------------------------------------------------------- | :--------- |
| **S**    | ~~**Modes from config**~~     | ~~Move personas to modes from config.~~ **Done** — /api/modes, mode_id in query.   | PBI-025 ✅ |
| **S**    | ~~**Skills Registry**~~       | ~~Promote PBI-SR; backend + persistence.~~ **Done** — PATCH /api/skills/:id.       | PBI-026 ✅ |
| **S**    | ~~**MCP Server discovery**~~  | ~~Backend API + Settings UI.~~ **Done** — config-driven, status check, Add dialog. | PBI-027 ✅ |
| **S**    | ~~**Integrations API**~~      | ~~Wire Google, Pinterest, etc.~~ **Done** — Google wired when credentials present. | PBI-028 ✅ |
| **S**    | ~~**Projects persistence**~~  | ~~CRUD, conversation association.~~ **Done** — in-memory CRUD + conversation link. | PBI-029 ✅ |
| **S**    | **Agent Template & Conformance**    | Framework + rules so generated agents conform to platform standards.        | PBI-035    |
| **S**    | ~~**Agent Code Generation**~~       | ~~LLM generates code; validate, register.~~ **Done** — /query with create_agent intent. | PBI-036 ✅ |
| **S**    | **Privacy Vault UI**                | Indicator and basic management.                                            | PBI-030    |
| **C**    | **Approval UX design system**       | Shared approve/reject/undo for Sentinel + HITL.                             | PBI-031    |
| **C**    | **Agent Creation Review UI**        | Review/edit generated code before registering.                            | PBI-037    |

---

### 🤖 Agent Creation (Code Generation + Conformance + Registration)

_The solution generates custom agent code from natural language. Rules/framework ensure conformity; generated agents are registered and added to the Automation Hub._

| Priority | Feature                             | Description                                                                 | Backlog ID |
| :------- | :---------------------------------- | :-------------------------------------------------------------------------- | :--------- |
| **S**    | **Agent Template & Conformance**   | Template, rules (agent_rules.json), validator; generated code must conform. | PBI-035    |
| **S**    | **Agent Code Generation**          | LLM generates agent code; validate → register → add to Automation Hub.      | PBI-036    |
| **C**    | **Agent Creation Review UI**       | Optional UI to review/edit generated code before approving registration.    | PBI-037    |

---

## 📋 UX Review: Next Priorities (from gap analysis)

See [docs/UX_UI_REVIEW_AND_GAP_ANALYSIS.md](docs/UX_UI_REVIEW_AND_GAP_ANALYSIS.md) for full analysis.

### Short-term (1–2 weeks)

| Item | Backlog | Notes |
| :--- | :------ | :--- |
| **Monitoring /metrics** | PBI-016 | Add Prometheus metrics endpoint to complete observability. |
| **Automation Hub APIs** | PBI-039 | Config-driven cron jobs and automations from JSON. |
| **Project management UI** | PBI-040 | Add "New project" and basic CRUD in sidebar. |
| **MCP Server Discovery** | PBI-027 | Config-driven MCP list; enable Add button or document config. |
| **ContextDisplay** | — | Wire when Window Poller exists; currently blocked. |

### Medium-term (aligned with roadmap)

| Item | Backlog | Notes |
| :--- | :------ | :--- |
| **Agent Template & Conformance** | PBI-035 | Template, rules, validator for generated agent code. |
| **Agent Code Generation** | PBI-036 | LLM generates code; validate, register, add to Automation Hub. |
| **Privacy Vault UI** | PBI-030 | After vault API exists. |
| **Sentinel Review Queue** | PBI-022 | Use ApprovalCard; depends on File Watchdog + Content Classifier. |
| **ScriptsList, StatusLogs, ErrorReports** | PBI-032 | Add Automation Hub detail view; wire components. |

---

_Follow the [VISION.md](./VISION.md) and [Operating Principles](./operating_principles.md) when contributing._
