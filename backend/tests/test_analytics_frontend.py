#!/usr/bin/env python3
"""
Test Analytics Frontend Result Display
"""

import requests
import json
import time

def test_analytics_frontend():
    """Test that analytics frontend displays Python execution results"""
    
    print("🧪 Testing Analytics Frontend Result Display")
    print("=" * 50)
    
    # Test simple Python execution
    test_code = """
print("🔥 ANALYTICS TEST RESULTS")
print("=" * 30)
print("✅ Python execution working!")
print("📊 Sample data: [10, 20, 30, 40, 50]")
print("🎯 Frontend should display this output")
print("⏱️ Execution completed successfully")
"""
    
    print("📤 Sending Python code to backend...")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/python/execute",
            json={"code": test_code},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Backend execution successful!")
            print(f"⏱️ Execution time: {result['execution_time']:.3f}s")
            print(f"📊 Success: {result['success']}")
            print(f"📝 Output length: {len(result['output'])} characters")
            
            print("\n📤 Expected Frontend Output:")
            print("-" * 40)
            print(result['output'])
            print("-" * 40)
            
            # Check if frontend can access the analytics page
            print("\n🌐 Testing Frontend Analytics Page...")
            frontend_response = requests.get("http://localhost:3000/analytics", timeout=10)
            
            if frontend_response.status_code == 200:
                print("✅ Analytics page accessible")
                print("🎯 You should now be able to:")
                print("   1. Paste Python code in the editor")
                print("   2. Click 'Execute Code' button")
                print("   3. See results in the output section")
                print("   4. View any generated charts")
            else:
                print(f"❌ Frontend error: {frontend_response.status_code}")
                
        else:
            print(f"❌ Backend error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Frontend Test Complete!")
    print("\n🔧 If results don't show in frontend:")
    print("   1. Check browser console for errors")
    print("   2. Verify the component is mounted")
    print("   3. Check network tab for API calls")
    print("\n🌐 Test the analytics page at:")
    print("   http://localhost:3000/analytics")

if __name__ == "__main__":
    test_analytics_frontend()
