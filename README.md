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
- **Automation Hub**: Sidebar section for agents, cron jobs, and automations; detail view at `/automation` for scripts, status logs, and error reports.

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

**Option A: Smart script (recommended)**
```bash
./manage.sh start          # Start all (Ollama, Backend, Frontend)
./manage.sh status         # Check what's running
./manage.sh stop           # Stop all
./manage.sh start backend  # Start only backend
./manage.sh stop ollama    # Stop only Ollama
./manage.sh cleanup       # Remove orphan venvs (../my-agent-venv, etc.)
```

**Option B: Manual**
```bash
# Backend (FastAPI on port 8001)
source venv/bin/activate
PYTHONPATH=. python3 -m core.main

# Frontend (Next.js on port 3000) – in another terminal
cd frontend && npm run dev
```
API at `http://localhost:8001` · Docs at `/docs` · Dashboard at `http://localhost:3000` · Automation Hub detail at `http://localhost:3000/automation`

### Optional
- Pull Ollama models: `ollama pull llama3` and `ollama pull mistral`
- Copy `.env.example` to `.env` and add API keys for Anthropic, Mistral, and Moonshot

### CLI (power users)
Run queries and send messages from the terminal:
```bash
# Query the agent
PYTHONPATH=. python3 -m scripts query "What's the weather like?"

# Send a message to your primary Telegram chat
PYTHONPATH=. python3 -m scripts send "Reminder: meeting at 3pm"

# Health and config check
PYTHONPATH=. python3 -m scripts doctor
```
Set `MYAGENT_API_URL` (default: http://localhost:8001) and `MYAGENT_API_KEY` if the backend requires auth. Use `--url <base_url>` to override the API URL per run.

### Testing
Ensure `./setup.sh` has been run first (venv and dependencies).

- **Backend:** `source venv/bin/activate && PYTHONPATH=. python3 -m pytest tests/ -v`
- **Coverage (optional):** `PYTHONPATH=. python3 -m pytest tests/ --cov=core --cov-report=term-missing`
- **Frontend:** `cd frontend && npm test`

---
*Created and maintained by the user in partnership with Google Antigravity.*
