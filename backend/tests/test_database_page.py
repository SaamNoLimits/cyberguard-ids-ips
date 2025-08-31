#!/usr/bin/env python3
"""
Test Database Page Functionality
"""

import requests
import json

def test_database_endpoints():
    """Test database endpoints used by the frontend"""
    
    tests = [
        {
            "name": "Database Stats",
            "url": "http://localhost:8000/api/database/stats",
            "method": "GET"
        },
        {
            "name": "Recent Threats",
            "url": "http://localhost:8000/api/database/threats/recent?limit=5",
            "method": "GET"
        },
        {
            "name": "Frontend Database Page",
            "url": "http://localhost:3000/database",
            "method": "GET"
        }
    ]
    
    print("🗄️ Testing Database Page Functionality")
    print("=" * 45)
    
    for test in tests:
        print(f"\n📊 {test['name']}")
        print(f"URL: {test['url']}")
        
        try:
            response = requests.get(test['url'], timeout=10)
            
            if response.status_code == 200:
                print("✅ SUCCESS")
                
                # Try to parse JSON for API endpoints
                if '/api/' in test['url']:
                    try:
                        data = response.json()
                        if 'total_threats' in data:
                            print(f"📈 Total Threats: {data['total_threats']:,}")
                        if 'threats' in data:
                            print(f"📋 Threats Retrieved: {len(data['threats'])}")
                            if data['threats']:
                                threat = data['threats'][0]
                                print(f"🚨 Sample: {threat['attack_type']} from {threat['source_ip']}")
                        if 'pcap_files_count' in data:
                            print(f"📁 PCAP Files: {data['pcap_files_count']}")
                    except:
                        print("📄 Response received (HTML content)")
                else:
                    print("📄 Frontend page loaded successfully")
                    
            else:
                print(f"❌ HTTP ERROR: {response.status_code}")
                
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
    
    print("\n" + "=" * 45)
    print("🎯 Database Page Testing Complete!")
    print("\n🌐 Access the database dashboard at:")
    print("   http://localhost:3000/database")

if __name__ == "__main__":
    test_database_endpoints()
