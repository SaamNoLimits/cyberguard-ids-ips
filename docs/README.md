# Cybersecurity IDS/IPS Platform

A comprehensive real-time cybersecurity platform with Intrusion Detection System (IDS) and Intrusion Prevention System (IPS) capabilities, featuring machine learning-based threat detection for IoT networks.

## 🏗️ Project Structure

```
pfaf/
├── frontend/           # Next.js React Dashboard
├── backend/           # FastAPI Python Backend
├── ml-iot/           # Machine Learning Models & IoT Detection
├── scripts/          # Deployment & Management Scripts
└── README.md         # This file
```

## 📁 Directory Overview

### Frontend (`/frontend`)
- **Technology**: Next.js 14 + TypeScript + Tailwind CSS
- **Features**: Real-time threat monitoring dashboard, threat details modal, manual threat management
- **Components**: Modern UI with Radix UI components, WebSocket integration for live updates

### Backend (`/backend`)
- **Technology**: FastAPI + Python 3.12
- **Services**: IDS/IPS engine, network monitoring, threat intelligence, blockchain audit
- **Features**: ML-based threat detection, real-time packet capture, WebSocket alerts, REST API

### ML-IoT (`/ml-iot`)
- **Technology**: LightGBM + scikit-learn + Jupyter
- **Models**: Pre-trained IoT attack detection models (1M+ samples, 47 features)
- **Attacks Detected**: Flood, Botnet/Mirai, Backdoors, Injection, Reconnaissance, Spoofing/MITM

### Scripts (`/scripts`)
- **Deployment**: Platform startup/shutdown scripts
- **Network Capture**: Root privilege network monitoring scripts
- **Kali Detection**: Specialized scripts for detecting Kali VM attacks

## 🚀 Quick Start

### 1. Start the Complete Platform
```bash
# Start backend and frontend services
./scripts/start_platform.sh

# Start with network capture (requires root)
sudo ./scripts/start_with_network_capture.sh

# Stop all services
./scripts/stop_platform.sh
```

### 2. Individual Services

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

#### ML Model Training
```bash
cd ml-iot
pip install -r requirements.txt
jupyter notebook iot-network-vulnerabilities.ipynb
```

## 🔧 Configuration

### Environment Variables
- **Backend**: Configure in `backend/.env`
- **Frontend**: Configure in `frontend/.env.local`
- **Database**: PostgreSQL + Redis (Docker Compose)

### Network Monitoring
- **Interface**: Auto-detected or specify in config
- **Privileges**: Root required for packet capture
- **Filters**: Configurable BPF filters for traffic analysis

## 🛡️ Security Features

### Threat Detection
- **Real-time ML Analysis**: LightGBM model with 99%+ accuracy
- **Attack Types**: 6 categories of IoT/network attacks
- **Confidence Scoring**: Probabilistic threat assessment
- **False Positive Reduction**: Advanced filtering algorithms

### Response Capabilities
- **Manual Blocking**: User-controlled threat blocking/unblocking
- **Automated Alerts**: Real-time WebSocket notifications
- **Forensic Analysis**: Detailed packet inspection and analysis
- **Audit Trail**: Immutable blockchain-based logging

### Threat Intelligence
- **External APIs**: VirusTotal, AbuseIPDB integration
- **IP Reputation**: Real-time malicious IP checking
- **Geolocation**: Attack source identification
- **Pattern Recognition**: Behavioral analysis

## 📊 Dashboard Features

### Real-time Monitoring
- **Live Threat Feed**: WebSocket-powered real-time updates
- **Interactive Charts**: Threat statistics and trends
- **Filtering & Search**: Advanced threat filtering capabilities
- **Pagination**: Scalable threat list handling

### Threat Analysis
- **Detailed Views**: Click-through threat analysis
- **Security Recommendations**: Attack-specific mitigation advice
- **Risk Assessment**: Threat level and impact analysis
- **Mitigation Steps**: Step-by-step response guidance

## 🧪 Testing & Development

### Kali VM Testing
```bash
# Monitor Kali VM attacks
./scripts/start_kali_detection.sh

# Test with sample attacks
cd backend
python simulate_kali_attacks.py
```

### API Testing
```bash
# Test public endpoints
cd backend
python test_endpoints.py

# Generate sample threats
python demo_realtime_threats.py
```

## 🐳 Docker Deployment

```bash
# Start with Docker Compose
cd backend
docker-compose up -d

# View logs
docker-compose logs -f
```

## 📈 Performance

### Scalability
- **High Volume**: Handles 1000+ threats/second
- **Low Latency**: <100ms threat detection
- **Memory Efficient**: Optimized for continuous operation
- **Concurrent Users**: Multi-user dashboard support

### System Requirements
- **CPU**: 4+ cores recommended
- **RAM**: 8GB+ for ML models
- **Storage**: 20GB+ for logs and models
- **Network**: Gigabit for high-traffic monitoring

## 🔍 Monitoring Capabilities

### Network Traffic Analysis
- **Packet Inspection**: Deep packet analysis
- **Protocol Support**: TCP, UDP, ICMP, ARP
- **Traffic Patterns**: Behavioral anomaly detection
- **Bandwidth Monitoring**: Network utilization tracking

### Attack Detection
- **Signature-based**: Known attack pattern matching
- **Anomaly-based**: ML-powered behavioral analysis
- **Hybrid Approach**: Combined detection methods
- **Real-time Processing**: Sub-second threat identification

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check individual README files in each directory
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Security**: Report security vulnerabilities privately

## 🔄 Version History

- **v2.0.0**: Restructured project architecture (Current)
- **v1.5.0**: Enhanced WebSocket stability and threat management
- **v1.0.0**: Initial release with basic IDS/IPS functionality
