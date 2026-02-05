# MyAgent: Roadmap & TODO

This document tracks the future development of the **Secure Personal Agentic Platform**. 

## 🎯 Philosophy: Agent System First
**MyAgent** is an agentic system designed for technological sovereignty, privacy, and capability. While the system is built with **Neuro-Supportive** design intent (reducing cognitive load, bridging execution gaps), it is primarily an extensible, secure agent platform.

---

## 🏗 MoSCoW Prioritization
**M**: Must Have | **S**: Should Have | **C**: Could Have | **W**: Won't Have

### 🧠 Core Intelligence & Memory
| Priority | Feature | Description |
| :--- | :--- | :--- |
| **M** | **Long-Term Memory** (LTM) | Implement Markdown-based local memory in `core/memory.py`. |
| **M** | **Context Injection** (CI) | Inject "Second Brain" fragments into prompts based on query. |
| **M** | **Intent Refinement** (IR) | Use local models (Mistral/Llama3) for intent classification. |
| **C** | **Habit Tracking** (HT) | Background agent to monitor and nudge habit consistency. |

### 🔒 Security & Privacy (Trust but Verify)
| Priority | Feature | Description |
| :--- | :--- | :--- |
| **M** | **Judge-as-a-Service** (JaaS) | Local "Judge" model to audit all external API responses. |
| **M** | **PII Scrubbing** (PIIS) | Redaction layer for sensitive data before external transmission. |
| **M** | **Local Model Optimization** (LMO) | Tune parameters specifically for M1 Mac performance. |

### 🧩 Skills, Tooling & MCP
| Priority | Feature | Description |
| :--- | :--- | :--- |
| **M** | **Skills Registry** (SR) | Central system to register and discover agent capabilities. |
| **M** | **Local Tool-Calling** (LTC) | Enable Ollama to invoke local Python functions. |
| **M** | **MCP Integration** (MCP) | Support the Model Context Protocol for tool servers. |
| **M** | **Google Workspace Skills** (GWS)| Expand adapters for GMail sending and Drive creation. |

### 🤝 Integrations & Sync
| Priority | Feature | Description |
| :--- | :--- | :--- |
| **M** | **Google Workspace** (GW) | Read-only adapters for GMail, Calendar, and Drive. |
| **C** | **Home Assistant** (HA) | Local-only adapter for secure smart home control. |

### 🧵 Background Agents & Parallel Work
| Priority | Feature | Description |
| :--- | :--- | :--- |
| **M** | **FastAPI BackgroundTasks** (FAPIBT) | Move slow model/skill calls to background threads. |
| **M** | **Status Polling** (SP) | Mechanim for UI/Telegram to check job status. |
| **S** | **Proactive Notifications** (PN) | Push updates to Telegram upon task completion. |

### 📱 Interface & Experience
| Priority | Feature | Description |
| :--- | :--- | :--- |
| **M** | **Web Settings Page** (WSP) | UI for managing API keys, models, and privacy rules. |
| **S** | **Telegram Reminders** (TR) | Scheduling logic for proactive bot notifications. |
| **C** | **Usage Dashboard** (UD) | Visual breakdown of usage and estimated cost savings. |
| **C** | **Dark Mode Sync** (DMS) | Support for system-wide dark mode in the dashboard. |

### ⚡ Agent Workflows & Efficiency
*Neuro-supportive intent is integrated into the design of these features to preserve executive function.*

| Priority | Feature | Description |
| :--- | :--- | :--- |
| **S** | **Micro-Tasking Engine** (MTE) | Break large goals into "dopamine-achievable" steps. |
| **S** | **Body Doubling Bot** (BDB) | Timed "work-with-me" sessions with Telegram check-ins. |
| **S** | **Executive Function Buffer** (EFB) | Rewrite complex inputs into clear, actionable points. |

---
*Follow the [VISION.md](./VISION.md) and [Operating Principles](./operating_principles.md) when contributing.*
