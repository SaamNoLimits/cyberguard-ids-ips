# 🛡️ Cybersecurity IDS/IPS Platform - Management Scripts

This document describes the shell scripts for managing the full cybersecurity platform.

## 📋 Available Scripts

### 1. 🚀 `start_full_platform.sh` - Complete Platform Startup
**Full platform startup with comprehensive testing**

```bash
./start_full_platform.sh
```

**What it does:**
- ✅ Checks prerequisites (Python venv, Node.js dependencies)
- 🗄️ Starts database services (PostgreSQL, Redis)
- 🔧 Starts backend API server (FastAPI on port 8000)
- 🌐 Starts frontend application (Next.js on port 3000)
- 🧪 Tests all dashboard endpoints
- ⚡ Tests core functionality (Python execution, SQL queries)
- 📊 Displays comprehensive service status
- 📝 Shows usage instructions

**Services Started:**
- Backend API: `http://localhost:8000`
- Frontend App: `http://localhost:3000`
- API Docs: `http://localhost:8000/docs`

---

### 2. 🧪 `quick_test_all.sh` - Quick Service Testing
**Fast testing of all services without starting them**

```bash
./quick_test_all.sh
```

**What it tests:**
- 🔧 **Backend Services**: API docs, stats, database, threats
- 🌐 **Frontend Dashboards**: Home, Analytics, SQL Query, Database
- ⚡ **Core Functionality**: Python execution, SQL queries, DB connection

**Sample Output:**
```
🔧 BACKEND SERVICES
API Documentation:       ✅ Working - FastAPI Swagger UI
Database Stats:          ✅ Working - Database info

🌐 FRONTEND DASHBOARDS  
Analytics:               ✅ Working - Python analytics & charts
SQL Query:               ✅ Working - Database query interface

⚡ CORE FUNCTIONALITY
Python Execution:        ✅ Working - Python scripts execute
Database Connection:     ✅ Working - 18154 threats in database
```

---

### 3. 🛑 `stop_all_services.sh` - Stop All Services
**Gracefully stops all platform services**

```bash
./stop_all_services.sh
```

**What it does:**
- 🛑 Stops FastAPI backend processes
- 🛑 Stops Next.js frontend processes
- 🐳 Stops Docker containers (if running)
- 🧹 Cleans up PID files
- 🔍 Checks that ports are free

---

## 🌐 Dashboard URLs

Once the platform is running, access these dashboards:

| Dashboard | URL | Description |
|-----------|-----|-------------|
| **Home Dashboard** | `http://localhost:3000` | Main cybersecurity monitoring |
| **Analytics Dashboard** | `http://localhost:3000/analytics` | Python scripts & data visualization |
| **SQL Query Dashboard** | `http://localhost:3000/sql-query` | Database query interface |
| **Database Dashboard** | `http://localhost:3000/database` | Database exploration & management |
| **API Documentation** | `http://localhost:8000/docs` | FastAPI Swagger UI |

## 🔧 Backend API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/public/stats` | GET | System statistics |
| `/api/database/stats` | GET | Database statistics |
| `/api/database/threats/recent` | GET | Recent threat alerts |
| `/api/database/query` | POST | Execute SQL queries |
| `/api/python/execute` | POST | Execute Python scripts |

## 📊 Platform Features

### ✅ Working Features:
- **🛡️ Threat Monitoring**: Real-time cybersecurity alerts (18,154+ threats)
- **🐍 Python Analytics**: Execute Python scripts with matplotlib charts
- **🗄️ SQL Queries**: Database exploration with SELECT queries
- **📊 Data Visualization**: Charts and graphs from threat data
- **🌐 Web Interface**: Modern React/Next.js dashboards
- **🔧 API Integration**: RESTful API with FastAPI
- **📈 Real-time Updates**: Live threat monitoring

### 🎯 Dashboard Capabilities:
- **Analytics**: Python script execution, chart generation, database analysis
- **SQL Query**: Splunk-like query interface with sample queries
- **Database**: Threat browsing, filtering, pagination, PCAP downloads
- **Home**: Real-time monitoring, statistics, threat alerts

## 🚀 Quick Start

1. **Start Everything:**
   ```bash
   ./start_full_platform.sh
   ```

2. **Test All Services:**
   ```bash
   ./quick_test_all.sh
   ```

3. **Access Dashboards:**
   - Open `http://localhost:3000` in your browser
   - Navigate between dashboards using the sidebar

4. **Stop When Done:**
   ```bash
   ./stop_all_services.sh
   ```

## 🔍 Troubleshooting

### If services don't start:
- Check if ports 3000, 8000, 5432, 6379 are available
- Ensure Python virtual environment exists: `backend/venv/`
- Ensure Node.js dependencies installed: `frontend/node_modules/`

### If dashboards show errors:
- Run `./quick_test_all.sh` to identify issues
- Check browser console for JavaScript errors
- Verify backend API is responding: `http://localhost:8000/docs`

### If database connection fails:
- Ensure PostgreSQL is running on port 5432
- Check database credentials in backend `.env` file
- Verify database `cybersec_ids` exists with threat data

## 📝 Logs

- **Backend logs**: `backend/backend.log`
- **Frontend logs**: `frontend/frontend.log`
- **Docker logs**: `docker-compose logs`

---

**🎉 Your cybersecurity platform is ready for threat monitoring and analysis!**
