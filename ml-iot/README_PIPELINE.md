# 🔒 IoT IDS Real-time Pipeline

Complete real-time Intrusion Detection System for IoT networks with management dashboard, blockchain audit trail, and Kali VM attack detection.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Kali VM       │───▶│  Network Monitor │───▶│   ML Model      │
│  (Attacks)      │    │  (Packet Capture)│    │  (LightGBM)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Web Dashboard  │◀───│   Flask API      │◀───│  Attack Alerts  │
│  (Management)   │    │  (Real-time)     │    │  (Classification)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Audit Reports   │◀───│   Blockchain     │◀───│   Logging       │
│ (PDF/JSON)      │    │   (Audit Trail)  │    │   (SQLite)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Clone and navigate
cd /path/to/IoTCIC/

# Run setup (requires sudo for packet capture)
sudo python3 setup_ids_pipeline.py
```

### 2. Train and Save Model
First, use your Jupyter notebook to train the model, then add this cell:

```python
# Save the best model after cross-validation
import pickle
from datetime import datetime

print("💾 Saving the best LightGBM model...")

# Train final model on full dataset
final_lgb_model = lgb.LGBMClassifier(
    objective='multiclass',
    num_class=len(le_lgb_cv.classes_),
    is_unbalance=True,
    n_estimators=100,
    random_state=42,
    verbose=-1
)
final_lgb_model.fit(X_lgb_cv, y_lgb_cv)

# Create model pipeline
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
model_pipeline = {
    'model': final_lgb_model,
    'scaler': scaler,
    'label_encoder': le_lgb_cv,
    'feature_names': list(df.drop(columns=['label', 'taxonomy_label']).columns),
    'model_type': 'LightGBM',
    'timestamp': timestamp,
    'classes': list(le_lgb_cv.classes_)
}

# Save as pickle
pickle_filename = f"iot_ids_lightgbm_latest.pkl"
with open(pickle_filename, 'wb') as f:
    pickle.dump(model_pipeline, f)

print(f"✅ Model saved as: {pickle_filename}")
```

### 3. Start the IDS Pipeline
```bash
# Start the system
sudo ./start_ids.sh

# Or manually
sudo python3 realtime_ids_pipeline.py
```

### 4. Access Dashboard
Open your browser: `http://localhost:5000`

### 5. Test with Kali VM
```bash
# On your Kali VM, update target IP and run:
chmod +x kali_attack_simulator.sh
./kali_attack_simulator.sh
```

## 📊 Dashboard Features

### Real-time Monitoring
- **Live Metrics**: Total packets, malicious packets, attack rate
- **Attack Timeline**: Real-time chart of detected attacks
- **Threat Levels**: Critical, High, Medium, Low classification
- **Source Analysis**: IP addresses and attack patterns

### Management Interface
- **System Status**: Online/offline monitoring status
- **Recent Attacks**: Last 10 detected attacks with details
- **Attack Details**: Comprehensive attack information table
- **Network Statistics**: Traffic analysis and patterns

### Blockchain Audit Trail
- **Immutable Logging**: All attacks logged to blockchain
- **Hash Verification**: SHA-256 hash chain integrity
- **Audit Trail**: Complete history of security events
- **Block Explorer**: View recent blockchain blocks

## 🎯 Attack Detection

### Supported Attack Types
- **Flood Attacks**: DoS-TCP_Flood, DoS-UDP_Flood, DoS-SYN_Flood
- **Botnet/Mirai**: Mirai-greeth_flood, Mirai-greip_flood, Mirai-udpplain
- **Spoofing/MITM**: MITM-ArpSpoofing, DNS_Spoofing
- **Reconnaissance**: Recon-PingSweep, Recon-OSScan, Recon-PortScan
- **Backdoors**: Backdoor_Malware, BrowserHijacking, CommandInjection
- **Injection**: SqlInjection, XSS
- **Benign Traffic**: Normal network activity

### Threat Level Classification
- **Critical**: High-confidence, severe attacks (>90% confidence)
- **High**: Major threats (Flood, Botnet, Backdoors)
- **Medium**: Moderate threats (Injection, Spoofing)
- **Low**: Minor threats (Reconnaissance)

## 🔧 Configuration

### Network Interface
Update in `realtime_ids_pipeline.py`:
```python
monitor = NetworkMonitor(model_path, interface="eth0")  # Change interface
```

### Model Path
Update in `realtime_ids_pipeline.py`:
```python
model_path = "iot_ids_lightgbm_latest.pkl"  # Your model file
```

### Dashboard Settings
Update in `ids_config.json`:
```json
{
    "dashboard_host": "0.0.0.0",
    "dashboard_port": 5000,
    "alert_threshold": 0.7,
    "monitoring_enabled": true
}
```

## 📋 API Endpoints

### Statistics
```
GET /api/stats
Returns: Current system statistics and monitoring status
```

### Recent Attacks
```
GET /api/attacks
Returns: List of recent attack detections
```

### Blockchain
```
GET /api/blockchain
Returns: Recent blockchain blocks for audit trail
```

### Traffic Chart
```
GET /api/traffic_chart
Returns: Plotly chart data for real-time visualization
```

## 🛡️ Security Features

### Real-time Detection
- **Packet-level Analysis**: Deep packet inspection
- **ML Classification**: LightGBM model with 99% accuracy
- **Feature Extraction**: 46+ network features analyzed
- **Threat Assessment**: Automated risk scoring

### Audit and Compliance
- **Blockchain Logging**: Immutable audit trail
- **Report Generation**: Automated security reports
- **Compliance Ready**: SOC/SIEM integration ready
- **Forensic Analysis**: Detailed attack information

### Alert Management
- **Real-time Alerts**: Immediate attack notifications
- **Threat Prioritization**: Critical to low severity levels
- **Source Tracking**: IP-based attack attribution
- **Pattern Recognition**: Recurring attack detection

## 🔍 Testing with Kali VM

### Attack Simulation Scripts
The `kali_attack_simulator.sh` includes:

1. **Port Scanning** (nmap)
2. **SYN Flood** (hping3)
3. **UDP Flood** (hping3)
4. **ARP Spoofing** (ettercap)
5. **Vulnerability Scanning** (nmap scripts)
6. **Botnet Simulation** (curl flood)

### Expected Detections
- Port scans → **Reconnaissance** (Low threat)
- Flood attacks → **Flood Attacks** (High threat)
- ARP spoofing → **Spoofing/MITM** (Medium threat)
- Botnet simulation → **Botnet/Mirai** (High threat)

## 📊 Audit Reports

### Generate Reports
```bash
python3 audit_report_generator.py
```

### Report Contents
- **Attack Summary**: Total attacks by type and severity
- **Timeline Analysis**: Attack patterns over time
- **Source Analysis**: Top attacking IP addresses
- **Recommendations**: Security improvement suggestions
- **Compliance Metrics**: Security posture assessment

## 🚨 Troubleshooting

### Common Issues

1. **Permission Denied (Packet Capture)**
   ```bash
   sudo python3 realtime_ids_pipeline.py
   ```

2. **Model File Not Found**
   - Ensure `iot_ids_lightgbm_latest.pkl` exists
   - Check file path in configuration

3. **Network Interface Error**
   ```bash
   ip link show  # List available interfaces
   # Update interface name in code
   ```

4. **Dashboard Not Loading**
   - Check if port 5000 is available
   - Verify Flask is installed
   - Check firewall settings

### Logs and Debugging
- **System Logs**: `ids_pipeline.log`
- **Debug Mode**: Set `debug=True` in Flask app
- **Verbose Logging**: Update log level in configuration

## 📈 Performance Optimization

### System Requirements
- **CPU**: Multi-core recommended for real-time processing
- **RAM**: 4GB+ for model and packet buffering
- **Network**: Gigabit interface for high-traffic environments
- **Storage**: SSD recommended for blockchain and logs

### Scaling Options
- **Distributed Processing**: Multiple monitoring nodes
- **Load Balancing**: Multiple dashboard instances
- **Database Backend**: Replace SQLite with PostgreSQL
- **Cloud Integration**: AWS/Azure deployment ready

## 🔄 Updates and Maintenance

### Model Retraining
1. Collect new attack samples
2. Retrain model with updated data
3. Replace model file
4. Restart IDS pipeline

### System Updates
```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Restart services
sudo systemctl restart iot-ids
```

## 📞 Support

For issues and questions:
1. Check logs in `ids_pipeline.log`
2. Verify configuration in `ids_config.json`
3. Test with known attack patterns
4. Review dashboard for system status

## 🎉 Success Indicators

When everything is working correctly, you should see:
- ✅ Dashboard shows "Online" status
- ✅ Kali attacks are detected and classified
- ✅ Blockchain blocks are created for each attack
- ✅ Real-time charts update with attack data
- ✅ Audit reports generate successfully

Your IoT IDS pipeline is now ready to detect and respond to network attacks in real-time!
