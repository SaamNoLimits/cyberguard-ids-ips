#!/usr/bin/env python3
"""
Test Kali Attack Detection
Simulates various Kali Linux attack patterns to test detection capabilities
"""

import requests
import time
import json
import random
from datetime import datetime

# Target system (your IDS platform)
TARGET_HOST = "192.168.100.124"  # Your main IP
API_BASE = f"http://{TARGET_HOST}:8000"
DASHBOARD_URL = f"http://{TARGET_HOST}:3000"

def test_api_connectivity():
    """Test if the API is accessible"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ API is accessible at {API_BASE}")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot reach API: {e}")
        return False

def simulate_nmap_scan():
    """Simulate Nmap-style scanning"""
    print("\n🔍 Simulating Nmap SYN scan...")
    
    # Common ports to scan
    ports = [22, 23, 53, 80, 110, 443, 993, 995, 3000, 8000, 8080]
    
    for port in ports:
        try:
            # Quick connection attempt (simulates SYN scan)
            response = requests.get(f"http://{TARGET_HOST}:{port}", timeout=1)
            print(f"   Port {port}: Open")
        except:
            print(f"   Port {port}: Closed/Filtered")
        
        time.sleep(0.1)  # Small delay between scans

def simulate_nikto_scan():
    """Simulate Nikto web vulnerability scan"""
    print("\n🕷️  Simulating Nikto web scan...")
    
    # Common Nikto test paths
    test_paths = [
        "/admin/",
        "/administrator/",
        "/backup/",
        "/config/",
        "/database/",
        "/logs/",
        "/test/",
        "/phpinfo.php",
        "/admin.php",
        "/login.php",
        "/wp-admin/",
        "/.env",
        "/robots.txt",
        "/sitemap.xml"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.00 (Nikto/2.1.6) (Evasions:None) (Test:000001)"
    }
    
    for path in test_paths:
        try:
            url = f"http://{TARGET_HOST}:3000{path}"
            response = requests.get(url, headers=headers, timeout=2)
            print(f"   Testing {path}: {response.status_code}")
        except:
            print(f"   Testing {path}: No response")
        
        time.sleep(0.2)

def simulate_sql_injection():
    """Simulate SQLMap-style SQL injection"""
    print("\n💉 Simulating SQL injection attempts...")
    
    # Common SQL injection payloads
    payloads = [
        "' OR '1'='1",
        "' UNION SELECT NULL--",
        "'; DROP TABLE users--",
        "' AND 1=1--",
        "' OR 1=1#",
        "admin'--",
        "' UNION SELECT username,password FROM users--"
    ]
    
    for payload in payloads:
        try:
            # Test against API endpoint
            url = f"{API_BASE}/api/public/threats/recent"
            params = {"id": payload}
            response = requests.get(url, params=params, timeout=2)
            print(f"   Payload '{payload[:20]}...': {response.status_code}")
        except:
            print(f"   Payload '{payload[:20]}...': No response")
        
        time.sleep(0.3)

def simulate_brute_force():
    """Simulate Hydra-style brute force attack"""
    print("\n🔨 Simulating brute force attack...")
    
    # Common username/password combinations
    credentials = [
        ("admin", "admin"),
        ("admin", "password"),
        ("admin", "123456"),
        ("root", "root"),
        ("root", "toor"),
        ("user", "user"),
        ("test", "test"),
        ("guest", "guest")
    ]
    
    for username, password in credentials:
        try:
            # Simulate login attempts
            data = {"username": username, "password": password}
            response = requests.post(f"{API_BASE}/auth/login", json=data, timeout=2)
            print(f"   Login attempt {username}:{password}: {response.status_code}")
        except:
            print(f"   Login attempt {username}:{password}: No response")
        
        time.sleep(0.1)  # Rapid attempts

def simulate_ddos_flood():
    """Simulate DDoS flood attack"""
    print("\n🌊 Simulating DDoS flood attack...")
    
    # Send rapid requests
    for i in range(20):
        try:
            # Large payload to simulate flood
            data = "A" * 1000  # 1KB payload
            response = requests.post(f"{API_BASE}/api/public/threats/generate", 
                                   data=data, timeout=1)
            print(f"   Flood request {i+1}: {response.status_code}")
        except:
            print(f"   Flood request {i+1}: Timeout/Error")
        
        time.sleep(0.05)  # Very rapid requests

def check_detection_results():
    """Check if attacks were detected"""
    print("\n📊 Checking detection results...")
    
    try:
        # Get recent threats
        response = requests.get(f"{API_BASE}/api/public/threats/recent", timeout=5)
        if response.status_code == 200:
            threats = response.json()
            print(f"✅ Found {len(threats)} recent threats:")
            
            for threat in threats[-5:]:  # Show last 5
                print(f"   🚨 {threat.get('attack_type', 'Unknown')} from {threat.get('source_ip', 'Unknown')} "
                      f"(Confidence: {threat.get('confidence', 0):.1%})")
        else:
            print(f"❌ Could not retrieve threats: {response.status_code}")
            
        # Get system stats
        response = requests.get(f"{API_BASE}/api/public/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"\n📈 System Statistics:")
            print(f"   Total threats: {stats.get('total_threats', 0)}")
            print(f"   Active monitoring: {stats.get('monitoring_active', False)}")
            print(f"   Network interfaces: {stats.get('network_interfaces', [])}")
        
    except Exception as e:
        print(f"❌ Error checking results: {e}")

def main():
    """Main test function"""
    print("🎯 Kali Attack Detection Test")
    print("=" * 50)
    print(f"Target: {TARGET_HOST}")
    print(f"API: {API_BASE}")
    print(f"Dashboard: {DASHBOARD_URL}")
    print()
    
    # Test connectivity first
    if not test_api_connectivity():
        print("❌ Cannot connect to API. Make sure the platform is running with:")
        print("   sudo ./start_with_network_capture.sh")
        return
    
    print("\n🚀 Starting attack simulations...")
    print("   Monitor the dashboard for real-time detection!")
    print(f"   Dashboard URL: {DASHBOARD_URL}/threat-monitoring")
    
    # Run attack simulations
    simulate_nmap_scan()
    time.sleep(2)
    
    simulate_nikto_scan()
    time.sleep(2)
    
    simulate_sql_injection()
    time.sleep(2)
    
    simulate_brute_force()
    time.sleep(2)
    
    simulate_ddos_flood()
    time.sleep(3)
    
    # Check results
    check_detection_results()
    
    print("\n✅ Attack simulation completed!")
    print(f"🌐 Check the dashboard at: {DASHBOARD_URL}/threat-monitoring")
    print("🔍 Look for real-time alerts and threat statistics")

if __name__ == "__main__":
    main()
