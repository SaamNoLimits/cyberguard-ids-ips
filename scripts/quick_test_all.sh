#!/bin/bash

# 🚀 QUICK TEST ALL SERVICES - Cybersecurity Platform
# Tests all dashboards and services without starting them

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

echo -e "${WHITE}🚀 QUICK TEST ALL CYBERSECURITY SERVICES${NC}"
echo -e "${WHITE}========================================${NC}"
echo -e "${CYAN}📅 $(date)${NC}"
echo ""

# Function to test service
test_service() {
    local url=$1
    local name=$2
    local description=$3
    
    printf "%-25s" "$name:"
    if curl -s "$url" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Working${NC} - $description"
        return 0
    else
        echo -e "${RED}❌ Failed${NC} - $description"
        return 1
    fi
}

# Test Backend Services
echo -e "${BLUE}🔧 BACKEND SERVICES${NC}"
echo -e "${BLUE}==================${NC}"
test_service "http://localhost:8000/docs" "API Documentation" "FastAPI Swagger UI"
test_service "http://localhost:8000/api/public/stats" "Public Stats" "System statistics"
test_service "http://localhost:8000/api/database/stats" "Database Stats" "Database info"
test_service "http://localhost:8000/api/database/threats/recent" "Threats API" "Recent alerts"

echo ""

# Test Frontend Dashboards
echo -e "${BLUE}🌐 FRONTEND DASHBOARDS${NC}"
echo -e "${BLUE}=====================${NC}"
test_service "http://localhost:3000" "Home Dashboard" "Main cybersecurity dashboard"
test_service "http://localhost:3000/analytics" "Analytics" "Python analytics & charts"
test_service "http://localhost:3000/sql-query" "SQL Query" "Database query interface"
test_service "http://localhost:3000/database" "Database" "Database exploration"

echo ""

# Test Core Functionality
echo -e "${BLUE}⚡ CORE FUNCTIONALITY${NC}"
echo -e "${BLUE}====================${NC}"

# Test Python execution
printf "%-25s" "Python Execution:"
PYTHON_TEST=$(curl -s -X POST "http://localhost:8000/api/python/execute" \
    -H "Content-Type: application/json" \
    -d '{"code": "print(\"Test successful!\")"}' 2>/dev/null)

if echo "$PYTHON_TEST" | grep -q "success.*true"; then
    echo -e "${GREEN}✅ Working${NC} - Python scripts execute"
else
    echo -e "${RED}❌ Failed${NC} - Python execution error"
fi

# Test SQL query
printf "%-25s" "SQL Query:"
SQL_TEST=$(curl -s -X POST "http://localhost:8000/api/database/query" \
    -H "Content-Type: application/json" \
    -d '{"query": "SELECT COUNT(*) FROM threat_alerts LIMIT 1"}' 2>/dev/null)

if echo "$SQL_TEST" | grep -q "success"; then
    echo -e "${GREEN}✅ Working${NC} - SQL queries execute"
else
    echo -e "${RED}❌ Failed${NC} - SQL query error"
fi

# Test database connection
printf "%-25s" "Database Connection:"
DB_TEST=$(curl -s "http://localhost:8000/api/database/stats" 2>/dev/null)

if echo "$DB_TEST" | grep -q "total_threats"; then
    THREAT_COUNT=$(echo "$DB_TEST" | grep -o '"total_threats":[0-9]*' | cut -d':' -f2)
    echo -e "${GREEN}✅ Working${NC} - ${THREAT_COUNT} threats in database"
else
    echo -e "${RED}❌ Failed${NC} - Database connection error"
fi

echo ""

# Quick Access URLs
echo -e "${YELLOW}🌐 QUICK ACCESS URLS${NC}"
echo -e "${YELLOW}===================${NC}"
echo -e "Main Dashboard:     ${CYAN}http://localhost:3000${NC}"
echo -e "Analytics (Python): ${CYAN}http://localhost:3000/analytics${NC}"
echo -e "SQL Query Tool:     ${CYAN}http://localhost:3000/sql-query${NC}"
echo -e "Database Explorer:  ${CYAN}http://localhost:3000/database${NC}"
echo -e "API Documentation:  ${CYAN}http://localhost:8000/docs${NC}"

echo ""
echo -e "${WHITE}🎯 TEST COMPLETE!${NC}"
