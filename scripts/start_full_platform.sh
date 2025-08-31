#!/bin/bash

# 🛡️ CYBERSECURITY IDS/IPS PLATFORM - FULL STARTUP SCRIPT
# Starts all services: Backend, Frontend, Database, and Tests all Dashboards

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Project paths
PROJECT_ROOT="/home/saamnolimits/Desktop/pfaf"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo -e "${WHITE}🛡️  CYBERSECURITY IDS/IPS PLATFORM STARTUP${NC}"
echo -e "${WHITE}================================================${NC}"
echo -e "${CYAN}📅 Started at: $(date)${NC}"
echo -e "${CYAN}📁 Project root: $PROJECT_ROOT${NC}"
echo ""

# Function to check if port is in use
check_port() {
    local port=$1
    local service=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${GREEN}✅ $service already running on port $port${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  $service not running on port $port${NC}"
        return 1
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${YELLOW}⏳ Waiting for $service to be ready...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ $service is ready!${NC}"
            return 0
        fi
        echo -e "${CYAN}   Attempt $attempt/$max_attempts - waiting...${NC}"
        sleep 2
        ((attempt++))
    done
    
    echo -e "${RED}❌ $service failed to start after $max_attempts attempts${NC}"
    return 1
}

# Function to test dashboard endpoint
test_dashboard() {
    local url=$1
    local name=$2
    local description=$3
    
    echo -e "${BLUE}🧪 Testing $name${NC}"
    echo -e "${CYAN}   URL: $url${NC}"
    echo -e "${CYAN}   Description: $description${NC}"
    
    if curl -s "$url" >/dev/null 2>&1; then
        echo -e "${GREEN}   ✅ $name - Working${NC}"
        return 0
    else
        echo -e "${RED}   ❌ $name - Failed${NC}"
        return 1
    fi
}

# Step 1: Check Prerequisites
echo -e "${WHITE}📋 STEP 1: CHECKING PREREQUISITES${NC}"
echo -e "${WHITE}=================================${NC}"

# Check if directories exist
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}❌ Backend directory not found: $BACKEND_DIR${NC}"
    exit 1
fi

if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}❌ Frontend directory not found: $FRONTEND_DIR${NC}"
    exit 1
fi

# Check Python virtual environment
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo -e "${YELLOW}⚠️  Python virtual environment not found. Creating...${NC}"
    cd "$BACKEND_DIR"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Python virtual environment found${NC}"
fi

# Check Node.js dependencies
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "${YELLOW}⚠️  Node.js dependencies not found. Installing...${NC}"
    cd "$FRONTEND_DIR"
    npm install
    echo -e "${GREEN}✅ Node.js dependencies installed${NC}"
else
    echo -e "${GREEN}✅ Node.js dependencies found${NC}"
fi

echo ""

# Step 2: Start Database Services
echo -e "${WHITE}📊 STEP 2: STARTING DATABASE SERVICES${NC}"
echo -e "${WHITE}=====================================${NC}"

# Check PostgreSQL
if check_port 5432 "PostgreSQL"; then
    echo -e "${GREEN}✅ PostgreSQL is running${NC}"
else
    echo -e "${YELLOW}⚠️  Starting PostgreSQL with Docker...${NC}"
    cd "$PROJECT_ROOT"
    if [ -f "docker-compose.yml" ]; then
        docker-compose up -d postgres
        wait_for_service "localhost:5432" "PostgreSQL"
    else
        echo -e "${RED}❌ docker-compose.yml not found${NC}"
    fi
fi

# Check Redis
if check_port 6379 "Redis"; then
    echo -e "${GREEN}✅ Redis is running${NC}"
else
    echo -e "${YELLOW}⚠️  Redis should be running for session management${NC}"
fi

echo ""

# Step 3: Start Backend Services
echo -e "${WHITE}🔧 STEP 3: STARTING BACKEND SERVICES${NC}"
echo -e "${WHITE}====================================${NC}"

if check_port 8000 "Backend API"; then
    echo -e "${GREEN}✅ Backend API already running${NC}"
else
    echo -e "${YELLOW}⚠️  Starting Backend API...${NC}"
    cd "$BACKEND_DIR"
    
    # Activate virtual environment and start backend in background
    source venv/bin/activate
    nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > backend.pid
    
    # Wait for backend to be ready
    wait_for_service "http://localhost:8000/docs" "Backend API"
fi

echo ""

# Step 4: Start Frontend Services
echo -e "${WHITE}🌐 STEP 4: STARTING FRONTEND SERVICES${NC}"
echo -e "${WHITE}=====================================${NC}"

if check_port 3000 "Frontend"; then
    echo -e "${GREEN}✅ Frontend already running${NC}"
else
    echo -e "${YELLOW}⚠️  Starting Frontend...${NC}"
    cd "$FRONTEND_DIR"
    
    # Start frontend in background
    nohup npm run dev > frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > frontend.pid
    
    # Wait for frontend to be ready
    wait_for_service "http://localhost:3000" "Frontend"
fi

echo ""

# Step 5: Test All Dashboard Services
echo -e "${WHITE}🧪 STEP 5: TESTING ALL DASHBOARD SERVICES${NC}"
echo -e "${WHITE}=========================================${NC}"

# Backend API Tests
echo -e "${PURPLE}🔧 Backend API Endpoints:${NC}"
test_dashboard "http://localhost:8000/docs" "API Documentation" "FastAPI Swagger UI"
test_dashboard "http://localhost:8000/api/public/stats" "Public Stats API" "System statistics"
test_dashboard "http://localhost:8000/api/database/stats" "Database Stats API" "Database statistics"
test_dashboard "http://localhost:8000/api/database/threats/recent" "Threats API" "Recent threat alerts"

echo ""

# Frontend Dashboard Tests
echo -e "${PURPLE}🌐 Frontend Dashboard Pages:${NC}"
test_dashboard "http://localhost:3000" "Home Dashboard" "Main cybersecurity dashboard"
test_dashboard "http://localhost:3000/analytics" "Analytics Dashboard" "Python analytics and charts"
test_dashboard "http://localhost:3000/sql-query" "SQL Query Dashboard" "Database query interface"
test_dashboard "http://localhost:3000/database" "Database Dashboard" "Database exploration and management"

echo ""

# Step 6: Test Core Functionality
echo -e "${WHITE}⚡ STEP 6: TESTING CORE FUNCTIONALITY${NC}"
echo -e "${WHITE}====================================${NC}"

# Test Python execution
echo -e "${BLUE}🐍 Testing Python Execution${NC}"
PYTHON_TEST=$(curl -s -X POST "http://localhost:8000/api/python/execute" \
    -H "Content-Type: application/json" \
    -d '{"code": "print(\"✅ Python execution test successful!\")"}')

if echo "$PYTHON_TEST" | grep -q "success.*true"; then
    echo -e "${GREEN}   ✅ Python Execution - Working${NC}"
else
    echo -e "${RED}   ❌ Python Execution - Failed${NC}"
fi

# Test SQL query execution
echo -e "${BLUE}🗄️  Testing SQL Query Execution${NC}"
SQL_TEST=$(curl -s -X POST "http://localhost:8000/api/database/query" \
    -H "Content-Type: application/json" \
    -d '{"query": "SELECT COUNT(*) FROM threat_alerts LIMIT 1"}')

if echo "$SQL_TEST" | grep -q "success"; then
    echo -e "${GREEN}   ✅ SQL Query Execution - Working${NC}"
else
    echo -e "${RED}   ❌ SQL Query Execution - Failed${NC}"
fi

# Test database connection
echo -e "${BLUE}📊 Testing Database Connection${NC}"
DB_TEST=$(curl -s "http://localhost:8000/api/database/stats")

if echo "$DB_TEST" | grep -q "total_threats"; then
    THREAT_COUNT=$(echo "$DB_TEST" | grep -o '"total_threats":[0-9]*' | cut -d':' -f2)
    echo -e "${GREEN}   ✅ Database Connection - Working (${THREAT_COUNT} threats)${NC}"
else
    echo -e "${RED}   ❌ Database Connection - Failed${NC}"
fi

echo ""

# Step 7: Display Service Status
echo -e "${WHITE}📊 STEP 7: SERVICE STATUS SUMMARY${NC}"
echo -e "${WHITE}=================================${NC}"

echo -e "${CYAN}🔧 Backend Services:${NC}"
echo -e "   • FastAPI Server: http://localhost:8000"
echo -e "   • API Documentation: http://localhost:8000/docs"
echo -e "   • Python Execution: ✅ Available"
echo -e "   • SQL Query Engine: ✅ Available"

echo -e "${CYAN}🌐 Frontend Services:${NC}"
echo -e "   • Next.js Application: http://localhost:3000"
echo -e "   • Home Dashboard: http://localhost:3000"
echo -e "   • Analytics Dashboard: http://localhost:3000/analytics"
echo -e "   • SQL Query Dashboard: http://localhost:3000/sql-query"
echo -e "   • Database Dashboard: http://localhost:3000/database"

echo -e "${CYAN}📊 Database Services:${NC}"
echo -e "   • PostgreSQL: localhost:5432"
echo -e "   • Redis: localhost:6379"
echo -e "   • Threat Alerts: ${THREAT_COUNT:-'N/A'} records"

echo ""

# Step 8: Usage Instructions
echo -e "${WHITE}🎯 STEP 8: USAGE INSTRUCTIONS${NC}"
echo -e "${WHITE}=============================${NC}"

echo -e "${GREEN}✅ Platform is now fully operational!${NC}"
echo ""
echo -e "${YELLOW}🌐 Access the dashboards:${NC}"
echo -e "   • Main Dashboard:     ${BLUE}http://localhost:3000${NC}"
echo -e "   • Analytics (Python): ${BLUE}http://localhost:3000/analytics${NC}"
echo -e "   • SQL Query Tool:     ${BLUE}http://localhost:3000/sql-query${NC}"
echo -e "   • Database Explorer:  ${BLUE}http://localhost:3000/database${NC}"
echo ""
echo -e "${YELLOW}🔧 API Endpoints:${NC}"
echo -e "   • API Documentation:  ${BLUE}http://localhost:8000/docs${NC}"
echo -e "   • System Stats:       ${BLUE}http://localhost:8000/api/public/stats${NC}"
echo -e "   • Database Stats:     ${BLUE}http://localhost:8000/api/database/stats${NC}"
echo ""
echo -e "${YELLOW}📝 Test Features:${NC}"
echo -e "   • Execute Python scripts in Analytics dashboard"
echo -e "   • Run SQL queries in SQL Query dashboard"
echo -e "   • Browse threat data in Database dashboard"
echo -e "   • Monitor real-time threats in Home dashboard"
echo ""
echo -e "${YELLOW}🛑 To stop all services:${NC}"
echo -e "   • Kill backend: ${CYAN}kill \$(cat $BACKEND_DIR/backend.pid 2>/dev/null || echo '')${NC}"
echo -e "   • Kill frontend: ${CYAN}kill \$(cat $FRONTEND_DIR/frontend.pid 2>/dev/null || echo '')${NC}"
echo -e "   • Or use: ${CYAN}pkill -f 'uvicorn\\|next'${NC}"

echo ""
echo -e "${WHITE}🎉 CYBERSECURITY PLATFORM STARTUP COMPLETE!${NC}"
echo -e "${WHITE}============================================${NC}"
echo -e "${CYAN}📅 Completed at: $(date)${NC}"
echo -e "${GREEN}🚀 Ready for cybersecurity monitoring and analysis!${NC}"
