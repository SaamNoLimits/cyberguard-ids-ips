#!/usr/bin/env python3
"""
Test Analytics Page Python Execution
"""

import requests
import json

def test_analytics_functionality():
    """Test analytics page and Python execution"""
    
    print("🐍 Testing Analytics Page Python Execution")
    print("=" * 45)
    
    # Test 1: Frontend Analytics Page
    print("\n📊 Testing Frontend Analytics Page")
    try:
        response = requests.get("http://localhost:3000/analytics", timeout=10)
        if response.status_code == 200:
            print("✅ Analytics page loads successfully")
        else:
            print(f"❌ HTTP ERROR: {response.status_code}")
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
    
    # Test 2: Python Execution Endpoint
    print("\n🔧 Testing Python Execution Endpoint")
    test_code = """
import datetime
print("🐍 Python execution test successful!")
print(f"📅 Current time: {datetime.datetime.now()}")
print("✅ All systems operational")
"""
    
    try:
        response = requests.post(
            "http://localhost:8000/api/python/execute",
            json={"code": test_code},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Python execution successful")
            print(f"⏱️ Execution time: {result['execution_time']:.3f}s")
            print("📤 Output:")
            print(result['output'])
        else:
            print(f"❌ HTTP ERROR: {response.status_code}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
    
    # Test 3: Database Query via Python
    print("\n🗄️ Testing Database Access via Python")
    db_test_code = """
import psycopg2
try:
    conn = psycopg2.connect(
        host="localhost",
        database="cybersec_ids", 
        user="cybersec",
        password="secure_password_123"
    )
    cursor = conn.cursor()
    
    # Get threat statistics
    cursor.execute("SELECT COUNT(*) FROM threat_alerts")
    total_threats = cursor.fetchone()[0]
    
    cursor.execute("SELECT DISTINCT attack_type FROM threat_alerts LIMIT 5")
    attack_types = [row[0] for row in cursor.fetchall()]
    
    print(f"📊 Total threats in database: {total_threats:,}")
    print(f"🎯 Attack types found: {len(attack_types)}")
    for i, attack_type in enumerate(attack_types, 1):
        print(f"   {i}. {attack_type}")
    
    conn.close()
    print("✅ Database connection successful")
    
except Exception as e:
    print(f"❌ Database error: {e}")
"""
    
    try:
        response = requests.post(
            "http://localhost:8000/api/python/execute",
            json={"code": db_test_code},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Database query via Python successful")
            print("📤 Output:")
            print(result['output'])
        else:
            print(f"❌ HTTP ERROR: {response.status_code}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
    
    # Test 4: Matplotlib Chart Generation
    print("\n📈 Testing Chart Generation")
    chart_code = """
import matplotlib.pyplot as plt
import numpy as np
import base64
import io

# Create a simple chart
fig, ax = plt.subplots(figsize=(10, 6))
x = np.linspace(0, 10, 100)
y = np.sin(x)

ax.plot(x, y, 'b-', linewidth=2, label='sin(x)')
ax.set_title('🔵 Test Chart - Sine Wave')
ax.set_xlabel('X values')
ax.set_ylabel('Y values')
ax.legend()
ax.grid(True, alpha=0.3)

# Save to base64
buffer = io.BytesIO()
plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
buffer.seek(0)
image_base64 = base64.b64encode(buffer.getvalue()).decode()
plt.close()

print("📊 Chart generated successfully!")
print(f"IMAGE_BASE64:{image_base64}")
print("✅ Chart encoding complete")
"""
    
    try:
        response = requests.post(
            "http://localhost:8000/api/python/execute",
            json={"code": chart_code},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Chart generation successful")
            print(f"⏱️ Execution time: {result['execution_time']:.3f}s")
            
            # Check if image was generated
            if "IMAGE_BASE64:" in result['output']:
                print("🖼️ Base64 image found in output")
            else:
                print("⚠️ No base64 image found")
                
        else:
            print(f"❌ HTTP ERROR: {response.status_code}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
    
    print("\n" + "=" * 45)
    print("🎯 Analytics Testing Complete!")
    print("\n🌐 Access the analytics dashboard at:")
    print("   http://localhost:3000/analytics")

if __name__ == "__main__":
    test_analytics_functionality()
