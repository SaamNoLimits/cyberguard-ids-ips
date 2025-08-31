# CyberGuard IDS/IPS Platform - Project Structure

## 📁 Complete Directory Structure

```
pfaf/                                    # Root project directory
├── README.md                           # Main project documentation
├── PROJECT_STRUCTURE.md               # This file - project organization
│
├── 🔧 backend/                         # Backend FastAPI Application
│   ├── backend/                       # Core backend code
│   │   ├── main.py                   # FastAPI application entry point
│   │   ├── services/                 # Business logic services
│   │   │   ├── ids_service.py       # Intrusion Detection Service
│   │   │   ├── network_monitor.py   # Network monitoring
│   │   │   ├── database_service.py  # Database operations
│   │   │   └── websocket_manager.py # WebSocket management
│   │   └── .env                     # Environment configuration
│   │
│   ├── analytics/                    # Analytics and dashboard scripts
│   │   ├── dashboard_analytics_script_for_interface.py
│   │   └── real_time_dashboard_script.py
│   │
│   ├── scripts/                      # Backend utility scripts
│   │   ├── prepare_attack_detection.py
│   │   └── simulate_nmap_attack.py
│   │
│   ├── tests/                        # Backend tests and demos
│   │   ├── demo_complete_system.py
│   │   ├── demo_final_system.sh
│   │   ├── demo_image_display.py
│   │   ├── test_analytics_frontend.py
│   │   ├── test_analytics_page.py
│   │   ├── test_complete_system.py
│   │   ├── test_database_page.py
│   │   ├── test_image_script.py
│   │   └── test_sql_query.py
│   │
│   ├── create_reports_tables.sql     # Database schema
│   ├── docker-compose.yml            # Docker services configuration
│   ├── generate_sample_threats.py    # Sample data generation
│   ├── monitor_attacks.py            # Attack monitoring utilities
│   └── venv/                         # Python virtual environment
│
├── 🎨 frontend/                        # Next.js React Frontend
│   ├── app/                          # Next.js 13+ app directory
│   │   ├── page.tsx                 # Home dashboard
│   │   ├── analytics/               # Analytics page
│   │   ├── database/                # Database explorer
│   │   ├── reports/                 # Reports management
│   │   ├── sql-query/               # SQL query interface
│   │   ├── threat-monitoring/       # Real-time threat monitoring
│   │   └── layout.tsx               # Main layout with navigation
│   │
│   ├── components/                   # Reusable React components
│   │   ├── ui/                      # Base UI components (Radix UI)
│   │   ├── python-analytics-dashboard.tsx
│   │   ├── simple-database-dashboard.tsx
│   │   ├── threat-details-modal.tsx
│   │   └── main-navigation.tsx
│   │
│   ├── lib/                          # Frontend utilities
│   │   ├── api.ts                   # API client
│   │   └── utils.ts                 # Utility functions
│   │
│   ├── package.json                  # Node.js dependencies
│   ├── tailwind.config.js           # Tailwind CSS configuration
│   └── next.config.js               # Next.js configuration
│
├── 🤖 ml-iot/                          # Machine Learning Models
│   ├── iot_ids_lightgbm_20250819_132715.pkl  # Pre-trained LightGBM model
│   ├── IoT_CIC_Dataset_Analysis.ipynb        # Jupyter notebook analysis
│   └── model_training/                        # Training scripts and data
│
├── 🚀 scripts/                         # Platform Management Scripts
│   ├── start_full_platform.sh       # Complete platform startup
│   ├── quick_test_all.sh            # Quick service testing
│   ├── stop_all_services.sh         # Graceful shutdown
│   ├── validate_system.py           # System validation
│   ├── validate_real_time_system.sh # Real-time system validation
│   └── test_complete_functionality.sh # Functionality testing
│
├── 📚 docs/                           # Documentation
│   ├── README.md                    # Original documentation
│   └── PLATFORM_SCRIPTS.md         # Script usage documentation
│
└── 🧪 tests/                          # Integration Tests
    └── (Integration test files)
```

## 🎯 Key Components

### Backend Services (`/backend/backend/`)
- **main.py**: FastAPI application with all API endpoints
- **services/ids_service.py**: Core intrusion detection logic
- **services/network_monitor.py**: Real-time network packet capture
- **services/database_service.py**: PostgreSQL database operations
- **services/websocket_manager.py**: Real-time WebSocket communications

### Frontend Pages (`/frontend/app/`)
- **page.tsx**: Main dashboard with system overview
- **threat-monitoring/**: Real-time threat detection interface
- **analytics/**: Python script execution with visualization
- **database/**: Database explorer and statistics
- **reports/**: Incident report management
- **sql-query/**: Custom SQL query interface

### Analytics Scripts (`/backend/analytics/`)
- **dashboard_analytics_script_for_interface.py**: Dashboard analytics
- **real_time_dashboard_script.py**: Real-time monitoring scripts

### Management Scripts (`/scripts/`)
- **start_full_platform.sh**: One-command platform startup
- **quick_test_all.sh**: Rapid service health checks
- **stop_all_services.sh**: Clean platform shutdown
- **validate_system.py**: Comprehensive system validation

## 🔄 Data Flow

```
Network Traffic → ML Model → IDS Service → Database → WebSocket → Frontend
                     ↓
                 Threat Detection → Alert Generation → User Interface
```

## 🛠️ Development Workflow

### 1. Backend Development
```bash
cd backend/backend
source ../venv/bin/activate
python main.py
```

### 2. Frontend Development
```bash
cd frontend
npm run dev
```

### 3. Full Platform Testing
```bash
./scripts/start_full_platform.sh
./scripts/quick_test_all.sh
```

### 4. Analytics Development
```bash
cd backend/analytics
python dashboard_analytics_script_for_interface.py
```

## 📊 API Structure

### Core Endpoints
- **Threats**: `/api/threats/*` - Threat management
- **Reports**: `/api/reports/*` - Incident reporting
- **Database**: `/api/database/*` - Database operations
- **Analytics**: `/api/python/execute` - Script execution
- **WebSocket**: `/ws` - Real-time communications

### Public Endpoints
- **Stats**: `/api/public/stats` - System statistics
- **Recent Threats**: `/api/public/threats/recent` - Latest threats
- **Generate Test**: `/api/public/threats/generate` - Test data

## 🔧 Configuration Files

### Backend Configuration
- **`.env`**: Environment variables and secrets
- **`docker-compose.yml`**: Container orchestration
- **`create_reports_tables.sql`**: Database schema

### Frontend Configuration
- **`package.json`**: Dependencies and scripts
- **`tailwind.config.js`**: Styling configuration
- **`next.config.js`**: Next.js settings

## 🚨 Security Considerations

### Network Security
- Real-time packet capture requires root privileges
- Network interfaces monitored: wlp0s20f3, vmnet1, vmnet8
- Target IP monitoring: 192.168.100.124

### API Security
- Input validation on all endpoints
- SQL injection prevention with parameterized queries
- Sandboxed Python execution environment
- WebSocket authentication and rate limiting

### Data Security
- PostgreSQL with encrypted connections
- Redis for session management
- Audit trail for all security events
- PCAP file secure storage

## 📈 Performance Optimization

### Backend Optimization
- Async/await for all database operations
- Connection pooling for PostgreSQL
- Redis caching for frequent queries
- Background task processing

### Frontend Optimization
- Next.js 13+ with app directory
- Server-side rendering for initial load
- Client-side hydration for interactivity
- Optimized bundle splitting

### ML Model Optimization
- Pre-trained LightGBM model loading
- Efficient feature extraction
- Real-time classification pipeline
- Memory-optimized packet processing

## 🔍 Monitoring and Logging

### System Monitoring
- Real-time threat detection metrics
- API response time monitoring
- Database performance tracking
- Network interface statistics

### Logging Strategy
- Structured logging with timestamps
- Error tracking and alerting
- Audit trail for security events
- Performance metrics collection

This structure provides a comprehensive, scalable, and maintainable cybersecurity platform with clear separation of concerns and organized codebase.
