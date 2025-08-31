#!/usr/bin/env python3
"""
Monitor attacks specifically from Kali VM 192.168.100.152
"""

import requests
import time
import json
from datetime import datetime

KALI_IP = "192.168.100.152"
API_BASE = "http://localhost:8000"

def monitor_kali_attacks():
    """Monitor attacks from Kali VM in real-time"""
    print(f"🔍 Monitoring attacks from Kali VM: {KALI_IP}")
    print("=" * 60)
    
    seen_threats = set()
    
    while True:
        try:
            # Get recent threats
            response = requests.get(f"{API_BASE}/api/public/threats/recent?limit=100")
            if response.status_code == 200:
                data = response.json()
                threats = data.get('threats', [])
                
                # Filter for Kali attacks
                kali_threats = [
                    threat for threat in threats 
                    if threat['source_ip'] == KALI_IP or threat['destination_ip'] == KALI_IP
                ]
                
                # Show new Kali attacks
                new_attacks = 0
                for threat in kali_threats:
                    threat_id = threat['id']
                    if threat_id not in seen_threats:
                        timestamp = datetime.fromisoformat(threat['timestamp'].replace('Z', '+00:00'))
                        
                        print(f"\n🚨 KALI ATTACK DETECTED!")
                        print(f"   ⏰ Time: {timestamp.strftime('%H:%M:%S')}")
                        print(f"   🎯 Attack: {threat['attack_type']}")
                        print(f"   ⚠️  Level: {threat['threat_level']}")
                        print(f"   📡 Source: {threat['source_ip']}")
                        print(f"   🎯 Target: {threat['destination_ip']}")
                        print(f"   🔍 Confidence: {threat['confidence']:.1%}")
                        print(f"   📝 Description: {threat['description']}")
                        
                        if threat['source_ip'] == KALI_IP:
                            print(f"   🔥 *** ATTACK FROM YOUR KALI VM ***")
                        else:
                            print(f"   🛡️  *** ATTACK TARGETING YOUR KALI VM ***")
                        
                        seen_threats.add(threat_id)
                        new_attacks += 1
                
                if new_attacks == 0:
                    # Show status
                    current_time = datetime.now().strftime('%H:%M:%S')
                    total_threats = len(threats)
                    local_threats = len([t for t in threats if t['source_ip'].startswith('192.168.100')])
                    print(f"⏰ {current_time} - Monitoring... (Total: {total_threats}, Local: {local_threats}, Kali: {len(kali_threats)})")
                else:
                    print(f"\n📊 New Kali attacks detected: {new_attacks}")
                    print("=" * 60)
            
            time.sleep(3)  # Check every 3 seconds
            
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_kali_attacks()
