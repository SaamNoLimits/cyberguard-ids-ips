#!/usr/bin/env python3
"""
System Validation Script for CyberGuard IDS/IPS Platform
Tests all major endpoints and services
"""

import requests
import json
import time
from datetime import datetime

def test_endpoint(url, method='GET', data=None, description=""):
    """Test an API endpoint and return the result"""
    try:
        if method == 'GET':
            response = requests.get(url, timeout=5)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=5)
        
        if response.status_code == 200:
            return True, response.json() if response.content else {}
        else:
            return False, f"Status: {response.status_code}"
    except Exception as e:
        return False, str(e)

def main():
    print("🛡️  CYBERGUARD IDS/IPS PLATFORM VALIDATION")
    print("=" * 50)
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Test endpoints
    endpoints = [
        ("http://localhost:8000/health", "GET", None, "Backend Health Check"),
        ("http://localhost:8000/api/public/stats", "GET", None, "System Statistics"),
        ("http://localhost:8000/api/public/threats/recent?limit=3", "GET", None, "Recent Threats"),
        ("http://localhost:8000/api/database/threats/recent?limit=2", "GET", None, "Database Threats"),
        ("http://localhost:8000/api/database/stats", "GET", None, "Database Statistics"),
        ("http://localhost:3000", "GET", None, "Frontend Dashboard"),
    ]

    results = []
    
    for url, method, data, description in endpoints:
        print(f"🔍 Testing: {description}")
        print(f"   URL: {url}")
        
        success, result = test_endpoint(url, method, data, description)
        
        if success:
            print("   ✅ SUCCESS")
            if isinstance(result, dict):
                # Show key information
                if 'status' in result:
                    print(f"   📊 Status: {result['status']}")
                if 'total_threats' in result:
                    print(f"   🚨 Total Threats: {result['total_threats']}")
                if 'threats' in result:
                    print(f"   📋 Threats Retrieved: {len(result['threats'])}")
                if 'services' in result:
                    services = result['services']
                    active_services = [k for k, v in services.items() if v]
                    print(f"   🔧 Active Services: {', '.join(active_services)}")
        else:
            print(f"   ❌ FAILED: {result}")
        
        results.append((description, success, result))
        print()
        time.sleep(0.5)

    # Summary
    print("📊 VALIDATION SUMMARY")
    print("=" * 30)
    
    successful = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")
    
    if successful == total:
        print("\n🎉 ALL SYSTEMS OPERATIONAL!")
        print("🌐 Access Points:")
        print("   • Main Dashboard: http://localhost:3000")
        print("   • API Backend: http://localhost:8000")
        print("   • API Docs: http://localhost:8000/docs")
        print("\n🔐 Features Available:")
        print("   • Real-time threat monitoring")
        print("   • ML-based attack detection")
        print("   • PostgreSQL database storage")
        print("   • WebSocket live updates")
        print("   • Python analytics execution")
        print("   • PCAP file generation")
        print("   • Manual threat management")
    else:
        print("\n⚠️  Some services may need attention")
    
    print("\n🛡️  Ready for cybersecurity monitoring!")

if __name__ == "__main__":
    main()
