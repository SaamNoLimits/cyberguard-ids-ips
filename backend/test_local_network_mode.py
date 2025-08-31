#!/usr/bin/env python3
"""
Test script for Local Network Only monitoring mode
"""

import requests
import json
import time
from datetime import datetime

API_BASE = "http://localhost:8000"

def test_monitoring_status():
    """Test getting monitoring status"""
    print("🔍 Getting monitoring status...")
    try:
        response = requests.get(f"{API_BASE}/api/public/monitoring/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Monitoring Status:")
            print(f"   🏠 Local Network Only: {status['local_network_only']}")
            print(f"   🌐 Local Subnet: {status['local_subnet']}")
            print(f"   🔒 Monitor Internal Attacks: {status['monitor_internal_attacks']}")
            print(f"   🔌 Network Interface: {status['network_interface']}")
            print(f"   📊 Total Local IPs: {status['total_local_ips']}")
            print(f"   📋 Sample Local IPs: {', '.join(status['sample_local_ips'][:5])}")
            return status
        else:
            print(f"❌ Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None

def toggle_local_network_mode(enable=True):
    """Toggle local network monitoring mode"""
    action = "enable" if enable else "disable"
    print(f"🔄 Attempting to {action} local network mode...")
    
    try:
        response = requests.post(f"{API_BASE}/api/public/monitoring/local-network-mode?enable={enable}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result['message']}")
            print(f"   🏠 Local Network Only: {result['local_network_only']}")
            print(f"   🌐 Local Subnet: {result['local_subnet']}")
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None

def get_local_threats(internal_only=False):
    """Get local network threats"""
    filter_type = "internal only" if internal_only else "local network"
    print(f"📊 Getting {filter_type} threats...")
    
    try:
        response = requests.get(f"{API_BASE}/api/public/threats/local?limit=20&internal_only={internal_only}")
        if response.status_code == 200:
            data = response.json()
            threats = data['threats']
            filter_info = data['filter_info']
            
            print(f"✅ Found {len(threats)} {filter_type} threats (Total in DB: {filter_info['total_all_threats']})")
            print(f"   🌐 Filter Subnet: {filter_info['local_subnet']}")
            print(f"   🔒 Internal Only: {filter_info['internal_only']}")
            
            # Show first few threats
            for i, threat in enumerate(threats[:5]):
                timestamp = datetime.fromisoformat(threat['timestamp'].replace('Z', '+00:00'))
                print(f"   {i+1}. 🚨 {threat['attack_type']} - {threat['threat_level']}")
                print(f"      📡 {threat['source_ip']} → {threat['destination_ip']}")
                print(f"      ⏰ {timestamp.strftime('%H:%M:%S')}")
                print(f"      🔍 Confidence: {threat['confidence']:.1%}")
            
            if len(threats) > 5:
                print(f"   ... and {len(threats) - 5} more threats")
                
            return threats
        else:
            print(f"❌ Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None

def compare_threat_modes():
    """Compare threats in different modes"""
    print("\n" + "="*60)
    print("🔄 COMPARING THREAT DETECTION MODES")
    print("="*60)
    
    # Test with local network mode disabled
    print("\n1️⃣ TESTING: All Network Mode (Local Network Mode OFF)")
    print("-" * 50)
    toggle_local_network_mode(False)
    time.sleep(2)
    all_threats = requests.get(f"{API_BASE}/api/public/threats/recent?limit=50").json()
    print(f"📊 Total threats detected: {len(all_threats.get('threats', []))}")
    
    # Test with local network mode enabled
    print("\n2️⃣ TESTING: Local Network Mode (Local Network Mode ON)")
    print("-" * 50)
    toggle_local_network_mode(True)
    time.sleep(2)
    local_threats = get_local_threats(internal_only=False)
    
    # Test internal only
    print("\n3️⃣ TESTING: Internal Attacks Only")
    print("-" * 50)
    internal_threats = get_local_threats(internal_only=True)
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    print(f"🌐 All Network Threats: {len(all_threats.get('threats', []))}")
    print(f"🏠 Local Network Threats: {len(local_threats) if local_threats else 0}")
    print(f"🔒 Internal Only Threats: {len(internal_threats) if internal_threats else 0}")

def main():
    print("🚀 Local Network Monitoring Mode Test")
    print("=" * 50)
    
    # Get initial status
    initial_status = test_monitoring_status()
    if not initial_status:
        print("❌ Cannot connect to backend. Make sure it's running on localhost:8000")
        return
    
    print(f"\n💡 Your local network subnet: {initial_status['local_subnet']}")
    print(f"💡 Your Kali VM should be in this range to be detected")
    
    # Interactive menu
    while True:
        print("\n" + "="*50)
        print("🎯 CHOOSE AN ACTION:")
        print("1. 🔍 Check monitoring status")
        print("2. 🏠 Enable local network mode")
        print("3. 🌐 Disable local network mode")
        print("4. 📊 Get local network threats")
        print("5. 🔒 Get internal attacks only")
        print("6. 🔄 Compare all modes")
        print("7. ❌ Exit")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == "1":
            test_monitoring_status()
        elif choice == "2":
            toggle_local_network_mode(True)
        elif choice == "3":
            toggle_local_network_mode(False)
        elif choice == "4":
            get_local_threats(internal_only=False)
        elif choice == "5":
            get_local_threats(internal_only=True)
        elif choice == "6":
            compare_threat_modes()
        elif choice == "7":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
