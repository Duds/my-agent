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

### Prerequisites
- [Ollama](https://ollama.com/) — install and run `ollama serve`
- Python 3.10+ with virtual environment
- Node.js 18+ and npm

### One-time setup
```bash
./setup.sh
# Or manually: create venv, pip install -r requirements.txt, cd frontend && npm install
```

### Running the Application

**Backend** (FastAPI on port 8001):
```bash
source ../my-agent-venv/bin/activate
PYTHONPATH=. python3 core/main.py
```
API available at `http://localhost:8001` · Docs at `/docs` and `/redoc`.

**Frontend** (Next.js on port 3000):
```bash
cd frontend && npm run dev
```
Dashboard at `http://localhost:3000`. Ensure the backend is running for full functionality.

### Optional
- Pull Ollama models: `ollama pull llama3` and `ollama pull mistral`
- Copy `.env.example` to `.env` and add API keys for Anthropic, Mistral, and Moonshot

---
*Created and maintained by the user in partnership with Google Antigravity.*
