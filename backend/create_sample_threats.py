#!/usr/bin/env python3
"""
Create sample threats by directly adding them to the running backend
"""
import requests
import json
import time
from datetime import datetime, timedelta
import uuid
import random

# Backend API URL
API_BASE = "http://localhost:8000"

def create_sample_threats():
    """Create sample threats by directly calling the backend"""
    
    # Sample attack scenarios
    sample_threats = [
        {
            "id": str(uuid.uuid4()),
            "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
            "source_ip": "192.168.1.100",
            "destination_ip": "192.168.1.1",
            "attack_type": "Flood Attacks",
            "threat_level": "HIGH",
            "confidence": 0.92,
            "description": "High-volume flood attack detected from internal network",
            "blocked": False,
            "raw_data": {
                "protocol": 6,
                "packet_size": 1500,
                "ttl": 64,
                "source_port": 45231,
                "destination_port": 80,
                "tcp_flags": 24,
                "window_size": 8192
            }
        },
        {
            "id": str(uuid.uuid4()),
            "timestamp": (datetime.utcnow() - timedelta(minutes=10)).isoformat(),
            "source_ip": "10.0.0.55",
            "destination_ip": "192.168.1.10",
            "attack_type": "Botnet/Mirai Attacks",
            "threat_level": "CRITICAL",
            "confidence": 0.98,
            "description": "Mirai botnet activity detected - IoT device compromise attempt",
            "blocked": False,
            "raw_data": {
                "protocol": 6,
                "packet_size": 512,
                "ttl": 32,
                "source_port": 23,
                "destination_port": 23,
                "tcp_flags": 2,
                "window_size": 1024
            }
        },
        {
            "id": str(uuid.uuid4()),
            "timestamp": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
            "source_ip": "203.0.113.42",
            "destination_ip": "192.168.1.50",
            "attack_type": "Injection Attacks",
            "threat_level": "HIGH",
            "confidence": 0.87,
            "description": "SQL injection attempt detected on web application",
            "blocked": False,
            "raw_data": {
                "protocol": 6,
                "packet_size": 2048,
                "ttl": 56,
                "source_port": 54321,
                "destination_port": 443,
                "tcp_flags": 24,
                "window_size": 4096
            }
        },
        {
            "id": str(uuid.uuid4()),
            "timestamp": (datetime.utcnow() - timedelta(minutes=20)).isoformat(),
            "source_ip": "198.51.100.15",
            "destination_ip": "192.168.1.1",
            "attack_type": "Reconnaissance",
            "threat_level": "MEDIUM",
            "confidence": 0.75,
            "description": "Port scanning activity detected from external source",
            "blocked": False,
            "raw_data": {
                "protocol": 6,
                "packet_size": 64,
                "ttl": 48,
                "source_port": 12345,
                "destination_port": 22,
                "tcp_flags": 2,
                "window_size": 512
            }
        },
        {
            "id": str(uuid.uuid4()),
            "timestamp": (datetime.utcnow() - timedelta(minutes=25)).isoformat(),
            "source_ip": "172.16.0.99",
            "destination_ip": "192.168.1.25",
            "attack_type": "Spoofing / MITM",
            "threat_level": "HIGH",
            "confidence": 0.89,
            "description": "ARP spoofing attack detected - potential man-in-the-middle",
            "blocked": False,
            "raw_data": {
                "protocol": 1,
                "packet_size": 128,
                "ttl": 64,
                "icmp_type": 8,
                "icmp_code": 0
            }
        }
    ]
    
    print("Creating sample threats...")
    
    # First, check if backend is running
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code != 200:
            print("Backend is not responding properly")
            return
    except requests.exceptions.RequestException as e:
        print(f"Cannot connect to backend: {e}")
        return
    
    # Create a simple endpoint to inject sample data
    # Since we can't easily modify the running service, let's use WebSocket to send the data
    import websocket
    import threading
    
    def on_message(ws, message):
        print(f"Received: {message}")
    
    def on_error(ws, error):
        print(f"WebSocket error: {error}")
    
    def on_close(ws, close_status_code, close_msg):
        print("WebSocket connection closed")
    
    def on_open(ws):
        print("WebSocket connection opened")
        
        # Send sample threats
        for i, threat in enumerate(sample_threats):
            threat_data = {
                "type": "threat_alert",
                "data": threat
            }
            
            print(f"Sending threat {i+1}: {threat['attack_type']} from {threat['source_ip']}")
            ws.send(json.dumps(threat_data))
            time.sleep(1)
        
        print("All sample threats sent!")
        ws.close()
    
    # Connect to WebSocket
    ws_url = "ws://localhost:8000/ws"
    print(f"Connecting to WebSocket: {ws_url}")
    
    ws = websocket.WebSocketApp(ws_url,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    
    ws.run_forever()

if __name__ == "__main__":
    create_sample_threats()
