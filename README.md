# CyberGuard IDS/IPS Platform

A comprehensive Intrusion Detection and Prevention System with real-time threat monitoring, machine learning-based attack detection, and a modern web dashboard.

## 🏗️ Project Structure

```
pfaf/
├── backend/                    # Backend FastAPI application
│   ├── backend/               # Main backend code
│   ├── analytics/             # Analytics and dashboard scripts
│   ├── scripts/               # Backend utility scripts
│   └── tests/                 # Backend tests and demos
├── frontend/                  # Next.js React frontend
│   ├── app/                   # Next.js app directory
│   ├── components/            # React components
│   ├── lib/                   # Frontend utilities
│   └── tests/                 # Frontend tests
├── ml-iot/                    # Machine learning models
├── scripts/                   # Platform management scripts
├── tests/                     # Integration tests
└── docs/                      # Documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- PostgreSQL
- Redis
- Docker (optional)

### 1. Start the Full Platform
```bash
./scripts/start_full_platform.sh
```

### 2. Test All Services
```bash
./scripts/quick_test_all.sh
```

### 3. Stop All Services
```bash
./scripts/stop_all_services.sh
```

## 🎯 Features

### Backend (FastAPI)
- **Real-time Threat Detection**: ML-based network monitoring
- **REST API**: Comprehensive endpoints for all operations
- **Database Integration**: PostgreSQL with threat storage
- **WebSocket Support**: Real-time alerts and updates
- **Python Analytics**: Secure script execution with visualization
- **Reports System**: Incident reporting and management

### Frontend (Next.js)
- **Modern Dashboard**: Real-time cybersecurity monitoring
- **Threat Management**: Manual threat blocking/unblocking
- **Analytics Interface**: Python script execution with charts
- **SQL Query Tool**: Database exploration and custom queries
- **Reports Management**: Create and manage incident reports
- **Responsive Design**: Works on desktop and mobile

### Machine Learning
- **LightGBM Model**: Pre-trained IoT attack detection
- **6 Attack Types**: Flood, Botnet/Mirai, Backdoors, Injection, Reconnaissance, Spoofing/MITM
- **Real-time Classification**: Live network packet analysis
- **High Accuracy**: Trained on 1M+ samples with 47 features

## 🔧 Services

### Core Services
- **Backend API**: http://localhost:8000
- **Frontend Dashboard**: http://localhost:3000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### Dashboard Pages
- **Home**: `/` - Main dashboard overview
- **Threat Monitoring**: `/threat-monitoring` - Real-time threats
- **Analytics**: `/analytics` - Python script execution
- **SQL Query**: `/sql-query` - Database queries
- **Database**: `/database` - Database explorer
- **Reports**: `/reports` - Incident reports

## 📊 API Endpoints

### Threats
- `GET /api/public/threats/recent` - Recent threats
- `POST /api/threats/{id}/block` - Block threat
- `POST /api/threats/{id}/unblock` - Unblock threat

### Reports
- `GET /api/reports` - List reports
- `POST /api/reports` - Create report
- `GET /api/reports/stats` - Report statistics
- `GET /api/reports/{id}` - Get report details

### Analytics
- `POST /api/python/execute` - Execute Python scripts
- `POST /api/database/query` - Execute SQL queries

## 🛡️ Security Features

### Detection Capabilities
- **Network Monitoring**: Real-time packet capture
- **ML Classification**: Automated threat detection
- **Manual Control**: User-controlled blocking
- **Forensic Analysis**: Detailed threat information
- **Audit Trail**: Complete activity logging

### Attack Types Detected
1. **Flood Attacks**: DDoS and traffic flooding
2. **Botnet/Mirai**: IoT botnet activity
3. **Backdoors**: Unauthorized access attempts
4. **Injection**: SQL injection and code injection
5. **Reconnaissance**: Port scanning and enumeration
6. **Spoofing/MITM**: ARP spoofing and man-in-the-middle

## 🧪 Testing

### Run All Tests
```bash
# Backend tests
cd backend/tests && python test_complete_system.py

# Frontend tests
cd frontend/tests && npm test

# Integration tests
./scripts/validate_system.py
```

### Demo Scripts
```bash
# Complete system demo
cd backend/tests && python demo_complete_system.py

# Real-time monitoring demo
cd backend/tests && ./demo_final_system.sh
```

## 📈 Analytics

### Python Script Execution
- **Secure Environment**: Sandboxed Python execution
- **Database Access**: Direct PostgreSQL connectivity
- **Visualization**: Matplotlib/Seaborn chart generation
- **Base64 Images**: Automatic image encoding and display
- **Sample Scripts**: Pre-built cybersecurity analysis templates

### Available Analytics
1. **Real-time Dashboard**: Live threat statistics
2. **Attack Pattern Analysis**: Temporal and geographic analysis
3. **Threat Intelligence**: IP reputation and threat feeds
4. **Anomaly Detection**: ML-based anomaly identification
5. **Custom Reports**: User-defined analysis scripts

## 🔧 Configuration

### Environment Variables
```bash
# Backend
DATABASE_URL=postgresql://cybersec:secure_password_123@localhost:5432/cybersec_ids
REDIS_URL=redis://localhost:6379
ML_MODEL_PATH=../ml-iot/iot_ids_lightgbm_20250819_132715.pkl

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Database Setup
```bash
# Create database and tables
psql -U postgres -c "CREATE DATABASE cybersec_ids;"
psql -U cybersec -d cybersec_ids -f backend/create_reports_tables.sql
```

## 🚨 Monitoring

### Real-time Alerts
- **WebSocket Integration**: Live threat notifications
- **Email Alerts**: Critical threat notifications (configurable)
- **Dashboard Notifications**: In-app alert system
- **Audit Logging**: Complete activity tracking

### Performance Metrics
- **Threat Detection Rate**: Real-time processing statistics
- **System Performance**: CPU, memory, and network usage
- **Database Metrics**: Query performance and storage usage
- **API Response Times**: Endpoint performance monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the documentation in `/docs`
- Run the validation scripts in `/scripts`
- Review the test examples in `/backend/tests`
- Examine the sample analytics in `/backend/analytics`

## 🔄 Updates

The system includes automatic update capabilities and version management. Check the changelog in `/docs` for recent updates and new features.
