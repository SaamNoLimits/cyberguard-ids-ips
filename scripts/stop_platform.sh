#!/bin/bash

# Stop Cybersecurity IDS/IPS Platform
echo "🛑 Stopping Cybersecurity IDS/IPS Platform..."

# Kill processes by PID if files exist
if [ -f .backend_pid ]; then
    BACKEND_PID=$(cat .backend_pid)
    echo "🔌 Stopping backend (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null
    rm -f .backend_pid
fi

if [ -f .frontend_pid ]; then
    FRONTEND_PID=$(cat .frontend_pid)
    echo "🔌 Stopping frontend (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null
    rm -f .frontend_pid
fi

# Kill any remaining processes on the ports
echo "🧹 Cleaning up remaining processes..."
pkill -f "uvicorn main:app" 2>/dev/null
pkill -f "next dev" 2>/dev/null
pkill -f "npm run dev" 2>/dev/null
pkill -f "pnpm dev" 2>/dev/null

# Kill processes using the ports
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null

echo "✅ Platform stopped successfully"
