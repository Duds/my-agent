# Full Codebase Feature Comparison: my-agent vs OpenClaw

**Compared codebases:**
- **my-agent**: `~/Projects/ai-agents/my-agent/` (this repo — Secure Personal Agentic Platform)
- **OpenClaw**: `~/Projects/ai-agents/openclaw/` (sibling directory; [openclaw/openclaw](https://github.com/openclaw/openclaw))

*Note: OpenClaw does not live under `my-agent/openclaw/`; it is a separate project in the same parent folder.*

---

## 1. Overview & positioning

| Aspect | my-agent | OpenClaw |
|--------|----------|----------|
| **Tagline** | Privacy-first “Second Brain”, neuro-supportive, hybrid local/cloud | Personal AI assistant on your own devices; “EXFOLIATE!” |
| **Primary goal** | Operational independence, cost efficiency, security assurance, neuro-supportive automation | Single control-plane assistant across all messaging channels + voice + canvas |
| **Scale** | Single repo, ~138 files (Python backend + Next.js frontend) | Monorepo, 5000+ files (TypeScript core, Swift/Kotlin apps, extensions, docs) |
| **Governance** | Backlog (PBI), TODO.md, VISION.md, operating principles | AGENTS.md, skills, PR workflow, Mintlify docs, ClawHub |

---

## 2. Technology stack

| Layer | my-agent | OpenClaw |
|-------|----------|----------|
| **Backend** | Python 3.10+, FastAPI, uvicorn | Node 22+, TypeScript (ESM), Bun/pnpm |
| **Frontend** | Next.js 14+ (TypeScript), React, shadcn/ui | Web UI (Control UI + WebChat) from gateway; shared Swift/Kotlin for apps |
| **AI runtime** | Ollama (local), Anthropic, Moonshot; adapter pattern | Pi agent (RPC); Anthropic/OpenAI OAuth; any model via config |
| **Messaging** | Telegram Bot API (built-in) | WhatsApp, Telegram, Slack, Discord, Google Chat, Signal, iMessage/BlueBubbles, MS Teams, Matrix, Zalo, WebChat (core + extensions) |
| **Packaging** | setup.sh, pytest, venv | npm/pnpm global, Nix, Docker, macOS/iOS/Android apps |

---

## 3. Core architecture

### my-agent
- **Controller** → **Router** → **Intent classifier** → **Security validator** → **Adapters** (local Ollama + remote API).
- **Memory**: Markdown/JSON, local-only (`core/memory.py`).
- **Single process**: FastAPI app; optional Telegram bot; no separate gateway daemon.
- **Config**: Env + JSON (routing, MCP); modes and task-specific model assignment.

### OpenClaw
- **Gateway** (WebSocket control plane) at `ws://127.0.0.1:18789`: sessions, presence, config, cron, webhooks, Control UI, Canvas host.
- **Channels** connect to Gateway; **Pi agent** (RPC) does tool/block streaming.
- **Multi-agent routing**: route channels/accounts/peers to different workspaces/agents.
- **Sessions**: `main`, group isolation, activation modes, queue modes, reply-back.
- **State**: config in `~/.openclaw/`, workspace `~/.openclaw/workspace`, skills under workspace.

---

## 4. Channels & user interfaces

| Feature | my-agent | OpenClaw |
|---------|----------|----------|
| **Telegram** | ✅ Built-in (`core/telegram_bot.py`, `adapters_telegram`) | ✅ Core (`src/telegram`) |
| **Web dashboard** | ✅ Next.js Command Centre (chat, models, settings, automation hub) | ✅ Control UI + WebChat from gateway |
| **WhatsApp** | ❌ | ✅ (Baileys) |
| **Slack** | ❌ | ✅ (Bolt) |
| **Discord** | ❌ | ✅ (discord.js) + extension |
| **Google Chat** | ❌ | ✅ (extension) |
| **Signal** | ❌ | ✅ (signal-cli) + extension |
| **iMessage** | ❌ | ✅ BlueBubbles (recommended) + legacy imessage extension |
| **MS Teams** | ❌ | ✅ Extension |
| **Matrix** | ❌ | ✅ Extension |
| **Zalo / Zalo Personal** | ❌ | ✅ Extensions |
| **WebChat** | ❌ | ✅ Served by gateway |
| **CLI** | ❌ (API-only for automation) | ✅ `openclaw` (gateway, agent, send, wizard, doctor) |
| **TUI** | ❌ | ✅ (`src/tui`) |

---

## 5. AI routing, intents & models

### my-agent
- **Intents**: SPEED, QUALITY, PRIVATE, NSFW, CODING, FINANCE, CREATE_AGENT.
- **Routing**: Intent → task-specific config (intent_classification, security_judge, pii_redactor) → local vs remote adapter.
- **Privacy rule**: PRIVATE/NSFW always local (Ollama); no override.
- **Security**: “Trust but Verify” — Judge model (local) inspects remote outputs; PII redaction; heuristic filters.
- **Streaming**: `/query/stream` SSE for Ollama.
- **Modes**: Configurable modes (replacing personas); model metadata API.

### OpenClaw
- **Model config**: Central config; OAuth (Anthropic/OpenAI) vs API keys; failover.
- **Session-level**: model, thinking level, verbose, send policy, group activation.
- **No built-in intent enum**: routing is channel/workspace/agent and session-based, not content-intent.
- **Pi agent**: RPC runtime with tool streaming and block streaming; long-context (e.g. Opus) recommended.
- **Chat commands**: `/status`, `/new`, `/restart`, `/think`, `/verbose`, `/usage`, `/activation`, etc.

---

## 6. Security & privacy

| Aspect | my-agent | OpenClaw |
|--------|----------|----------|
| **API auth** | Optional X-API-Key (FastAPI) | Gateway: token/password; Tailscale identity; SSH tunnels |
| **DM policy** | N/A (Telegram only) | Pairing by default; allowlists; `openclaw doctor` for risky config |
| **Data locality** | Local-first; sensitive intents forced local | Local-first gateway; credentials in `~/.openclaw/credentials/` |
| **Audit** | Logging, Prometheus metrics | Logging; security docs |
| **Principle** | Principle of Least Privilege (AI), Trust but Verify | Treat DMs as untrusted; pairing/allowlists |

---

## 7. Peer review: pros and cons

Here “peer review” is used in two ways: **AI peer review** (one model reviewing another model’s output) and **code/contributor peer review** (human review of changes, PR workflow).

### 7.1 AI peer review (model-as-judge / output validation)

| | my-agent | OpenClaw |
|---|----------|----------|
| **Approach** | **Trust but Verify**: a separate “Judge” model (e.g. local Ollama) reviews remote model outputs before they are returned. Heuristic layer (dangerous commands, credential patterns) plus optional LLM verdict (SAFE/UNSAFE). PII redactor can run in the same pipeline. | No built-in second-model review. Output is streamed/returned from the primary model. Security is channel-side (pairing, allowlists) and operational (doctor, docs). |
| **Pros** | Catches prompt injection, PII leaks, and malicious code at response time. Aligns with “Trust but Verify” and Least Privilege. Judge can be local-only, so sensitive content need not leave the machine. Heuristics add a fast, deterministic first line of defence. | Simpler pipeline; no extra latency or judge cost. Fewer moving parts; no risk of judge misconfiguration or overload. Suits “trust the provider” and channel-based access control. |
| **Cons** | Extra latency and (if Judge is remote) cost. Judge can misclassify (false positives/negatives). Heuristics are brittle and may miss novel attacks. Requires maintaining a suitable judge model and prompts. | No automated check that a given response is safe or free of leakage. Relies on model behaviour and channel/ops controls; vulnerable to novel prompt injection or exfiltration that the primary model doesn’t refuse. |

**Summary (AI peer review):** my-agent trades latency and complexity for automated output validation; OpenClaw favours simplicity and defers safety to channels and operations.

### 7.2 Code / contributor peer review

| | my-agent | OpenClaw |
|---|----------|----------|
| **Approach** | Backlog (PBI), TODO.md, development rules (`.cursor/rules`, `.agent/rules`). PR/code review process not explicitly described in the comparison docs. | Documented PR workflow (e.g. `.agents/skills/PR_WORKFLOW.md`), review-pr / prepare-pr / merge-pr agent skills, triage order, rebase rules, commit/changelog conventions. |
| **Pros** | Clear roadmap and acceptance criteria (PBIs). Rules give consistent guidance for AI and humans. Lighter process suits a single/small team. | Explicit review pipeline and skills improve consistency and quality bar. Rebase and changelog rules reduce merge friction. Documented co-contributor policy. |
| **Cons** | No single “peer review” doc; review expectations live in rules and habits. Risk of ad hoc or inconsistent review if the team grows. | Heavier process; more steps and docs to follow. May be overkill for very small or solo efforts. |

**Summary (code peer review):** my-agent emphasises product/backlog structure and rules; OpenClaw adds an explicit, skill-supported PR and merge workflow.

---

## 8. Memory & context

| Feature | my-agent | OpenClaw |
|--------|----------|----------|
| **Format** | Markdown + JSON files, local-only | Sessions, transcript history; Pi session model |
| **Scope** | User preferences, project history, context | Per-session; `sessions_list`, `sessions_history`, `sessions_send` |
| **Persistence** | `data/` dir (in repo/data) | `~/.openclaw/sessions/`; workspace |
| **Cross-agent** | N/A | Session tools for agent-to-agent messaging |

---

## 9. Automation, tools & skills

### my-agent
- **API surface**: REST (FastAPI) — `/query`, `/query/stream`, `/api/models`, config, modes, skills, MCPs, system status, Ollama start/stop, integrations, Telegram send, projects, conversations, agent processes, cron, automations, scripts, automation-logs, error-reports.
- **Concepts**: Projects, conversations, agent processes, cron jobs, automations, scripts; automation hub UI (scripts list, status logs, error reports).
- **MCP**: Configurable MCP servers (e.g. filesystem, GitHub).
- **Skills**: Platform skills registry (list, enable/disable via API); no external skill store.

### OpenClaw
- **Tools**: Browser (Chrome/Chromium, CDP), Canvas (A2UI), nodes (camera, screen, location, notify), cron, webhooks, Gmail Pub/Sub, session tools.
- **Skills**: Bundled, managed, workspace skills; install gating + UI; ClawHub registry for discovery.
- **Extensions**: Many (e.g. open-prose, memory-lancedb, voice-call, msteams, matrix, nostr, twitch, feishu, mattermost, nextcloud-talk, irc, line, lobster, etc.).
- **Open Prose**: Full prose workflow language (skills, examples, pipelines, agents).
- **Cron + wakeups**: Built into gateway.

---

## 10. Frontend / UI

| Feature | my-agent | OpenClaw |
|---------|----------|----------|
| **Framework** | Next.js 14, React, TypeScript, shadcn/ui | Gateway-served Control UI + WebChat; no Next.js app in main repo |
| **Pages** | Home, design-system, automation hub | Web UI for gateway config, webchat for chat |
| **Components** | Chat, sidebar, mode selector, model selector, settings, approval, automation (scripts, logs, error reports), context display | TUI; macOS/iOS/Android native UIs |
| **Design system** | Dedicated design-system page, theme toggle | Per-platform (SwiftUI, Kotlin, web) |

---

## 11. Native / mobile apps

| Platform | my-agent | OpenClaw |
|----------|----------|----------|
| **macOS** | ❌ | ✅ Menu bar app (Voice Wake, Talk, WebChat, remote gateway) |
| **iOS** | ❌ | ✅ Node (Canvas, Voice Wake, Talk, camera, Bonjour pairing) |
| **Android** | ❌ | ✅ Node (Canvas, Talk, camera, optional SMS) |
| **Voice** | ❌ | ✅ Voice Wake + Talk (ElevenLabs, etc.); TTS |

---

## 12. DevOps, observability & packaging

| Feature | my-agent | OpenClaw |
|---------|----------|----------|
| **Health** | `/health`, `/ready` | Gateway status; `openclaw doctor` |
| **Metrics** | Prometheus `/metrics` (if client installed) | Usage tracking, logging |
| **Install** | setup.sh, Python venv | `npm install -g openclaw`, `openclaw onboard --install-daemon` |
| **Daemon** | Run FastAPI (and optionally Telegram) | launchd/systemd user service for gateway |
| **Remote** | CORS, configurable | Tailscale Serve/Funnel, SSH tunnels |
| **CI** | .github (e.g. 1 *.yml) | 19 files in .github (workflows, labeler, etc.) |
| **Testing** | pytest (routing, API auth, memory, etc.) | Vitest (unit, e2e, live, docker, extensions) |

---

## 13. Summary: feature matrix (high level)

| Capability | my-agent | OpenClaw |
|------------|:--------:|:--------:|
| Single-user personal agent | ✅ | ✅ |
| Local-first / self-hostable | ✅ | ✅ |
| Intent-based model routing (content) | ✅ | ❌ |
| Privacy-forcing routing (e.g. PRIVATE/NSFW local) | ✅ | ❌ |
| Security “Judge” / output validation | ✅ | ❌ |
| Telegram | ✅ | ✅ |
| Web UI (dashboard/chat) | ✅ | ✅ |
| Multiple messaging channels | ❌ (Telegram only) | ✅ (many) |
| CLI (send, agent, gateway) | ❌ | ✅ |
| TUI | ❌ | ✅ |
| Native macOS/iOS/Android apps | ❌ | ✅ |
| Voice (wake, TTS, Talk) | ❌ | ✅ |
| Canvas / A2UI | ❌ | ✅ |
| Browser automation (CDP) | ❌ | ✅ |
| Device nodes (camera, screen, location) | ❌ | ✅ |
| Projects & conversations (API) | ✅ | Via sessions |
| Cron / automations / scripts (API + UI) | ✅ | ✅ (cron, webhooks, skills) |
| MCP servers (config) | ✅ | Different plugin model (extensions) |
| Skills registry (in-repo) | ✅ | ✅ + ClawHub |
| Open Prose / workflow language | ❌ | ✅ (extension) |
| Multi-agent / workspace routing | ❌ | ✅ |
| Agent-to-agent (sessions_*) | ❌ | ✅ |
| Prometheus metrics | ✅ | ❌ (usage/logging focus) |
| Backlog / PBI / roadmap (structured) | ✅ | AGENTS.md / docs |
| Neuro-supportive / AuDHD focus (stated) | ✅ | ❌ |

---

## 14. Gaps and possible directions

**If extending my-agent toward OpenClaw-like surface:**
- Add more channels (WhatsApp, Slack, Discord, etc.) or a generic “channel adapter” abstraction.
- Introduce a long-lived gateway (WebSocket) for sessions, presence, and multi-client access.
- Consider CLI (`openclaw`-style) for power users and scripting.
- Optional: native apps and voice (Voice Wake, Talk) for always-on, hands-free use.

**If OpenClaw wanted my-agent-style behaviour:**
- Intent-based routing (SPEED/QUALITY/PRIVATE/NSFW/CODING/FINANCE) and task-specific model assignment.
- “Trust but Verify” Judge + PII redaction for remote model outputs.
- Strong “sensitive always local” guarantee and explicit operating principles (Least Privilege, Neuro-Affirmative).

**Shared strengths:**
- Both are local-first, personal-assistant-oriented, and channel-aware.
- Both support multiple models and configuration-driven behaviour.
- Both have a concept of skills/capabilities and automation (cron, scripts, sessions/agents).

---

## 15. Recommendations for my-agent

Prioritised by alignment with VISION.md and operating principles (Local-First, Least Privilege, Trust but Verify, Neuro-Affirmative, Vendor Independence). Effort is indicative (S = small, M = medium, L = large).

### High priority (strong fit, high value)

1. **CLI for power users and scripting (M)**  
   Add a thin CLI (e.g. `myagent query "…"`, `myagent send "…"`) that calls the existing REST API. Enables scripting, cron, and terminal workflows without opening the web UI. No gateway required; keep FastAPI as the single backend.

2. **Second channel adapter (M)**  
   Introduce one additional channel (e.g. WhatsApp or Slack) via an adapter pattern similar to Telegram. Validates a generic “channel adapter” design and reduces single-channel dependency while staying within current architecture.

3. **Doctor / health and config check (S)**  
   Add an endpoint or CLI subcommand that checks: API key usage, CORS, routing config, MCP connectivity, Ollama reachability, and surfaces risky or misconfigured settings. Complements existing `/health` and `/ready` and supports “Trust but Verify” operations.

4. **Session and conversation continuity (M)**  
   Strengthen conversation/session semantics in the API and UI (e.g. explicit session IDs, optional summary/compaction) so that long-running context and “main” vs project sessions are first-class. Reduces cognitive load (Neuro-Affirmative) and prepares for multi-client or agent-to-agent use later.

### Medium priority (valuable, scope carefully)

5. **WebSocket or SSE for real-time status (M)**  
   Optional WebSocket (or long-lived SSE) for dashboard: live model status, Ollama availability, automation/cron updates. Improves observability without committing to a full OpenClaw-style gateway.

6. **Skills discovery and install gating (M)**  
   Extend the skills registry with optional discovery (e.g. a minimal “skill hub” or curated list) and install/enable gating so users can safely add skills. Keeps skills local-first and avoids unnecessary vendor lock-in.

7. **Structured chat commands (S)**  
   If adding more channels later, define a small set of slash-style commands (e.g. `/status`, `/reset`, `/think`) and document them. Enables consistent behaviour across Telegram and any future channel adapters.

### Lower priority / longer term

8. **Voice and TTS (L)**  
   Consider voice input (wake word or PTT) and TTS only if neuro-supportive or accessibility use cases justify it. Likely requires native or bridge components; keep core routing and security in the existing backend.

9. **Additional channels (L per channel)**  
   Each new channel (Discord, WhatsApp, etc.) is a substantial integration. Prioritise based on user need and maintenance cost; prefer adapter abstraction so intent-based routing and security stay central.

10. **Native apps (L)**  
    macOS/iOS/Android apps are a large investment. Only pursue if always-on, device-local actions (camera, screen, notifications) become a stated goal and align with Local-First and Least Privilege.

### What to keep from OpenClaw as reference only

- **Gateway-as-control-plane**: Useful pattern for multi-channel, multi-client setups; not necessary for my-agent’s current scale. Revisit if you add many channels and need presence/real-time coordination.
- **Open Prose / workflow language**: Rich but heavy; my-agent’s automation hub and scripts may be sufficient unless you need visual or declarative multi-step workflows.
- **ClawHub-style public registry**: Aligns with Vendor Independence only if self-hosted or minimal; avoid dependency on a single external registry.

### Summary

Focus first on **CLI**, **one extra channel adapter**, **doctor/health checks**, and **session/conversation continuity**. These reinforce local-first use, security hygiene, and neuro-supportive workflows without duplicating OpenClaw’s full surface. Re-evaluate voice, many channels, and native apps when roadmap and capacity support them.

---

This comparison is accurate as of the codebase state at the time of writing. OpenClaw’s docs live at https://docs.openclaw.ai; my-agent’s vision and architecture are in `VISION.md`, `ARCHITECTURE.md`, and `operating_principles.md`.
