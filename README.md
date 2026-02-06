# Secure Personal Agentic Platform

A local-first, privacy-obsessed personal AI assistant and agentic platform.

## 🌟 Philosophy: Secure -> Private -> Cost-Conscious
This platform is purpose-built to act as a secure extension of the user. It takes inspiration from OpenClaw but applies a "Principle of Least Privilege" and a "Hybrid Privacy" model.

### Core Documentation
- **[Vision & Objectives](./VISION.md)**: The "Why" and high-level goals.
- **[Operating Principles](./operating_principles.md)**: The values driving every architectural decision. (Found in brain artifacts)
- **[Governance Rules](./.agent/rules/governance.md)**: Rules for the development lifecycle.

## 🚀 Key Features
- **Model Choice Engine**: Intelligently routes requests between local Ollama models and commercial APIs (Anthropic, Moonshot).
- **Privacy Vault**: Traps sensitive/NSFW/Personal data locally.
- **Peer-Review Security**: A local "Judge" model inspects outputs for threats or leaks.
- **Dual-Interface**: Concise Telegram bot for mobility + Rich Web Dashboard for deep work.
- **Workspace Integration**: Read-optimized access to Google GMail, Calendar, and Drive.

## 🛠 Tech Stack
- **Backend**: Python (FastAPI / Uvicorn)
- **Frontend**: Next.js (TypeScript / Tailwind)
- **AI Runtime**: Ollama (Local) + Anthropic/Moonshot (API)
- **Database**: Local Markdown / JSON (Memory System)

## 🏃 Quick Start
1. **Prerequisites**: Install [Ollama](https://ollama.com/) and pull `llama3` and `mistral`.
2. **Install**: `pip install -r requirements.txt`
3. **Run Controller**: `source ../my-agent-venv/bin/activate && PYTHONPATH=. python3 core/main.py`
4. **Run Dashboard**: `cd frontend && npm run dev`

---
*Created and maintained by the user in partnership with Google Antigravity.*
