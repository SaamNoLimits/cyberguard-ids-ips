#!/usr/bin/env python3
"""
Generate sample threats for testing the enhanced dashboard
"""
import asyncio
import json
import random
from datetime import datetime, timedelta
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.ids_service import IDSService, AttackType, ThreatLevel
from services.websocket_manager import WebSocketManager
from core.config import settings

async def generate_sample_threats():
    """Generate sample threats and broadcast them via WebSocket"""
    
    # Initialize services
    ids_service = IDSService()
    await ids_service.initialize()
    
    websocket_manager = WebSocketManager()
    
    # Sample attack scenarios
    attack_scenarios = [
        {
            "source_ip": "192.168.1.100",
            "destination_ip": "192.168.1.1",
            "attack_type": AttackType.FLOOD_ATTACK,
            "threat_level": ThreatLevel.HIGH,
            "confidence": 0.92,
            "description": "High-volume flood attack detected from internal network",
            "protocol": 6,  # TCP
            "source_port": 45231,
            "destination_port": 80,
            "packet_size": 1500,
            "ttl": 64
        },
        {
            "source_ip": "10.0.0.55",
            "destination_ip": "192.168.1.10",
            "attack_type": AttackType.BOTNET_MIRAI,
            "threat_level": ThreatLevel.CRITICAL,
            "confidence": 0.98,
            "description": "Mirai botnet activity detected - IoT device compromise attempt",
            "protocol": 6,  # TCP
            "source_port": 23,
            "destination_port": 23,
            "packet_size": 512,
            "ttl": 32
        },
        {
            "source_ip": "203.0.113.42",
            "destination_ip": "192.168.1.50",
            "attack_type": AttackType.INJECTION_ATTACK,
            "threat_level": ThreatLevel.HIGH,
            "confidence": 0.87,
            "description": "SQL injection attempt detected on web application",
            "protocol": 6,  # TCP
            "source_port": 54321,
            "destination_port": 443,
            "packet_size": 2048,
            "ttl": 56
        },
        {
            "source_ip": "198.51.100.15",
            "destination_ip": "192.168.1.1",
            "attack_type": AttackType.RECONNAISSANCE,
            "threat_level": ThreatLevel.MEDIUM,
            "confidence": 0.75,
            "description": "Port scanning activity detected from external source",
            "protocol": 6,  # TCP
            "source_port": 12345,
            "destination_port": 22,
            "packet_size": 64,
            "ttl": 48
        },
        {
            "source_ip": "172.16.0.99",
            "destination_ip": "192.168.1.25",
            "attack_type": AttackType.SPOOFING_MITM,
            "threat_level": ThreatLevel.HIGH,
            "confidence": 0.89,
            "description": "ARP spoofing attack detected - potential man-in-the-middle",
            "protocol": 1,  # ICMP
            "packet_size": 128,
            "ttl": 64,
            "icmp_type": 8,
            "icmp_code": 0
        }
    ]
    
    print("Generating sample threats...")
    
    for i, scenario in enumerate(attack_scenarios):
        # Create raw packet data
        raw_data = {
            "protocol": scenario["protocol"],
            "packet_size": scenario["packet_size"],
            "ttl": scenario["ttl"],
            "source_port": scenario.get("source_port"),
            "destination_port": scenario.get("destination_port"),
            "icmp_type": scenario.get("icmp_type"),
            "icmp_code": scenario.get("icmp_code"),
            "tcp_flags": random.randint(1, 255) if scenario["protocol"] == 6 else None,
            "window_size": random.randint(1024, 65535) if scenario["protocol"] == 6 else None
        }
        
        # Create threat alert manually
        from models.threat_alert import ThreatAlert
        import uuid
        
        threat_alert = ThreatAlert(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow() - timedelta(minutes=random.randint(1, 30)),
            source_ip=scenario["source_ip"],
            destination_ip=scenario["destination_ip"],
            attack_type=scenario["attack_type"],
            threat_level=scenario["threat_level"],
            confidence=scenario["confidence"],
            description=scenario["description"],
            blocked=False,  # Manual blocking only
            raw_data=raw_data
        )
        
        # Add to IDS service recent alerts
        ids_service.recent_alerts.append(threat_alert)
        ids_service.attack_stats["total_attacks"] += 1
        ids_service.attack_stats["attack_types"][scenario["attack_type"].value] += 1
        
        # Broadcast via WebSocket
        threat_data = {
            "type": "threat_alert",
            "data": {
                "id": threat_alert.id,
                "timestamp": threat_alert.timestamp.isoformat(),
                "source_ip": threat_alert.source_ip,
                "destination_ip": threat_alert.destination_ip,
                "attack_type": threat_alert.attack_type.value,
                "threat_level": threat_alert.threat_level.value,
                "confidence": threat_alert.confidence,
                "description": threat_alert.description,
                "blocked": threat_alert.blocked,
                "raw_data": threat_alert.raw_data
            }
        }
        
        await websocket_manager.broadcast_message(json.dumps(threat_data))
        print(f"Generated threat {i+1}: {scenario['attack_type'].value} from {scenario['source_ip']}")
        
        # Wait a bit between threats
        await asyncio.sleep(1)
    
    print(f"Generated {len(attack_scenarios)} sample threats successfully!")
    print("Check the dashboard to see the threats and test the detailed view by clicking on them.")

if __name__ == "__main__":
    asyncio.run(generate_sample_threats())
