#!/usr/bin/env python3
"""
Real-time Kali Attack Monitor
Monitors attacks specifically from Kali VM IP: 192.168.100.152
"""

import requests
import json
import time
from datetime import datetime
import sys

KALI_IP = "192.168.100.152"
TARGET_IP = "192.168.100.124"
API_BASE = "http://localhost:8000"

def get_recent_threats():
    """Get recent threats from the API"""
    try:
        response = requests.get(f"{API_BASE}/api/public/threats/recent?limit=50")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ API Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None

def filter_kali_attacks(threats_data):
    """Filter threats from Kali IP or targeting our system"""
    if not threats_data or 'threats' not in threats_data:
        return []
    
    kali_threats = []
    for threat in threats_data['threats']:
        # Check if attack is from Kali or targeting our system
        if (threat['source_ip'] == KALI_IP or 
            threat['destination_ip'] == TARGET_IP or
            threat['source_ip'] == TARGET_IP):
            kali_threats.append(threat)
    
    return kali_threats

def display_threat(threat):
    """Display threat information"""
    timestamp = datetime.fromisoformat(threat['timestamp'].replace('Z', '+00:00'))
    
    # Color coding for threat levels
    colors = {
        'CRITICAL': '\033[91m',  # Red
        'HIGH': '\033[93m',      # Yellow
        'MEDIUM': '\033[94m',    # Blue
        'LOW': '\033[92m'        # Green
    }
    reset_color = '\033[0m'
    
    threat_color = colors.get(threat['threat_level'], '')
    
    print(f"\n🚨 {threat_color}THREAT DETECTED{reset_color}")
    print(f"   📅 Time: {timestamp.strftime('%H:%M:%S')}")
    print(f"   🎯 Attack: {threat['attack_type']}")
    print(f"   ⚠️  Level: {threat_color}{threat['threat_level']}{reset_color}")
    print(f"   📡 Source: {threat['source_ip']}")
    print(f"   🎯 Target: {threat['destination_ip']}")
    print(f"   🔍 Confidence: {threat['confidence']:.1%}")
    print(f"   📝 Description: {threat['description']}")
    
    if threat['source_ip'] == KALI_IP:
        print(f"   🔥 {threat_color}*** KALI VM ATTACK CONFIRMED ***{reset_color}")

def main():
    print("🔍 Kali Attack Monitor Started")
    print(f"🎯 Monitoring attacks from Kali: {KALI_IP}")
    print(f"🛡️  Protecting target: {TARGET_IP}")
    print("=" * 50)
    
    seen_threats = set()
    
    while True:
        try:
            # Get recent threats
            threats_data = get_recent_threats()
            if not threats_data:
                time.sleep(5)
                continue
            
            # Filter for Kali attacks
            kali_threats = filter_kali_attacks(threats_data)
            
            # Display new threats
            new_threats = 0
            for threat in kali_threats:
                threat_id = threat['id']
                if threat_id not in seen_threats:
                    display_threat(threat)
                    seen_threats.add(threat_id)
                    new_threats += 1
            
            if new_threats > 0:
                print(f"\n📊 Total new threats detected: {new_threats}")
                print("=" * 50)
            else:
                # Show status every 10 seconds
                current_time = datetime.now().strftime('%H:%M:%S')
                print(f"⏰ {current_time} - Monitoring... (Total threats in DB: {len(threats_data.get('threats', []))})")
            
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
