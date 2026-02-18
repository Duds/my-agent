---
description: Standard development commands for the MyAgent (Secure Personal Agentic Platform) project
---

# Development Commands

## Starting Development

```bash
# One-time setup (create venv, install deps)
./setup.sh

# Start all services (Ollama, Backend, Frontend)
./manage.sh start

# Start specific service
./manage.sh start backend
./manage.sh start frontend
./manage.sh start ollama
```

## Manual Run (alternative to manage.sh)

```bash
# Backend (FastAPI on port 8001)
source venv/bin/activate
PYTHONPATH=. python3 -m core.main

# Frontend (Next.js on port 3000) - in another terminal
cd frontend && npm run dev
```

## Testing

```bash
# Backend tests
source venv/bin/activate && PYTHONPATH=. python3 -m pytest tests/ -v

# Backend tests with coverage
PYTHONPATH=. python3 -m pytest tests/ --cov=core --cov-report=term-missing

# Frontend tests
cd frontend && npm test
```

## CLI (power users)

```bash
# Query the agent
PYTHONPATH=. python3 -m scripts query "What's the weather like?"

# Send message to primary Telegram chat
PYTHONPATH=. python3 -m scripts send "Reminder: meeting at 3pm"

# Health and config check
PYTHONPATH=. python3 -m scripts doctor
```

## Critical Dependencies

Before major development tasks, check [ARCHITECTURE.md](../../ARCHITECTURE.md), [TODO.md](../../TODO.md), and [backlog/](../../backlog/) for design constraints and dependencies.
