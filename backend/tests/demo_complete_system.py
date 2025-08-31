#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete System Demo - Cybersecurity IDS/IPS Platform
Tests all functionalities: Database, SQL, Python Analytics with Image Generation
"""

import requests
import json
import time
import base64

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_database_api():
    """Test database API endpoints"""
    print("🔍 Testing Database API...")
    
    # Test tables endpoint
    response = requests.get(f"{BACKEND_URL}/api/database/tables")
    if response.status_code == 200:
        tables = response.json()
        print(f"✅ Found {len(tables)} database tables")
        for table in tables:
            print(f"   - {table['tablename']}: {table['row_count']} rows, {table['size']}")
    else:
        print(f"❌ Database API failed: {response.status_code}")
    
    return response.status_code == 200

def test_sql_execution():
    """Test SQL execution API"""
    print("\n📊 Testing SQL Execution...")
    
    # Test SQL query
    sql_query = {
        "query": """
        SELECT 
            attack_type,
            threat_level,
            COUNT(*) as threat_count,
            AVG(confidence) as avg_confidence
        FROM threat_alerts 
        GROUP BY attack_type, threat_level 
        ORDER BY threat_count DESC 
        LIMIT 5
        """
    }
    
    response = requests.post(f"{BACKEND_URL}/api/sql/execute", json=sql_query)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ SQL executed in {result['execution_time']:.3f}s")
        print(f"   Results: {len(result['result'])} rows")
        for row in result['result'][:3]:
            print(f"   - {row['attack_type']}: {row['threat_count']} threats")
    else:
        print(f"❌ SQL execution failed: {response.status_code}")
    
    return response.status_code == 200

def test_python_analytics():
    """Test Python analytics with image generation"""
    print("\n🐍 Testing Python Analytics with Image Generation...")
    
    # Python script for cybersecurity analytics
    python_code = '''
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import base64
import io
import psycopg2

print("🔍 Starting Cybersecurity Analytics...")

# Database connection
try:
    conn = psycopg2.connect(
        host="localhost",
        database="cybersec_ids",
        user="cybersec",
        password="secure_password_123"
    )
    print("✅ Connected to PostgreSQL database")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    exit(1)

# Query threat data
query = """
SELECT 
    DATE(timestamp) as date,
    attack_type,
    threat_level,
    COUNT(*) as threat_count
FROM threat_alerts 
WHERE timestamp >= NOW() - INTERVAL '30 days'
GROUP BY DATE(timestamp), attack_type, threat_level
ORDER BY date DESC
LIMIT 100
"""

df = pd.read_sql(query, conn)
print(f"📊 Loaded {len(df)} threat records")

# Create comprehensive analytics dashboard
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Cybersecurity Threat Analytics Dashboard', fontsize=16, fontweight='bold')

# 1. Threat count by type
threat_by_type = df.groupby('attack_type')['threat_count'].sum().sort_values(ascending=False)
colors = ['#ff6b6b', '#feca57', '#48dbfb', '#ff9ff3', '#54a0ff']
ax1.bar(threat_by_type.index, threat_by_type.values, color=colors[:len(threat_by_type)])
ax1.set_title('Threats by Attack Type')
ax1.set_ylabel('Total Threats')
ax1.tick_params(axis='x', rotation=45)

# 2. Threat level distribution
threat_by_level = df.groupby('threat_level')['threat_count'].sum()
ax2.pie(threat_by_level.values, labels=threat_by_level.index, autopct='%1.1f%%', 
        colors=['#ff6b6b', '#feca57', '#48dbfb', '#ff9ff3'])
ax2.set_title('Threat Level Distribution')

# 3. Timeline analysis
timeline_data = df.groupby('date')['threat_count'].sum().reset_index()
timeline_data['date'] = pd.to_datetime(timeline_data['date'])
ax3.plot(timeline_data['date'], timeline_data['threat_count'], 
         marker='o', linewidth=2, markersize=6, color='#ff6b6b')
ax3.set_title('Threat Timeline (Last 30 Days)')
ax3.set_ylabel('Daily Threat Count')
ax3.tick_params(axis='x', rotation=45)
ax3.grid(True, alpha=0.3)

# 4. Heatmap of threats by type and level
heatmap_data = df.pivot_table(values='threat_count', 
                             index='attack_type', 
                             columns='threat_level', 
                             aggfunc='sum', 
                             fill_value=0)
sns.heatmap(heatmap_data, annot=True, fmt='d', cmap='Reds', ax=ax4)
ax4.set_title('Threat Intensity Heatmap')

plt.tight_layout()

# Convert to base64 for web display
buffer = io.BytesIO()
plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
buffer.seek(0)
image_base64 = base64.b64encode(buffer.getvalue()).decode()
plt.close()

print("📈 Analytics dashboard generated successfully!")
print("🖼️  Image encoded in base64 for web display")
print(f"IMAGE_BASE64:{image_base64}")

# Summary statistics
print("\\n📊 Summary Statistics:")
print(f"   - Total threats analyzed: {df['threat_count'].sum()}")
print(f"   - Unique attack types: {df['attack_type'].nunique()}")
print(f"   - Date range: {df['date'].min()} to {df['date'].max()}")
print(f"   - Average daily threats: {df['threat_count'].mean():.1f}")

conn.close()
print("✅ Analysis complete!")
'''
    
    payload = {"code": python_code}
    response = requests.post(f"{BACKEND_URL}/api/python/execute", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Python analytics executed in {result['execution_time']:.3f}s")
        
        # Check if image was generated
        if "IMAGE_BASE64:" in result['result']:
            print("🖼️  Analytics dashboard image generated successfully!")
            print("   - Chart includes: threat types, levels, timeline, and heatmap")
            print("   - Image ready for display in frontend")
        else:
            print("⚠️  No image generated in output")
            
        # Show summary of output
        lines = result['result'].split('\n')
        summary_lines = [line for line in lines if '📊' in line or '✅' in line or '🖼️' in line]
        for line in summary_lines[:5]:
            print(f"   {line}")
            
    else:
        print(f"❌ Python analytics failed: {response.status_code}")
        if response.text:
            print(f"   Error: {response.text}")
    
    return response.status_code == 200

def test_query_history():
    """Test query history API"""
    print("\n📝 Testing Query History...")
    
    response = requests.get(f"{BACKEND_URL}/api/query/history?limit=5")
    if response.status_code == 200:
        history = response.json()
        print(f"✅ Found {len(history)} recent queries")
        for query in history[:3]:
            print(f"   - {query['query_type']}: {query['status']} ({query['execution_time']:.3f}s)")
    else:
        print(f"❌ Query history failed: {response.status_code}")
    
    return response.status_code == 200

def main():
    """Run complete system demo"""
    print("🚀 Starting Complete Cybersecurity Platform Demo")
    print("=" * 60)
    
    # Test all components
    tests = [
        ("Database API", test_database_api),
        ("SQL Execution", test_sql_execution),
        ("Python Analytics", test_python_analytics),
        ("Query History", test_query_history),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
        
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 DEMO RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
        print(f"🌐 Frontend available at: {FRONTEND_URL}")
        print(f"🔧 Backend API available at: {BACKEND_URL}")
        print("\n📱 Available Features:")
        print("   - Real-time threat monitoring")
        print("   - PostgreSQL database explorer")
        print("   - Custom SQL query execution")
        print("   - Python analytics with image generation")
        print("   - Query execution history")
        print("   - WebSocket real-time updates")
    else:
        print("⚠️  Some components need attention")
    
    print("\n🔗 Access the dashboard at: http://localhost:3000")

if __name__ == "__main__":
    main()
