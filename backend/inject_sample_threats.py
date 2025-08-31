#!/usr/bin/env python3
"""
Inject sample threats directly into the running backend
"""
import requests
import json
from datetime import datetime, timedelta
import uuid

def inject_sample_threats():
    """Inject sample threats via the backend API"""
    
    # Check if backend is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("Backend is not responding properly")
            return
        print("✅ Backend is running")
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to backend: {e}")
        return
    
    # Sample threats data
    sample_threats = [
        {
            "source_ip": "192.168.1.100",
            "destination_ip": "192.168.1.1", 
            "attack_type": "Flood Attacks",
            "threat_level": "HIGH",
            "confidence": 0.92,
            "description": "High-volume flood attack detected from internal network",
            "protocol": 6,
            "source_port": 45231,
            "destination_port": 80,
            "packet_size": 1500,
            "ttl": 64
        },
        {
            "source_ip": "10.0.0.55",
            "destination_ip": "192.168.1.10",
            "attack_type": "Botnet/Mirai Attacks", 
            "threat_level": "CRITICAL",
            "confidence": 0.98,
            "description": "Mirai botnet activity detected - IoT device compromise attempt",
            "protocol": 6,
            "source_port": 23,
            "destination_port": 23,
            "packet_size": 512,
            "ttl": 32
        },
        {
            "source_ip": "203.0.113.42",
            "destination_ip": "192.168.1.50",
            "attack_type": "Injection Attacks",
            "threat_level": "HIGH", 
            "confidence": 0.87,
            "description": "SQL injection attempt detected on web application",
            "protocol": 6,
            "source_port": 54321,
            "destination_port": 443,
            "packet_size": 2048,
            "ttl": 56
        },
        {
            "source_ip": "198.51.100.15",
            "destination_ip": "192.168.1.1",
            "attack_type": "Reconnaissance",
            "threat_level": "MEDIUM",
            "confidence": 0.75,
            "description": "Port scanning activity detected from external source",
            "protocol": 6,
            "source_port": 12345,
            "destination_port": 22,
            "packet_size": 64,
            "ttl": 48
        },
        {
            "source_ip": "172.16.0.99", 
            "destination_ip": "192.168.1.25",
            "attack_type": "Spoofing / MITM",
            "threat_level": "HIGH",
            "confidence": 0.89,
            "description": "ARP spoofing attack detected - potential man-in-the-middle",
            "protocol": 1,
            "packet_size": 128,
            "ttl": 64
        }
    ]
    
    print("🚨 Injecting sample threats...")
    
    # Create a temporary endpoint to inject threats
    # We'll modify the backend to accept these
    for i, threat in enumerate(sample_threats):
        # Create complete threat data
        threat_data = {
            "id": str(uuid.uuid4()),
            "timestamp": (datetime.utcnow() - timedelta(minutes=i*5)).isoformat(),
            "source_ip": threat["source_ip"],
            "destination_ip": threat["destination_ip"],
            "attack_type": threat["attack_type"],
            "threat_level": threat["threat_level"],
            "confidence": threat["confidence"],
            "description": threat["description"],
            "blocked": False,
            "raw_data": {
                "protocol": threat["protocol"],
                "packet_size": threat["packet_size"],
                "ttl": threat["ttl"],
                "source_port": threat.get("source_port"),
                "destination_port": threat.get("destination_port"),
                "tcp_flags": 24 if threat["protocol"] == 6 else None,
                "window_size": 8192 if threat["protocol"] == 6 else None,
                "icmp_type": 8 if threat["protocol"] == 1 else None,
                "icmp_code": 0 if threat["protocol"] == 1 else None
            }
        }
        
        print(f"  📡 Threat {i+1}: {threat['attack_type']} from {threat['source_ip']}")
    
    print("✅ Sample threats prepared!")
    print("📋 To see these threats, I'll need to add a temporary endpoint to the backend.")
    print("💡 Alternatively, you can test with real network traffic from your Kali VM.")
    
    return sample_threats

if __name__ == "__main__":
    inject_sample_threats()
