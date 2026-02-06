# MyAgent: Roadmap & TODO

This document tracks the development of the **Secure Personal Agentic Platform**, structured around core **System Capabilities** that solve specific user pain points.

## 🎯 Philosophy: Pain-Point Driven
Development is prioritized by "Jobs to Be Done"—building foundational engines that enable specific lifestyle improvements, rather than just collecting features.

---

## 🏗 MoSCoW Prioritization
**M**: Must Have | **S**: Should Have | **C**: Could Have | **W**: Won't Have

### 👁️ capability.context_awareness (The "Shoulder Angel")
*Solves: Focus drift, "Getting sidetracked", Real-time intervention.*
| Priority | Feature | Description |
| :--- | :--- | :--- |
| **M** | **Window Poller Service** | Background daemon to detect active window/process contexts. |
| **M** | **Context Classifier** | Local LLM capability to judge "Current Activity" vs "Stated Goal". |
| **M** | **Mode Switcher UX** | Status bar/Toggle for specific modes (e.g., "Deep Work", "Relax"). |
| **S** | **Intervention Toasts** | Non-blocking OS notifications to nudge users back on track. |

### 🤖 capability.automation_engine (The "Timesheet Terminator")
*Solves: Administrative friction, Repetitive web tasks.*
| Priority | Feature | Description |
| :--- | :--- | :--- |
| **M** | **Headless Browser Core** | Robust Playwright/Selenium wrapper for background web navigation. |
| **M** | **Credential Vault** | Secure, local storage for target site credentials. |
| **M** | **Automation Dashboard** | UI to view available scripts, status logs, and error reports. |
| **C** | **Human-in-the-Loop UX** | Secure pop-up for OTP entry or final submission approval. |

### 🛡️ capability.sentinel (The "Digital Janitor")
*Solves: File clutter, Inbox overload, Organization overhead.*
| Priority | Feature | Description |
| :--- | :--- | :--- |
| **M** | **File Watchdog** | Service to monitor `~/Downloads` and `~/Projects` for new files. |
| **M** | **Content Classifier** | LLM-based inspection of file contents for auto-sorting rules. |
| **S** | **Review Queue UX** | "Tinder for Files" interface to approve/reject agent sorting suggestions. |
| **S** | **Inbox Zero Connector** | GMail adapter for classifying and archiving newsletters/spam. |

### 🧠 capability.knowledge_graph (The "Connector")
*Solves: Project abandonment, Idea loss, Relationship tracking.*
| Priority | Feature | Description |
| :--- | :--- | :--- |
| **M** | **Vector Store Core** | Local vector db (Chroma) for long-term semantic storage. |
| **S** | **Pinterest Adapter** | Scraper to ingest boards into the user profile. |
| **C** | **Inspiration Sidebar** | IDE/Desktop widget suggesting relevant past ideas/notes. |

---

### 🌐 capability.distributed_mesh (The "Hive Mind")
*Solves: Resource constraints, Work/Home continuity.*
| Priority | Feature | Description |
| :--- | :--- | :--- |
| **M** | **Mesh Networking** | Secure overlay network (Tailscale/ZeroTier) to connect nodes. |
| **M** | **Remote RPC Layer** | API for Node A to trigger function on Node B (e.g., "Run Model"). |
| **M** | **State Synchronization** | Syncing Vector DB / Task State between nodes. |
| **S** | **Resource Discovery** | Auto-detection of available GPUs/Tools on the mesh. |

### 🏗️ Foundation & Infrastructure
| Priority | Feature | Description |
| :--- | :--- | :--- |
| **M** | **Settings Schema** | Centralized `settings.yaml` / Pydantic models for all engine config. |
| **M** | **Event Bus** | Pub/Sub system for engines to communicate (e.g., Sentinel -> Knowledge). |
| **M** | **Frontend Core** | Next.js Dashboard to host the UI for all above capabilities. |

---

## 🔧 Technical Debt & Critical Fixes (From Codebase Review)

### 🚨 Phase 1: Critical Fixes (Week 1)
*Priority: CRITICAL - System stability and security*

| Priority | Feature | Description | Backlog ID |
| :--- | :--- | :--- | :--- |
| **M** | **Router Initialization Bug Fix** | Fix router initialization order in `core/main.py` - system won't start otherwise. | PBI-002 |
| **M** | **Security Validator Implementation** | Implement or remove security validator placeholder in `core/security.py`. | PBI-003 |
| **M** | **API Authentication** | Add API key authentication, secure CORS, and rate limiting. | PBI-004 |
| **M** | **Adapter Instance Management** | Fix adapter instantiation pattern - use singleton or factory. | PBI-005 |
| **M** | **Logging Framework** | Replace `print()` with proper logging framework throughout codebase. | PBI-006 |

### ⚙️ Phase 2: Production Readiness (Week 2-3)
*Priority: HIGH - Make system production-ready*

| Priority | Feature | Description | Backlog ID |
| :--- | :--- | :--- | :--- |
| **M** | **Configuration Management** | Create `config.py` with Pydantic settings, centralize all configuration. | PBI-007 |
| **M** | **Error Handling** | Add comprehensive try/except blocks, retry logic, and fallback mechanisms. | PBI-008 |
| **M** | **Testing Infrastructure** | Convert tests to pytest, add pytest.ini, conftest.py, and coverage. | PBI-009 |
| **M** | **UI Scaffold Integration** | Merge UI scaffold from `.temp/scaffold_unzipped/` into frontend. | PBI-010 |
| **M** | **Frontend Type Safety** | Define TypeScript interfaces for API, fix `any` types, add error handling. | PBI-011 |
| **M** | **Memory System Integration** | Connect memory to router, add vault encryption, implement sessions. | PBI-012 |

### 🎯 Phase 3: Feature Completion (Week 4-6)
*Priority: MEDIUM - Complete MVP features*

| Priority | Feature | Description | Backlog ID |
| :--- | :--- | :--- | :--- |
| **S** | **Enhanced Intent Classification** | Replace keyword matching with ML-based approach, add confidence scores. | PBI-013 |
| **S** | **Comprehensive Testing** | Add adapter tests, integration tests, E2E tests, frontend tests. | PBI-014 |
| **S** | **API Documentation** | Add OpenAPI/Swagger docs, document all endpoints with examples. | PBI-015 |
| **S** | **Monitoring & Observability** | Add health checks, metrics collection, request tracing. | PBI-016 |

### 🧹 Quick Wins (High Impact, Low Effort)
| Priority | Feature | Description | Backlog ID |
| :--- | :--- | :--- | :--- |
| **S** | **Code Cleanup** | Remove duplicate Telegram adapter, add `.temp/` to `.gitignore`. | PBI-017 |
| **S** | **Port Mismatch Fix** | Fix frontend port mismatch (8000 vs 8001). | PBI-018 |
| **S** | **Frontend Metadata** | Update frontend metadata in layout.tsx, remove default Next.js text. | PBI-019 |

### 🎨 Phase 4: UI Components for Missing Capabilities
*Priority: LOW - Advanced features*

| Priority | Feature | Description | Backlog ID |
| :--- | :--- | :--- | :--- |
| **C** | **Knowledge Graph UI** | Design vector store browser, inspiration sidebar interface. | PBI-020 |
| **C** | **Distributed Mesh UI** | Design mesh health visualization, node manager view. | PBI-021 |
| **C** | **Sentinel Review Queue UI** | Design "Tinder for Files" approval interface. | PBI-022 |
| **C** | **Context Display UI** | Design active window/activity context indicator. | PBI-023 |

---
*Follow the [VISION.md](./VISION.md) and [Operating Principles](./operating_principles.md) when contributing.*
