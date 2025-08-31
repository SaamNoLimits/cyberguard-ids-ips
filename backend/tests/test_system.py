#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

BACKEND_URL = "http://localhost:8000"

def test_database():
    print("Testing Database API...")
    response = requests.get(f"{BACKEND_URL}/api/database/tables")
    if response.status_code == 200:
        tables = response.json()
        print(f"SUCCESS: Found {len(tables)} database tables")
        return True
    else:
        print(f"FAILED: {response.status_code}")
        return False

def test_sql():
    print("Testing SQL Execution...")
    query = {"query": "SELECT COUNT(*) as total FROM threat_alerts"}
    response = requests.post(f"{BACKEND_URL}/api/sql/execute", json=query)
    if response.status_code == 200:
        result = response.json()
        print(f"SUCCESS: SQL executed in {result['execution_time']:.3f}s")
        return True
    else:
        print(f"FAILED: {response.status_code}")
        return False

def test_python():
    print("Testing Python Analytics...")
    code = '''
import matplotlib.pyplot as plt
import numpy as np
import base64
import io

print("Creating analytics chart...")

# Create sample data
x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(10, 6))
plt.plot(x, y, 'b-', linewidth=2)
plt.title('Sample Analytics Chart')
plt.xlabel('X values')
plt.ylabel('Sin(X)')
plt.grid(True)

# Convert to base64
buffer = io.BytesIO()
plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
buffer.seek(0)
image_base64 = base64.b64encode(buffer.getvalue()).decode()
plt.close()

print("Chart generated successfully!")
print(f"IMAGE_BASE64:{image_base64}")
'''
    
    payload = {"code": code}
    response = requests.post(f"{BACKEND_URL}/api/python/execute", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"SUCCESS: Python executed in {result['execution_time']:.3f}s")
        if "IMAGE_BASE64:" in result['result']:
            print("SUCCESS: Image generated!")
        return True
    else:
        print(f"FAILED: {response.status_code}")
        return False

def main():
    print("=== CYBERSECURITY PLATFORM SYSTEM TEST ===")
    
    tests = [
        ("Database API", test_database),
        ("SQL Execution", test_sql),
        ("Python Analytics", test_python),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        try:
            success = test_func()
            results.append(success)
        except Exception as e:
            print(f"ERROR: {e}")
            results.append(False)
    
    print(f"\n=== RESULTS ===")
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("ALL SYSTEMS OPERATIONAL!")
        print("Frontend: http://localhost:3000")
        print("Backend: http://localhost:8000")
    else:
        print("Some tests failed - check logs")

if __name__ == "__main__":
    main()
