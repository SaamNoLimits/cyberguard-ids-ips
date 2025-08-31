#!/usr/bin/env python3
"""
Real-time Cybersecurity IDS/IPS Platform - FastAPI Backend
Detects attacks from Kali VM and other sources
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import threading
import time

# Network monitoring imports
from scapy.all import sniff, IP, TCP, UDP, ICMP, ARP
import socket
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables
threats = []
websocket_connections = []
stats = {
    "total_threats": 0,
    "active_connections": 0,
    "threat_levels": {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0},
    "attack_types": {},
    "last_updated": datetime.now().isoformat()
}

# Create FastAPI app
app = FastAPI(
    title="Cybersecurity IDS/IPS Platform",
    description="Real-time Intrusion Detection & Prevention System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ThreatDetector:
    def __init__(self):
        self.target_ip = "192.168.100.124"  # Your machine IP
        self.kali_ips = ["192.168.100.152", "192.168.100.153"]  # Common Kali IPs
        self.attack_patterns = {
            "syn_flood": {"count": 0, "threshold": 50},
            "port_scan": {"ports": set(), "threshold": 10},
            "icmp_flood": {"count": 0, "threshold": 20},
            "arp_scan": {"count": 0, "threshold": 30}
        }
        self.packet_counts = {}
        
    def detect_attack(self, packet):
        """Detect various types of attacks"""
        try:
            if not packet.haslayer(IP):
                return None
                
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            
            # Only monitor traffic to our target IP
            if dst_ip != self.target_ip:
                return None
                
            threat = None
            
            # TCP SYN Flood Detection
            if packet.haslayer(TCP) and packet[TCP].flags == 2:  # SYN flag
                self.attack_patterns["syn_flood"]["count"] += 1
                if self.attack_patterns["syn_flood"]["count"] > self.attack_patterns["syn_flood"]["threshold"]:
                    threat = {
                        "id": str(uuid.uuid4()),
                        "timestamp": datetime.now().isoformat(),
                        "source_ip": src_ip,
                        "destination_ip": dst_ip,
                        "attack_type": "Flood Attacks",
                        "threat_level": "HIGH",
                        "confidence": 95.0,
                        "description": f"SYN flood attack detected from {src_ip}",
                        "blocked": False,
                        "raw_data": {
                            "protocol": "TCP",
                            "src_port": packet[TCP].sport,
                            "dst_port": packet[TCP].dport,
                            "flags": packet[TCP].flags
                        }
                    }
                    self.attack_patterns["syn_flood"]["count"] = 0  # Reset counter
            
            # Port Scan Detection
            elif packet.haslayer(TCP):
                port = packet[TCP].dport
                self.attack_patterns["port_scan"]["ports"].add(port)
                if len(self.attack_patterns["port_scan"]["ports"]) > self.attack_patterns["port_scan"]["threshold"]:
                    threat = {
                        "id": str(uuid.uuid4()),
                        "timestamp": datetime.now().isoformat(),
                        "source_ip": src_ip,
                        "destination_ip": dst_ip,
                        "attack_type": "Reconnaissance",
                        "threat_level": "MEDIUM",
                        "confidence": 85.0,
                        "description": f"Port scan detected from {src_ip} - {len(self.attack_patterns['port_scan']['ports'])} ports scanned",
                        "blocked": False,
                        "raw_data": {
                            "protocol": "TCP",
                            "scanned_ports": list(self.attack_patterns["port_scan"]["ports"])[-10:],  # Last 10 ports
                            "total_ports": len(self.attack_patterns["port_scan"]["ports"])
                        }
                    }
                    self.attack_patterns["port_scan"]["ports"].clear()  # Reset
            
            # ICMP Flood Detection
            elif packet.haslayer(ICMP):
                self.attack_patterns["icmp_flood"]["count"] += 1
                if self.attack_patterns["icmp_flood"]["count"] > self.attack_patterns["icmp_flood"]["threshold"]:
                    threat = {
                        "id": str(uuid.uuid4()),
                        "timestamp": datetime.now().isoformat(),
                        "source_ip": src_ip,
                        "destination_ip": dst_ip,
                        "attack_type": "Flood Attacks",
                        "threat_level": "MEDIUM",
                        "confidence": 80.0,
                        "description": f"ICMP flood attack detected from {src_ip}",
                        "blocked": False,
                        "raw_data": {
                            "protocol": "ICMP",
                            "type": packet[ICMP].type,
                            "code": packet[ICMP].code
                        }
                    }
                    self.attack_patterns["icmp_flood"]["count"] = 0
            
            # ARP Scan Detection
            elif packet.haslayer(ARP):
                self.attack_patterns["arp_scan"]["count"] += 1
                if self.attack_patterns["arp_scan"]["count"] > self.attack_patterns["arp_scan"]["threshold"]:
                    threat = {
                        "id": str(uuid.uuid4()),
                        "timestamp": datetime.now().isoformat(),
                        "source_ip": src_ip,
                        "destination_ip": dst_ip,
                        "attack_type": "Reconnaissance",
                        "threat_level": "LOW",
                        "confidence": 70.0,
                        "description": f"ARP scan detected from {src_ip}",
                        "blocked": False,
                        "raw_data": {
                            "protocol": "ARP",
                            "operation": packet[ARP].op
                        }
                    }
                    self.attack_patterns["arp_scan"]["count"] = 0
            
            return threat
            
        except Exception as e:
            logger.error(f"Error in attack detection: {e}")
            return None

# Global threat detector
detector = ThreatDetector()

def packet_handler(packet):
    """Handle captured packets"""
    threat = detector.detect_attack(packet)
    if threat:
        # Add to threats list
        threats.append(threat)
        
        # Keep only last 1000 threats
        if len(threats) > 1000:
            threats.pop(0)
        
        # Update stats
        stats["total_threats"] += 1
        stats["threat_levels"][threat["threat_level"]] += 1
        
        attack_type = threat["attack_type"]
        if attack_type in stats["attack_types"]:
            stats["attack_types"][attack_type] += 1
        else:
            stats["attack_types"][attack_type] = 1
            
        stats["last_updated"] = datetime.now().isoformat()
        
        logger.info(f"🚨 THREAT DETECTED: {threat['attack_type']} from {threat['source_ip']} -> {threat['destination_ip']}")
        
        # Broadcast to WebSocket clients
        asyncio.create_task(broadcast_threat(threat))

async def broadcast_threat(threat):
    """Broadcast threat to all WebSocket connections"""
    if websocket_connections:
        message = json.dumps({
            "type": "new_threat",
            "data": threat
        })
        
        # Send to all connected clients
        disconnected = []
        for websocket in websocket_connections:
            try:
                await websocket.send_text(message)
            except:
                disconnected.append(websocket)
        
        # Remove disconnected clients
        for ws in disconnected:
            websocket_connections.remove(ws)

def start_network_monitoring():
    """Start network packet capture"""
    try:
        logger.info("🔍 Starting network monitoring...")
        # Monitor all interfaces for packets to our target IP
        sniff(filter=f"host {detector.target_ip}", prn=packet_handler, store=0)
    except Exception as e:
        logger.error(f"❌ Network monitoring error: {e}")

# Start network monitoring in background thread
monitoring_thread = threading.Thread(target=start_network_monitoring, daemon=True)
monitoring_thread.start()

@app.get("/")
async def root():
    return {"message": "Cybersecurity IDS/IPS Platform - Real-time Detection Active", "status": "monitoring"}

@app.get("/api/public/stats")
async def get_stats():
    """Get real-time statistics"""
    stats["active_connections"] = len(websocket_connections)
    return stats

@app.get("/api/public/threats/recent")
async def get_recent_threats(limit: int = 50):
    """Get recent threats"""
    recent = threats[-limit:] if threats else []
    return recent

@app.post("/api/public/threats/generate")
async def generate_test_threat():
    """Generate a test threat for testing"""
    threat = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "source_ip": "192.168.100.200",
        "destination_ip": detector.target_ip,
        "attack_type": "Flood Attacks",
        "threat_level": "HIGH",
        "confidence": 100.0,
        "description": "Generated test threat",
        "blocked": False,
        "raw_data": {"test": True}
    }
    
    # Add to threats
    threats.append(threat)
    stats["total_threats"] += 1
    stats["threat_levels"]["HIGH"] += 1
    stats["attack_types"]["Flood Attacks"] = stats["attack_types"].get("Flood Attacks", 0) + 1
    stats["last_updated"] = datetime.now().isoformat()
    
    # Broadcast
    await broadcast_threat(threat)
    
    return threat

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    websocket_connections.append(websocket)
    logger.info(f"📡 WebSocket client connected. Total: {len(websocket_connections)}")
    
    try:
        while True:
            # Send periodic stats updates
            await asyncio.sleep(10)
            if websocket in websocket_connections:
                stats_message = json.dumps({
                    "type": "stats_update",
                    "data": stats
                })
                await websocket.send_text(stats_message)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)
        logger.info(f"📡 WebSocket client disconnected. Total: {len(websocket_connections)}")

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Real-time Cybersecurity IDS/IPS Platform...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
