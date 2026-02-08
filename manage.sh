#!/bin/bash

# Configuration
BACKEND_PORT=8001
FRONTEND_PORT=3000
OLLAMA_PORT=11434
VENV_PATH="../my-agent-venv"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create logs directory if it doesn't exist
mkdir -p logs

status() {
    echo "Checking service status..."
    
    # Check Ollama
    if lsof -i :$OLLAMA_PORT > /dev/null; then
        echo -e "Ollama:  [${GREEN}RUNNING${NC}] (Port $OLLAMA_PORT)"
    else
        echo -e "Ollama:  [${RED}STOPPED${NC}]"
    fi

    # Check Backend
    if lsof -i :$BACKEND_PORT > /dev/null; then
        echo -e "Backend: [${GREEN}RUNNING${NC}] (Port $BACKEND_PORT)"
    else
        echo -e "Backend: [${RED}STOPPED${NC}]"
    fi

    # Check Frontend
    if lsof -i :$FRONTEND_PORT > /dev/null; then
        echo -e "Frontend:[${GREEN}RUNNING${NC}] (Port $FRONTEND_PORT)"
    else
        echo -e "Frontend:[${RED}STOPPED${NC}]"
    fi
}

start() {
    echo "Starting services intelligently..."

    # 1. Start Ollama if not running
    if ! lsof -i :$OLLAMA_PORT > /dev/null; then
        echo "Starting Ollama..."
        nohup ollama serve > logs/ollama.log 2>&1 &
        echo "Waiting for Ollama to respond..."
        MAX_WAIT=30
        WAIT_COUNT=0
        until curl -s http://localhost:$OLLAMA_PORT > /dev/null || [ $WAIT_COUNT -eq $MAX_WAIT ]; do
            sleep 1
            ((WAIT_COUNT++))
        done
        if [ $WAIT_COUNT -eq $MAX_WAIT ]; then
            echo -e "${RED}Error: Ollama failed to start within $MAX_WAIT seconds.${NC}"
        else
            echo "Ollama is ready."
        fi
    else
        echo "Ollama is already running."
    fi

    # 2. Start Backend if not running
    if ! lsof -i :$BACKEND_PORT > /dev/null; then
        echo "Starting Backend..."
        if [ -d "$VENV_PATH" ]; then
            source $VENV_PATH/bin/activate
        else
            echo -e "${YELLOW}Warning: Virtual environment not found at $VENV_PATH. Using system python.${NC}"
        fi
        PYTHONPATH=. nohup python3 core/main.py > logs/backend.log 2>&1 &
        echo "Waiting for Backend to respond..."
        MAX_WAIT=10
        WAIT_COUNT=0
        until curl -s http://localhost:$BACKEND_PORT/health > /dev/null || [ $WAIT_COUNT -eq $MAX_WAIT ]; do
            sleep 1
            ((WAIT_COUNT++))
        done
        if [ $WAIT_COUNT -eq $MAX_WAIT ]; then
            echo -e "${RED}Error: Backend failed to start within $MAX_WAIT seconds.${NC}"
        else
            echo "Backend is ready."
        fi
    else
        echo "Backend is already running."
    fi

    # 3. Start Frontend if not running
    if ! lsof -i :$FRONTEND_PORT > /dev/null; then
        echo "Starting Frontend..."
        cd frontend && nohup npm run dev > ../logs/frontend.log 2>&1 &
        cd ..
        echo "Waiting for Frontend to respond..."
        MAX_WAIT=30
        WAIT_COUNT=0
        until curl -s http://localhost:$FRONTEND_PORT > /dev/null || [ $WAIT_COUNT -eq $MAX_WAIT ]; do
            sleep 1
            ((WAIT_COUNT++))
        done
        if [ $WAIT_COUNT -eq $MAX_WAIT ]; then
            echo -e "${RED}Error: Frontend failed to start within $MAX_WAIT seconds.${NC}"
        else
            echo "Frontend is ready."
        fi
    else
        echo "Frontend is already running."
    fi

    if lsof -i :$FRONTEND_PORT > /dev/null; then
        echo -e "${GREEN}All services started successfully!${NC}"
        echo "Opening http://localhost:$FRONTEND_PORT in browser..."
        open http://localhost:$FRONTEND_PORT
    else
        echo -e "${RED}Process completed but some services might not be running. Run '$0 status' to check.${NC}"
    fi
}

stop() {
    echo "Stopping services..."
    
    # Kill backend
    BACKEND_PID=$(lsof -t -i :$BACKEND_PORT)
    if [ ! -z "$BACKEND_PID" ]; then
        echo "Stopping Backend (PID $BACKEND_PID)..."
        kill $BACKEND_PID
    fi

    # Kill frontend
    FRONTEND_PID=$(lsof -t -i :$FRONTEND_PORT)
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "Stopping Frontend (PID $FRONTEND_PID)..."
        # Try graceful first
        kill $FRONTEND_PID
        sleep 1
        # Hard kill leftovers if any (npm run dev often spawns children)
        pkill -f "next-dev" 2>/dev/null
    fi
    
    echo -e "${GREEN}Done.${NC}"
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    status)
        status
        ;;
    restart)
        stop
        sleep 2
        start
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart}"
        exit 1
esac
