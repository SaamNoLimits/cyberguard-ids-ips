#!/usr/bin/env python3
"""
Quick endpoint testing script
"""

import requests
import json
from datetime import datetime

API_BASE_URL = "http://localhost:8000"

def test_endpoint(name, url, method="GET"):
    """Test an API endpoint"""
    print(f"\n🧪 Testing {name}...")
    print(f"   URL: {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, timeout=5)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success!")
            
            # Pretty print first few items if it's a list
            if isinstance(data, list):
                print(f"   📊 Returned {len(data)} items")
                if data:
                    print(f"   📝 Sample item: {json.dumps(data[0], indent=2)[:200]}...")
            elif isinstance(data, dict):
                print(f"   📝 Response: {json.dumps(data, indent=2)[:300]}...")
        else:
            print(f"   ❌ Failed: {response.text[:100]}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    """Test all endpoints"""
    print("🔒 CYBERSECURITY API ENDPOINT TESTING")
    print("=" * 50)
    
    # Test endpoints
    endpoints = [
        ("Health Check", f"{API_BASE_URL}/health", "GET"),
        ("Recent Threats", f"{API_BASE_URL}/api/public/threats/recent?limit=5", "GET"),
        ("System Stats", f"{API_BASE_URL}/api/public/stats", "GET"),
        ("Generate Threat", f"{API_BASE_URL}/api/public/threats/generate", "POST"),
        ("Recent Threats (after generation)", f"{API_BASE_URL}/api/public/threats/recent?limit=3", "GET"),
    ]
    
    for name, url, method in endpoints:
        test_endpoint(name, url, method)
    
    print(f"\n✅ Testing completed at {datetime.now().strftime('%H:%M:%S')}")
    print("\n💡 To see real-time updates:")
    print("   1. Open http://localhost:3000/threat-monitoring")
    print("   2. Run: python3 demo_realtime_threats.py")

if __name__ == "__main__":
    main()
