#!/usr/bin/env python3
"""
Test SQL Query Functionality
"""

import requests
import json

def test_sql_queries():
    """Test various SQL queries"""
    
    queries = [
        {
            "name": "List Tables",
            "query": "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
        },
        {
            "name": "Threat Alerts Count",
            "query": "SELECT COUNT(*) as total_threats FROM threat_alerts;"
        },
        {
            "name": "Recent Threats",
            "query": "SELECT id, timestamp, source_ip, destination_ip, attack_type, threat_level FROM threat_alerts ORDER BY timestamp DESC LIMIT 5;"
        },
        {
            "name": "Attack Types Distribution",
            "query": "SELECT attack_type, COUNT(*) as count FROM threat_alerts GROUP BY attack_type ORDER BY count DESC;"
        }
    ]
    
    print("🔍 Testing SQL Query Functionality")
    print("=" * 40)
    
    for test in queries:
        print(f"\n📊 {test['name']}")
        print(f"Query: {test['query']}")
        
        try:
            response = requests.post(
                "http://localhost:8000/api/database/query",
                json={"query": test['query']},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    print("✅ SUCCESS")
                    print(f"Columns: {result['columns']}")
                    print(f"Rows: {len(result['rows'])}")
                    if result['rows']:
                        print("Sample data:")
                        for i, row in enumerate(result['rows'][:3]):
                            print(f"  Row {i+1}: {row}")
                        if len(result['rows']) > 3:
                            print(f"  ... and {len(result['rows']) - 3} more rows")
                else:
                    print(f"❌ FAILED: {result}")
            else:
                print(f"❌ HTTP ERROR: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
    
    print("\n" + "=" * 40)
    print("🎯 SQL Query Testing Complete!")

if __name__ == "__main__":
    test_sql_queries()
