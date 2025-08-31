#!/usr/bin/env python3
"""
Simulate Kali Linux Attacks for Testing
This script simulates various Kali attack patterns to test the IDS detection
"""

import requests
import time
import random
import json
from datetime import datetime

API_BASE = "http://localhost:8000"
TARGET_IP = "192.168.100.124"

def simulate_nmap_scan():
    """Simulate Nmap scanning patterns"""
    print("🔍 Simulating Nmap scan...")
    
    # Generate multiple threats that look like nmap scans
    for i in range(3):
        threat_data = {
            "source_ip": f"192.168.{random.randint(1,254)}.{random.randint(1,254)}",
            "destination_ip": TARGET_IP,
            "attack_type": "Reconnaissance",
            "threat_level": "MEDIUM",
            "confidence": random.uniform(0.7, 0.9),
            "description": f"Nmap port scan detected - sequence {i+1}",
            "tool_detected": "nmap_syn_scan",
            "raw_data": {
                "protocol": 6,  # TCP
                "packet_size": random.randint(40, 80),
                "ttl": random.randint(60, 64),
                "tcp_flags": 2,  # SYN flag
                "destination_port": random.choice([22, 80, 443, 3000, 8000])
            }
        }
        
        response = requests.post(f"{API_BASE}/api/public/threats/generate", 
                               json={"custom_threat": threat_data})
        if response.status_code == 200:
            print(f"   ✅ Nmap scan {i+1} simulated")
        time.sleep(1)

def simulate_nikto_scan():
    """Simulate Nikto web vulnerability scan"""
    print("🕷️  Simulating Nikto scan...")
    
    threat_data = {
        "source_ip": f"192.168.{random.randint(1,254)}.{random.randint(1,254)}",
        "destination_ip": TARGET_IP,
        "attack_type": "Reconnaissance",
        "threat_level": "HIGH",
        "confidence": random.uniform(0.8, 0.95),
        "description": "Nikto web vulnerability scan detected",
        "tool_detected": "nikto_scan",
        "raw_data": {
            "protocol": 6,  # TCP
            "packet_size": random.randint(500, 1500),
            "ttl": 64,
            "destination_port": random.choice([80, 443, 3000, 8080]),
            "user_agent": "Mozilla/5.00 (Nikto/2.1.6)"
        }
    }
    
    response = requests.post(f"{API_BASE}/api/public/threats/generate", 
                           json={"custom_threat": threat_data})
    if response.status_code == 200:
        print("   ✅ Nikto scan simulated")

def simulate_sql_injection():
    """Simulate SQLMap injection attempts"""
    print("💉 Simulating SQL injection...")
    
    threat_data = {
        "source_ip": f"192.168.{random.randint(1,254)}.{random.randint(1,254)}",
        "destination_ip": TARGET_IP,
        "attack_type": "Injection Attacks",
        "threat_level": "CRITICAL",
        "confidence": random.uniform(0.85, 0.95),
        "description": "SQLMap injection attempt detected",
        "tool_detected": "sqlmap_injection",
        "raw_data": {
            "protocol": 6,  # TCP
            "packet_size": random.randint(800, 2000),
            "ttl": 64,
            "destination_port": random.choice([80, 443, 8000]),
            "payload": "' OR '1'='1"
        }
    }
    
    response = requests.post(f"{API_BASE}/api/public/threats/generate", 
                           json={"custom_threat": threat_data})
    if response.status_code == 200:
        print("   ✅ SQL injection simulated")

def simulate_ddos_attack():
    """Simulate DDoS flood attack"""
    print("🌊 Simulating DDoS attack...")
    
    threat_data = {
        "source_ip": f"192.168.{random.randint(1,254)}.{random.randint(1,254)}",
        "destination_ip": TARGET_IP,
        "attack_type": "Flood Attacks",
        "threat_level": "CRITICAL",
        "confidence": random.uniform(0.9, 0.98),
        "description": "DDoS flood attack from Kali VM detected",
        "tool_detected": "ddos_flood",
        "raw_data": {
            "protocol": random.choice([6, 17]),  # TCP or UDP
            "packet_size": random.randint(1000, 1500),
            "ttl": random.randint(60, 64),
            "packets_per_second": random.randint(100, 500)
        }
    }
    
    response = requests.post(f"{API_BASE}/api/public/threats/generate", 
                           json={"custom_threat": threat_data})
    if response.status_code == 200:
        print("   ✅ DDoS attack simulated")

def simulate_brute_force():
    """Simulate Hydra brute force attack"""
    print("🔨 Simulating brute force attack...")
    
    threat_data = {
        "source_ip": f"192.168.{random.randint(1,254)}.{random.randint(1,254)}",
        "destination_ip": TARGET_IP,
        "attack_type": "Backdoors & Exploits",
        "threat_level": "HIGH",
        "confidence": random.uniform(0.8, 0.9),
        "description": "Hydra brute force attack detected",
        "tool_detected": "hydra_bruteforce",
        "raw_data": {
            "protocol": 6,  # TCP
            "packet_size": random.randint(100, 300),
            "ttl": 64,
            "destination_port": random.choice([22, 21, 23, 80, 443]),
            "login_attempts": random.randint(10, 50)
        }
    }
    
    response = requests.post(f"{API_BASE}/api/public/threats/generate", 
                           json={"custom_threat": threat_data})
    if response.status_code == 200:
        print("   ✅ Brute force attack simulated")

def main():
    print("🎯 Kali Linux Attack Simulation")
    print("=" * 50)
    print(f"Target: {TARGET_IP}")
    print(f"API: {API_BASE}")
    print()
    
    # Test API connectivity
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✅ API connected")
        else:
            print("❌ API connection failed")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return
    
    print("\n🚀 Starting Kali attack simulation...")
    print("Monitor the dashboard and console for real-time detection!")
    print()
    
    attacks = [
        ("Nmap Scan", simulate_nmap_scan),
        ("Nikto Scan", simulate_nikto_scan),
        ("SQL Injection", simulate_sql_injection),
        ("DDoS Attack", simulate_ddos_attack),
        ("Brute Force", simulate_brute_force)
    ]
    
    for attack_name, attack_func in attacks:
        print(f"🎯 Launching {attack_name}...")
        attack_func()
        print(f"   ⏳ Waiting 3 seconds...")
        time.sleep(3)
        print()
    
    print("✅ All Kali attacks simulated!")
    print("\n📊 Check the monitoring console and dashboard for detections")
    print(f"🌐 Dashboard: http://{TARGET_IP}:3000/threat-monitoring")
    
    # Show final stats
    try:
        response = requests.get(f"{API_BASE}/api/public/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"\n📈 Final Stats:")
            print(f"   Total threats: {stats.get('total_threats', 0)}")
            attack_types = stats.get('attack_types', {})
            for attack_type, count in attack_types.items():
                if count > 0:
                    print(f"   {attack_type}: {count}")
    except:
        pass

if __name__ == "__main__":
    main()
