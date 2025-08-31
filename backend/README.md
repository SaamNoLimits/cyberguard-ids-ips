# 🔒 Cybersecurity IDS/IPS Platform

Full-stack Intrusion Detection & Prevention System with IoT network analysis, real-time threat monitoring, and advanced cybersecurity dashboard.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend│───▶│   FastAPI Backend│───▶│   ML Pipeline   │
│   (Dashboard)   │    │   (REST API)     │    │   (LightGBM)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   WebSocket     │◀───│   Redis Cache    │◀───│  Network Monitor│
│   (Real-time)   │    │   (Sessions)     │    │  (Packet Capture)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   PostgreSQL    │◀───│   Blockchain     │◀───│   Threat Intel  │
│   (Analytics)   │    │   (Audit Trail)  │    │   (OSINT APIs)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Features

### Frontend (React + TypeScript)
- **Real-time Dashboard**: Live threat monitoring with WebSocket updates
- **Network Topology**: Interactive network visualization
- **Threat Intelligence**: MITRE ATT&CK framework integration
- **Incident Response**: Automated playbooks and response workflows
- **Analytics**: Advanced charts and threat trend analysis
- **User Management**: Role-based access control

### Backend (FastAPI + Python)
- **ML Pipeline**: LightGBM-based IoT attack detection
- **Real-time Processing**: Network packet analysis and classification
- **API Gateway**: RESTful endpoints for all operations
- **WebSocket Server**: Real-time data streaming
- **Blockchain Audit**: Immutable security event logging
- **Threat Intelligence**: Integration with external threat feeds

### Security Features
- **IDS (Intrusion Detection)**: Real-time network monitoring
- **IPS (Intrusion Prevention)**: Automated threat blocking
- **Behavioral Analysis**: ML-based anomaly detection
- **Forensics**: Detailed attack analysis and reporting
- **Compliance**: NIST, ISO 27001 reporting capabilities

## 📦 Tech Stack

### Frontend
- React 18 + TypeScript
- Next.js 15 for SSR/SSG
- Tailwind CSS + shadcn/ui
- Recharts for data visualization
- Socket.io for real-time updates
- Zustand for state management

### Backend
- FastAPI (Python 3.11+)
- PostgreSQL for data persistence
- Redis for caching and sessions
- Celery for background tasks
- Docker for containerization
- Nginx for reverse proxy

### ML/Security
- LightGBM for attack classification
- Scapy for packet capture
- YARA for malware detection
- Suricata for network IDS
- OpenVAS for vulnerability scanning

## 🛠️ Installation

### Prerequisites
```bash
# System requirements
sudo apt update
sudo apt install -y python3.11 python3-pip nodejs npm postgresql redis-server docker.io
```

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python setup_database.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run build
```

### Docker Deployment
```bash
docker-compose up -d
```

## 🔧 Configuration

### Environment Variables
```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@localhost/cybersec_ids
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
ML_MODEL_PATH=./models/iot_ids_lightgbm.pkl

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

## 📊 Usage

1. **Start the platform**: `docker-compose up`
2. **Access dashboard**: http://localhost:3000
3. **API documentation**: http://localhost:8000/docs
4. **Monitor networks**: Configure network interfaces in settings
5. **View threats**: Real-time alerts appear in dashboard

## 🔍 Attack Detection

The system detects these IoT attack types:
- **Flood Attacks**: TCP/UDP/ICMP flooding
- **Botnet/Mirai**: IoT botnet communications
- **Backdoors & Exploits**: Unauthorized access attempts
- **Injection Attacks**: SQL/Command injection
- **Reconnaissance**: Network scanning and enumeration
- **Spoofing/MITM**: Man-in-the-middle attacks

## 📈 Performance

- **Throughput**: 10,000+ packets/second analysis
- **Latency**: <100ms detection time
- **Accuracy**: 99%+ on IoT attack classification
- **Scalability**: Horizontal scaling with Docker Swarm

## 🛡️ Security

- JWT-based authentication
- Role-based access control (RBAC)
- API rate limiting
- Input validation and sanitization
- Encrypted data transmission (TLS 1.3)
- Blockchain audit trail for compliance

## 📚 Documentation

- [API Reference](./docs/api.md)
- [Deployment Guide](./docs/deployment.md)
- [Security Playbooks](./docs/playbooks.md)
- [ML Model Training](./docs/ml-training.md)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- Documentation: [Wiki](./wiki)
- Issues: [GitHub Issues](./issues)
- Discord: [Community Server](https://discord.gg/cybersec-ids)
