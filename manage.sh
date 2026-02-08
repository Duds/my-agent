#!/bin/bash

# Secure Personal Agentic Platform - Service Management
# Usage: ./manage.sh {start|stop|status|restart|cleanup} [ollama|backend|frontend|all]
#   start [service]  - Start all or specific service(s)
#   stop [service]   - Stop all or specific service(s). Default: all.
#   status           - Show what's running
#   restart [service]- Stop then start

# Resolve script location (works when run from any directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Single venv location: venv/ inside this project only
# Use VENV_PATH env to override
VENV_PATH="${VENV_PATH:-$PROJECT_ROOT/venv}"
if [ ! -f "$VENV_PATH/bin/activate" ]; then
    VENV_PATH=""
fi

# Configuration
BACKEND_PORT=8001
FRONTEND_PORT=3000
OLLAMA_PORT=11434
LOGS_DIR="$PROJECT_ROOT/logs"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

mkdir -p "$LOGS_DIR"

# --- Status helpers ---
is_ollama_running() { lsof -i :$OLLAMA_PORT > /dev/null 2>&1; }
is_backend_running() { lsof -i :$BACKEND_PORT > /dev/null 2>&1; }
is_frontend_running() { lsof -i :$FRONTEND_PORT > /dev/null 2>&1; }

status() {
    echo "Service status:"
    echo ""
    if [ -n "$VENV_PATH" ]; then
        echo -e "  Venv:   [${GREEN}OK${NC}] $VENV_PATH"
    else
        echo -e "  Venv:   [${RED}NOT FOUND${NC}] Run ./setup.sh to create venv/"
    fi
    echo ""
    if is_ollama_running; then
        echo -e "  Ollama:  [${GREEN}RUNNING${NC}] (Port $OLLAMA_PORT)"
    else
        echo -e "  Ollama:  [${RED}STOPPED${NC}]"
    fi
    if is_backend_running; then
        echo -e "  Backend: [${GREEN}RUNNING${NC}] (Port $BACKEND_PORT)"
    else
        echo -e "  Backend: [${RED}STOPPED${NC}]"
    fi
    if is_frontend_running; then
        echo -e "  Frontend:[${GREEN}RUNNING${NC}] (Port $FRONTEND_PORT)"
    else
        echo -e "  Frontend:[${RED}STOPPED${NC}]"
    fi
}

# --- Start helpers ---
start_ollama() {
    if is_ollama_running; then
        echo "Ollama is already running."
        return 0
    fi
    echo "Starting Ollama..."
    nohup ollama serve > "$LOGS_DIR/ollama.log" 2>&1 &
    MAX_WAIT=30
    WAIT_COUNT=0
    until curl -s http://localhost:$OLLAMA_PORT > /dev/null 2>&1 || [ $WAIT_COUNT -eq $MAX_WAIT ]; do
        sleep 1
        ((WAIT_COUNT++))
    done
    if [ $WAIT_COUNT -eq $MAX_WAIT ]; then
        echo -e "${RED}Error: Ollama failed to start within $MAX_WAIT seconds.${NC}"
        return 1
    fi
    echo "Ollama is ready."
    return 0
}

start_backend() {
    if is_backend_running; then
        echo "Backend is already running."
        return 0
    fi
    echo "Starting Backend..."
    if [ -n "$VENV_PATH" ] && [ -f "$VENV_PATH/bin/activate" ]; then
        (cd "$PROJECT_ROOT" && source "$VENV_PATH/bin/activate" && PYTHONPATH=. nohup python3 -m core.main > "$LOGS_DIR/backend.log" 2>&1 &)
    else
        echo -e "${YELLOW}Warning: No venv/ found. Run ./setup.sh to create one.${NC}"
        (cd "$PROJECT_ROOT" && PYTHONPATH=. nohup python3 -m core.main > "$LOGS_DIR/backend.log" 2>&1 &)
    fi
    MAX_WAIT=10
    WAIT_COUNT=0
    until curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1 || [ $WAIT_COUNT -eq $MAX_WAIT ]; do
        sleep 1
        ((WAIT_COUNT++))
    done
    if [ $WAIT_COUNT -eq $MAX_WAIT ]; then
        echo -e "${RED}Error: Backend failed to start within $MAX_WAIT seconds.${NC}"
        return 1
    fi
    echo "Backend is ready."
    return 0
}

start_frontend() {
    if is_frontend_running; then
        echo "Frontend is already running."
        return 0
    fi
    echo "Starting Frontend..."
    (cd "$PROJECT_ROOT/frontend" && nohup npm run dev > "$LOGS_DIR/frontend.log" 2>&1 &)
    MAX_WAIT=30
    WAIT_COUNT=0
    until curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1 || [ $WAIT_COUNT -eq $MAX_WAIT ]; do
        sleep 1
        ((WAIT_COUNT++))
    done
    if [ $WAIT_COUNT -eq $MAX_WAIT ]; then
        echo -e "${RED}Error: Frontend failed to start within $MAX_WAIT seconds.${NC}"
        return 1
    fi
    echo "Frontend is ready."
    return 0
}

# --- Stop helpers ---
stop_ollama() {
    if ! is_ollama_running; then
        echo "Ollama is not running."
        return 0
    fi
    echo "Stopping Ollama..."
    pkill ollama 2>/dev/null || true
    sleep 2
    if is_ollama_running; then
        echo -e "${RED}Ollama may still be running. Try: pkill -9 ollama${NC}"
        return 1
    fi
    echo "Ollama stopped."
    return 0
}

stop_backend() {
    if ! is_backend_running; then
        echo "Backend is not running."
        return 0
    fi
    BACKEND_PID=$(lsof -t -i :$BACKEND_PORT)
    echo "Stopping Backend (PID $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null || true
    sleep 2
    if is_backend_running; then
        kill -9 $BACKEND_PID 2>/dev/null || true
    fi
    echo "Backend stopped."
    return 0
}

stop_frontend() {
    if ! is_frontend_running; then
        echo "Frontend is not running."
        return 0
    fi
    FRONTEND_PID=$(lsof -t -i :$FRONTEND_PORT)
    echo "Stopping Frontend (PID $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null || true
    sleep 1
    pkill -f "next-dev" 2>/dev/null || true
    echo "Frontend stopped."
    return 0
}

# --- Main commands ---
start() {
    local service="${1:-all}"
    echo "Starting $service..."
    echo ""

    case "$service" in
        ollama)
            start_ollama
            ;;
        backend)
            start_backend
            ;;
        frontend)
            start_frontend
            ;;
        all)
            start_ollama
            start_backend
            start_frontend
            if is_frontend_running; then
                echo ""
                echo -e "${GREEN}All services started.${NC}"
                echo "Opening http://localhost:$FRONTEND_PORT ..."
                open http://localhost:$FRONTEND_PORT 2>/dev/null || true
            fi
            ;;
        *)
            echo -e "${RED}Unknown service: $service${NC}"
            echo "Use: ollama | backend | frontend | all"
            exit 1
            ;;
    esac
}

stop() {
    local service="${1:-all}"
    echo "Stopping $service..."
    echo ""

    case "$service" in
        ollama)
            stop_ollama
            ;;
        backend)
            stop_backend
            ;;
        frontend)
            stop_frontend
            ;;
        all)
            stop_backend
            stop_frontend
            stop_ollama
            echo -e "${GREEN}All services stopped.${NC}"
            ;;
        *)
            echo -e "${RED}Unknown service: $service${NC}"
            echo "Use: ollama | backend | frontend | all"
            exit 1
            ;;
    esac
}

cleanup() {
    echo "Removing unused my-agent venvs (keeps venv/ inside this project only)..."
    local removed=0
    for candidate in \
        "$PROJECT_ROOT/../my-agent-venv" \
        "$PROJECT_ROOT/my-agent-venv"; do
        if [ -d "$candidate" ] && [ -f "$candidate/bin/activate" ]; then
            echo "  Removing $candidate"
            rm -rf "$candidate"
            removed=$((removed + 1))
        fi
    done
    if [ $removed -eq 0 ]; then
        echo "  Nothing to remove (no orphan venvs found)."
    else
        echo -e "${GREEN}Removed $removed unused venv(s).${NC}"
    fi
}

# --- Entry point ---
case "${1:-}" in
    start)
        start "${2:-all}"
        ;;
    stop)
        stop "${2:-all}"
        ;;
    status)
        status
        ;;
    restart)
        stop "${2:-all}"
        sleep 2
        start "${2:-all}"
        ;;
    cleanup)
        cleanup
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart|cleanup} [ollama|backend|frontend|all]"
        echo ""
        echo "  start [service]   Start all (default) or specific service"
        echo "  stop [service]    Stop all (default) or specific service"
        echo "  status            Show what's running"
        echo "  restart [service] Stop then start"
        echo "  cleanup           Remove orphan venvs (../my-agent-venv, etc.)"
        exit 1
        ;;
esac
