#!/bin/bash

# 🛑 STOP ALL CYBERSECURITY PLATFORM SERVICES

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
WHITE='\033[1;37m'
NC='\033[0m'

echo -e "${WHITE}🛑 STOPPING CYBERSECURITY PLATFORM SERVICES${NC}"
echo -e "${WHITE}============================================${NC}"
echo -e "${BLUE}📅 $(date)${NC}"
echo ""

# Function to kill process by name
kill_process() {
    local process_name=$1
    local service_name=$2
    
    local pids=$(pgrep -f "$process_name" 2>/dev/null)
    if [ -n "$pids" ]; then
        echo -e "${YELLOW}🛑 Stopping $service_name...${NC}"
        kill $pids 2>/dev/null
        sleep 2
        
        # Force kill if still running
        local remaining=$(pgrep -f "$process_name" 2>/dev/null)
        if [ -n "$remaining" ]; then
            echo -e "${RED}   Force killing $service_name...${NC}"
            kill -9 $remaining 2>/dev/null
        fi
        echo -e "${GREEN}   ✅ $service_name stopped${NC}"
    else
        echo -e "${BLUE}   ℹ️  $service_name not running${NC}"
    fi
}

# Stop Backend Services
echo -e "${BLUE}🔧 STOPPING BACKEND SERVICES${NC}"
echo -e "${BLUE}=============================${NC}"
kill_process "uvicorn.*main:app" "FastAPI Backend"
kill_process "python.*main.py" "Python Backend"

# Stop Frontend Services
echo -e "${BLUE}🌐 STOPPING FRONTEND SERVICES${NC}"
echo -e "${BLUE}==============================${NC}"
kill_process "next.*dev" "Next.js Frontend"
kill_process "node.*next" "Node.js Frontend"

# Stop Docker Services (optional)
echo -e "${BLUE}🐳 STOPPING DOCKER SERVICES${NC}"
echo -e "${BLUE}============================${NC}"
if command -v docker-compose &> /dev/null; then
    if [ -f "docker-compose.yml" ]; then
        echo -e "${YELLOW}🛑 Stopping Docker containers...${NC}"
        docker-compose down 2>/dev/null || echo -e "${BLUE}   ℹ️  No Docker containers to stop${NC}"
    fi
fi

# Clean up PID files
echo -e "${BLUE}🧹 CLEANING UP${NC}"
echo -e "${BLUE}===============${NC}"
rm -f backend/backend.pid frontend/frontend.pid 2>/dev/null
echo -e "${GREEN}✅ PID files cleaned${NC}"

# Check if ports are free
echo -e "${BLUE}🔍 CHECKING PORTS${NC}"
echo -e "${BLUE}=================${NC}"

check_port() {
    local port=$1
    local service=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}   ⚠️  Port $port still in use ($service)${NC}"
    else
        echo -e "${GREEN}   ✅ Port $port is free ($service)${NC}"
    fi
}

check_port 3000 "Frontend"
check_port 8000 "Backend"
check_port 5432 "PostgreSQL"
check_port 6379 "Redis"

echo ""
echo -e "${WHITE}🎯 ALL SERVICES STOPPED${NC}"
echo -e "${WHITE}=======================${NC}"
echo -e "${GREEN}✅ Cybersecurity platform services have been stopped${NC}"
echo -e "${BLUE}📝 To restart, run: ./start_full_platform.sh${NC}"
echo -e "${BLUE}🧪 To test services, run: ./quick_test_all.sh${NC}"
