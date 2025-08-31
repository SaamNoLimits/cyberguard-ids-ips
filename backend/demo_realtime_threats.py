#!/usr/bin/env python3
"""
Real-time Threat Generation Demo Script
Generates threats continuously for dashboard demonstration
"""

import requests
import time
import json
import random
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
GENERATE_ENDPOINT = f"{API_BASE_URL}/api/public/threats/generate"
STATS_ENDPOINT = f"{API_BASE_URL}/api/public/stats"
THREATS_ENDPOINT = f"{API_BASE_URL}/api/public/threats/recent"

def check_backend_status():
    """Check if backend is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def generate_threat():
    """Generate a single threat"""
    try:
        response = requests.post(GENERATE_ENDPOINT, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "threat" in data:
                threat = data["threat"]
                print(f"🚨 {datetime.now().strftime('%H:%M:%S')} - NEW THREAT DETECTED!")
                print(f"   📍 Source: {threat['source_ip']} → {threat['destination_ip']}")
                print(f"   🎯 Type: {threat['attack_type']}")
                print(f"   ⚠️  Level: {threat['threat_level']}")
                print(f"   📊 Confidence: {threat['confidence']:.1%}")
                print(f"   📝 Description: {threat['description']}")
                print(f"   🆔 ID: {threat['id'][:8]}...")
                print("-" * 60)
                return True
            else:
                print(f"❌ Error generating threat: {data}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def get_current_stats():
    """Get current system statistics"""
    try:
        response = requests.get(STATS_ENDPOINT, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def print_stats_summary(stats):
    """Print a summary of current statistics"""
    if not stats:
        return
    
    print(f"\n📊 CURRENT SYSTEM STATUS - {datetime.now().strftime('%H:%M:%S')}")
    print(f"   🎯 Total Threats: {stats['total_threats']}")
    print(f"   🔗 Active Connections: {stats['active_connections']}")
    
    # Threat levels
    levels = stats['threat_levels']
    print(f"   📈 Threat Levels:")
    for level, count in levels.items():
        if count > 0:
            emoji = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🟠", "CRITICAL": "🔴"}
            print(f"      {emoji.get(level, '⚪')} {level}: {count}")
    
    # Top attack types
    attacks = stats['attack_types']
    active_attacks = {k: v for k, v in attacks.items() if v > 0}
    if active_attacks:
        print(f"   🎯 Active Attack Types:")
        for attack_type, count in sorted(active_attacks.items(), key=lambda x: x[1], reverse=True)[:3]:
            print(f"      • {attack_type}: {count}")
    
    print("=" * 60)

def main():
    """Main demo function"""
    print("🔒 CYBERSECURITY IDS/IPS REAL-TIME THREAT DEMO")
    print("=" * 60)
    print("This script generates threats in real-time for dashboard demonstration.")
    print("Open http://localhost:3000/threat-monitoring to see live updates!")
    print("=" * 60)
    
    # Check backend status
    if not check_backend_status():
        print("❌ Backend is not running! Please start the backend first.")
        print("   Run: ./start_platform.sh")
        return
    
    print("✅ Backend is running!")
    
    # Show initial stats
    initial_stats = get_current_stats()
    if initial_stats:
        print_stats_summary(initial_stats)
    
    print("\n🚀 Starting real-time threat generation...")
    print("   Press Ctrl+C to stop\n")
    
    threat_count = 0
    
    try:
        while True:
            # Generate a threat
            if generate_threat():
                threat_count += 1
                
                # Show stats every 5 threats
                if threat_count % 5 == 0:
                    stats = get_current_stats()
                    if stats:
                        print_stats_summary(stats)
            
            # Random delay between 2-8 seconds for realistic simulation
            delay = random.uniform(2, 8)
            time.sleep(delay)
            
    except KeyboardInterrupt:
        print(f"\n\n🛑 Demo stopped by user")
        print(f"📊 Generated {threat_count} threats during this session")
        
        # Final stats
        final_stats = get_current_stats()
        if final_stats:
            print_stats_summary(final_stats)
        
        print("\n💡 Dashboard is still running at http://localhost:3000")
        print("   You can continue to monitor the threats that were generated!")

if __name__ == "__main__":
    main()
