#!/usr/bin/env python3
"""
Real-time Attack Monitor
Monitors attacks detected by the IDS system in real-time
"""

import requests
import time
import json
from datetime import datetime
import websocket
import threading

API_BASE = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"

class AttackMonitor:
    def __init__(self):
        self.last_threat_count = 0
        self.ws = None
        self.running = True
        
    def on_message(self, ws, message):
        """Handle WebSocket messages"""
        try:
            data = json.loads(message)
            if data.get("type") == "threat_alert":
                threat = data.get("data", {})
                print(f"\n🚨 REAL-TIME THREAT DETECTED!")
                print(f"   Time: {threat.get('timestamp', 'Unknown')}")
                print(f"   Source: {threat.get('source_ip', 'Unknown')}")
                print(f"   Target: {threat.get('destination_ip', 'Unknown')}")
                print(f"   Attack: {threat.get('attack_type', 'Unknown')}")
                print(f"   Level: {threat.get('threat_level', 'Unknown')}")
                print(f"   Confidence: {threat.get('confidence', 0):.1%}")
                print(f"   Description: {threat.get('description', 'No description')}")
                print("-" * 60)
                
            elif data.get("type") == "kali_attack_alert":
                attack = data.get("data", {})
                print(f"\n🎯 KALI ATTACK DETECTED!")
                print(f"   Time: {attack.get('timestamp', 'Unknown')}")
                print(f"   Source: {attack.get('source_ip', 'Unknown')}")
                print(f"   Target: {attack.get('destination_ip', 'Unknown')}")
                print(f"   Tool: {attack.get('tool_detected', 'Unknown')}")
                print(f"   Attack: {attack.get('attack_type', 'Unknown')}")
                print(f"   Description: {attack.get('description', 'No description')}")
                print("-" * 60)
                
            elif data.get("type") == "stats_update":
                stats = data.get("data", {})
                network_stats = stats.get("network_stats", {})
                print(f"\n📊 Network Stats Update:")
                print(f"   Packets: {network_stats.get('total_packets', 0)}")
                print(f"   Devices: {network_stats.get('active_devices', 0)}")
                print(f"   Threats: {len(stats.get('recent_alerts', []))}")
                
        except Exception as e:
            print(f"Error processing WebSocket message: {e}")
    
    def on_error(self, ws, error):
        """Handle WebSocket errors"""
        print(f"WebSocket error: {error}")
    
    def on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close"""
        print("WebSocket connection closed")
    
    def on_open(self, ws):
        """Handle WebSocket open"""
        print("✅ WebSocket connected - monitoring real-time attacks...")
    
    def start_websocket(self):
        """Start WebSocket connection"""
        try:
            self.ws = websocket.WebSocketApp(WS_URL,
                                           on_message=self.on_message,
                                           on_error=self.on_error,
                                           on_close=self.on_close,
                                           on_open=self.on_open)
            self.ws.run_forever()
        except Exception as e:
            print(f"WebSocket connection failed: {e}")
    
    def monitor_api(self):
        """Monitor via API polling"""
        while self.running:
            try:
                # Get current stats
                response = requests.get(f"{API_BASE}/api/public/stats", timeout=5)
                if response.status_code == 200:
                    stats = response.json()
                    current_threats = stats.get("total_threats", 0)
                    
                    if current_threats > self.last_threat_count:
                        new_threats = current_threats - self.last_threat_count
                        print(f"\n📈 {new_threats} new threat(s) detected! Total: {current_threats}")
                        
                        # Get recent threats
                        response = requests.get(f"{API_BASE}/api/public/threats/recent", timeout=5)
                        if response.status_code == 200:
                            threats = response.json()
                            for threat in threats[-new_threats:]:
                                print(f"   🚨 {threat.get('attack_type', 'Unknown')} from {threat.get('source_ip', 'Unknown')}")
                        
                        self.last_threat_count = current_threats
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                print(f"API monitoring error: {e}")
                time.sleep(10)
    
    def start_monitoring(self):
        """Start monitoring"""
        print("🎯 Real-Time Attack Monitor")
        print("=" * 50)
        print(f"API: {API_BASE}")
        print(f"WebSocket: {WS_URL}")
        print()
        
        # Test API connectivity
        try:
            response = requests.get(f"{API_BASE}/health", timeout=5)
            if response.status_code == 200:
                print("✅ API connected")
            else:
                print("❌ API connection failed")
                return
        except Exception as e:
            print(f"❌ Cannot connect to API: {e}")
            return
        
        # Get initial stats
        try:
            response = requests.get(f"{API_BASE}/api/public/stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                self.last_threat_count = stats.get("total_threats", 0)
                print(f"📊 Initial threat count: {self.last_threat_count}")
        except:
            pass
        
        print("\n🚀 Starting real-time monitoring...")
        print("Launch attacks from your Kali VM now!")
        print("Press Ctrl+C to stop monitoring")
        print("-" * 60)
        
        # Start WebSocket in separate thread
        ws_thread = threading.Thread(target=self.start_websocket, daemon=True)
        ws_thread.start()
        
        # Start API monitoring in main thread
        try:
            self.monitor_api()
        except KeyboardInterrupt:
            print("\n🛑 Stopping monitor...")
            self.running = False

if __name__ == "__main__":
    monitor = AttackMonitor()
    monitor.start_monitoring()
