#!/usr/bin/env python3
"""
Cybersecurity IDS/IPS Platform - FastAPI Backend
Integrates with existing React cybersecurity dashboard
"""

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, BackgroundTasks, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import uvicorn
import os
from contextlib import asynccontextmanager

# Import our modules
from core.config import settings
from core.security import verify_token, create_access_token
from core.database import get_db
from models.schemas import *
from services.ids_service import IDSService
from services.network_monitor import NetworkMonitor
from services.threat_intelligence import ThreatIntelligenceService
from services.blockchain_audit import BlockchainAudit
from services.websocket_manager import WebSocketManager
from services.database_service import database_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global services
ids_service = None
network_monitor = None
threat_intel = None
blockchain_audit = None
websocket_manager = WebSocketManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global ids_service, network_monitor, threat_intel, blockchain_audit
    
    logger.info("🚀 Starting Cybersecurity IDS/IPS Platform...")
    
    # Initialize services
    try:
        # Initialize database service first
        await database_service.initialize()
        logger.info("✅ Database service initialized")
        
        ids_service = IDSService()
        await ids_service.initialize()
        
        network_monitor = NetworkMonitor(ids_service=ids_service, websocket_manager=websocket_manager)
        await network_monitor.start()
        
        threat_intel = ThreatIntelligenceService()
        await threat_intel.initialize()
        
        blockchain_audit = BlockchainAudit()
        
        logger.info("✅ All services initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down services...")
    if network_monitor:
        await network_monitor.stop()
    logger.info("✅ Shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Cybersecurity IDS/IPS Platform",
    description="Advanced Intrusion Detection & Prevention System with IoT Analytics",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint to provide a simple API status message."""
    return {"message": "Cybersecurity IDS/IPS Platform API is running."}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Favicon endpoint to prevent 404 errors from browsers."""
    return Response(status_code=204)

# Security
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        payload = verify_token(credentials.credentials)
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "ids": ids_service is not None,
            "network_monitor": network_monitor is not None,
            "threat_intel": threat_intel is not None,
            "blockchain": blockchain_audit is not None
        }
    }

# Helper functions for threat filtering and pagination
async def get_filtered_threat_alerts(limit: int, offset: int, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get filtered threat alerts with pagination"""
    try:
        # Get all recent alerts from IDS service
        all_alerts = await ids_service.get_recent_alerts(limit=1000) if ids_service else []
        
        # Convert to dict format for easier filtering
        alerts_dict = []
        for alert in all_alerts:
            if hasattr(alert, 'dict'):
                alert_dict = alert.dict()
            else:
                alert_dict = {
                    "id": getattr(alert, 'id', str(uuid.uuid4())),
                    "timestamp": getattr(alert, 'timestamp', datetime.utcnow()).isoformat(),
                    "source_ip": getattr(alert, 'source_ip', 'Unknown'),
                    "destination_ip": getattr(alert, 'destination_ip', 'Unknown'),
                    "attack_type": getattr(alert, 'attack_type', 'Unknown'),
                    "threat_level": getattr(alert, 'threat_level', 'MEDIUM'),
                    "confidence": getattr(alert, 'confidence', 0.5),
                    "description": getattr(alert, 'description', 'Threat detected'),
                    "blocked": getattr(alert, 'blocked', False)
                }
            alerts_dict.append(alert_dict)
        
        # Apply filters
        filtered_alerts = alerts_dict
        
        if filters.get('attack_type'):
            filtered_alerts = [a for a in filtered_alerts if filters['attack_type'].lower() in a.get('attack_type', '').lower()]
        
        if filters.get('threat_level'):
            filtered_alerts = [a for a in filtered_alerts if filters['threat_level'].upper() == a.get('threat_level', '').upper()]
        
        if filters.get('source_ip'):
            filtered_alerts = [a for a in filtered_alerts if filters['source_ip'] in a.get('source_ip', '')]
        
        if filters.get('search'):
            search_term = filters['search'].lower()
            filtered_alerts = [a for a in filtered_alerts if 
                             search_term in a.get('description', '').lower() or
                             search_term in a.get('source_ip', '').lower() or
                             search_term in a.get('attack_type', '').lower()]
        
        # Sort by timestamp (newest first)
        filtered_alerts.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Apply pagination
        paginated_alerts = filtered_alerts[offset:offset + limit]
        
        return paginated_alerts
        
    except Exception as e:
        logger.error(f"Error filtering threat alerts: {e}")
        return []

async def get_threat_count(filters: Dict[str, Any]) -> int:
    """Get total count of threats matching filters"""
    try:
        # Get all alerts and apply same filters to count
        filtered_alerts = await get_filtered_threat_alerts(limit=10000, offset=0, filters=filters)
        return len(filtered_alerts)
    except Exception as e:
        logger.error(f"Error getting threat count: {e}")
        return 0

# Authentication endpoints
@app.post("/auth/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """User login"""
    # For demo purposes - implement proper user authentication
    if credentials.username == "admin" and credentials.password == "cyberguard2024":
        token = create_access_token({"sub": credentials.username, "role": "admin"})
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=3600,
            user=UserResponse(
                id=1,
                username="admin",
                email="admin@cybersec.com",
                role="admin",
                is_active=True
            )
        )
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Dashboard endpoints
@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    """Get dashboard statistics"""
    try:
        # Get real-time stats from services
        network_stats = await network_monitor.get_stats() if network_monitor else {}
        threat_stats = await threat_intel.get_stats() if threat_intel else {}
        ids_stats = await ids_service.get_stats() if ids_service else {}
        
        return DashboardStats(
            total_devices=network_stats.get("total_devices", 0),
            active_threats=threat_stats.get("active_threats", 0),
            blocked_attacks=ids_stats.get("blocked_attacks", 0),
            network_traffic=network_stats.get("traffic_mbps", 0),
            threat_level=threat_stats.get("threat_level", "LOW"),
            uptime_hours=24,  # Calculate actual uptime
            last_updated=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard stats")

@app.get("/api/public/threats/recent")
async def get_recent_threats(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    attack_type: Optional[str] = Query(None),
    threat_level: Optional[str] = Query(None),
    source_ip: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """Get recent threats with pagination, filtering and search"""
    try:
        # Get filtered threats from database or cache
        filters = {
            "attack_type": attack_type,
            "threat_level": threat_level,
            "source_ip": source_ip,
            "search": search,
            "start_date": start_date,
            "end_date": end_date
        }
        
        recent_threats = await get_filtered_threat_alerts(
            limit=limit, 
            offset=offset, 
            filters=filters
        )
        
        # Get total count for pagination
        total_count = await get_threat_count(filters)
        
        return {
            "threats": recent_threats,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total_count
        }
    except Exception as e:
        logger.error(f"Error getting recent threats: {e}")
        return {
            "threats": [],
            "total": 0,
            "limit": limit,
            "offset": offset,
            "has_more": False
        }

@app.get("/api/public/threats/{threat_id}")
async def get_threat_details(threat_id: str):
    """Get detailed information about a specific threat"""
    try:
        # Get all recent alerts and find the specific one
        all_alerts = await ids_service.get_recent_alerts(limit=1000) if ids_service else []
        
        for alert in all_alerts:
            alert_id = getattr(alert, 'id', None)
            if str(alert_id) == threat_id:
                # Convert to detailed dict
                if hasattr(alert, 'dict'):
                    threat_details = alert.dict()
                else:
                    threat_details = {
                        "id": getattr(alert, 'id', str(uuid.uuid4())),
                        "timestamp": getattr(alert, 'timestamp', datetime.utcnow()).isoformat(),
                        "source_ip": getattr(alert, 'source_ip', 'Unknown'),
                        "destination_ip": getattr(alert, 'destination_ip', 'Unknown'),
                        "attack_type": getattr(alert, 'attack_type', 'Unknown'),
                        "threat_level": getattr(alert, 'threat_level', 'MEDIUM'),
                        "confidence": getattr(alert, 'confidence', 0.5),
                        "description": getattr(alert, 'description', 'Threat detected'),
                        "blocked": getattr(alert, 'blocked', False),
                        "raw_data": getattr(alert, 'raw_data', {})
                    }
                
                # Add additional analysis
                threat_details["analysis"] = {
                    "severity_score": threat_details.get("confidence", 0.5) * 100,
                    "risk_assessment": get_risk_assessment(threat_details),
                    "recommended_actions": get_recommended_actions(threat_details),
                    "similar_attacks": await get_similar_attacks(threat_details),
                    "geolocation": await get_ip_geolocation(threat_details.get("source_ip")),
                    "threat_intelligence": await get_threat_intelligence(threat_details.get("source_ip"))
                }
                
                return threat_details
        
        raise HTTPException(status_code=404, detail="Threat not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting threat details: {e}")
        raise HTTPException(status_code=500, detail="Failed to get threat details")

def get_risk_assessment(threat_details: Dict[str, Any]) -> str:
    """Generate risk assessment for a threat"""
    confidence = threat_details.get("confidence", 0.5)
    threat_level = threat_details.get("threat_level", "MEDIUM")
    
    if confidence > 0.9 and threat_level == "CRITICAL":
        return "EXTREME RISK - Immediate action required"
    elif confidence > 0.8 and threat_level in ["CRITICAL", "HIGH"]:
        return "HIGH RISK - Urgent attention needed"
    elif confidence > 0.6 and threat_level in ["HIGH", "MEDIUM"]:
        return "MODERATE RISK - Monitor closely"
    else:
        return "LOW RISK - Standard monitoring"

def get_recommended_actions(threat_details: Dict[str, Any]) -> List[str]:
    """Generate recommended actions for a threat"""
    actions = []
    attack_type = threat_details.get("attack_type", "")
    source_ip = threat_details.get("source_ip", "")
    
    if "Flood" in attack_type or "DDoS" in attack_type:
        actions.extend([
            "Implement rate limiting for source IP",
            "Consider blocking source IP temporarily",
            "Monitor network bandwidth usage",
            "Activate DDoS mitigation protocols"
        ])
    elif "Injection" in attack_type:
        actions.extend([
            "Review and sanitize input validation",
            "Check database query logs",
            "Implement WAF rules",
            "Audit application security"
        ])
    elif "Reconnaissance" in attack_type:
        actions.extend([
            "Monitor for follow-up attacks",
            "Review firewall rules",
            "Consider IP blocking",
            "Increase monitoring sensitivity"
        ])
    else:
        actions.extend([
            "Investigate source IP reputation",
            "Monitor for similar patterns",
            "Review security logs",
            "Consider blocking if pattern continues"
        ])
    
    return actions

async def get_similar_attacks(threat_details: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Find similar attacks in recent history"""
    try:
        attack_type = threat_details.get("attack_type", "")
        source_ip = threat_details.get("source_ip", "")
        
        # Get recent alerts
        all_alerts = await ids_service.get_recent_alerts(limit=100) if ids_service else []
        similar_attacks = []
        
        for alert in all_alerts:
            alert_attack_type = getattr(alert, 'attack_type', '')
            alert_source_ip = getattr(alert, 'source_ip', '')
            alert_id = getattr(alert, 'id', '')
            
            # Skip the same alert
            if str(alert_id) == threat_details.get("id"):
                continue
            
            # Find similar attacks
            if (attack_type == alert_attack_type or source_ip == alert_source_ip):
                similar_attacks.append({
                    "id": str(alert_id),
                    "timestamp": getattr(alert, 'timestamp', datetime.utcnow()).isoformat(),
                    "attack_type": alert_attack_type,
                    "source_ip": alert_source_ip,
                    "confidence": getattr(alert, 'confidence', 0.5)
                })
        
        return similar_attacks[:5]  # Return top 5 similar attacks
        
    except Exception as e:
        logger.error(f"Error finding similar attacks: {e}")
        return []

async def get_ip_geolocation(ip_address: str) -> Dict[str, Any]:
    """Get geolocation information for an IP address"""
    try:
        # Mock geolocation data - in production, use a real geolocation service
        return {
            "country": "Unknown",
            "region": "Unknown",
            "city": "Unknown",
            "latitude": 0.0,
            "longitude": 0.0,
            "isp": "Unknown",
            "organization": "Unknown"
        }
    except Exception as e:
        logger.error(f"Error getting geolocation: {e}")
        return {}

async def get_threat_intelligence(ip_address: str) -> Dict[str, Any]:
    """Get threat intelligence information for an IP address"""
    try:
        # Mock threat intelligence data - in production, integrate with threat intel feeds
        return {
            "reputation_score": 50,  # 0-100, higher is more malicious
            "known_malicious": False,
            "categories": [],
            "last_seen": None,
            "reports_count": 0,
            "sources": []
        }
    except Exception as e:
        logger.error(f"Error getting threat intelligence: {e}")
        return {}

@app.get("/api/network/topology", response_model=NetworkTopology)
async def get_network_topology(current_user: dict = Depends(get_current_user)):
    """Get network topology"""
    try:
        topology = await network_monitor.get_topology() if network_monitor else {}
        return topology
    except Exception as e:
        logger.error(f"Error getting network topology: {e}")
        raise HTTPException(status_code=500, detail="Failed to get network topology")

@app.get("/api/analytics/traffic", response_model=List[TrafficData])
async def get_traffic_analytics(
    hours: int = 24,
    current_user: dict = Depends(get_current_user)
):
    """Get traffic analytics data"""
    try:
        data = await network_monitor.get_traffic_analytics(hours) if network_monitor else []
        return data
    except Exception as e:
        logger.error(f"Error getting traffic analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get traffic analytics")

@app.get("/api/analytics/attacks", response_model=List[AttackData])
async def get_attack_analytics(
    hours: int = 24,
    current_user: dict = Depends(get_current_user)
):
    """Get attack analytics data"""
    try:
        data = await ids_service.get_attack_analytics(hours) if ids_service else []
        return data
    except Exception as e:
        logger.error(f"Error getting attack analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get attack analytics")

# IDS/IPS Management
@app.post("/api/ids/scan", response_model=ScanResult)
async def start_network_scan(
    scan_request: ScanRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Start network security scan"""
    try:
        scan_id = await ids_service.start_scan(scan_request)
        
        # Add blockchain audit entry
        audit_data = {
            "action": "network_scan_started",
            "user": current_user["sub"],
            "scan_id": scan_id,
            "target": scan_request.target,
            "timestamp": datetime.utcnow().isoformat()
        }
        blockchain_audit.add_block(audit_data)
        
        return ScanResult(
            scan_id=scan_id,
            status="started",
            message="Network scan initiated successfully"
        )
    except Exception as e:
        logger.error(f"Error starting network scan: {e}")
        raise HTTPException(status_code=500, detail="Failed to start network scan")

@app.get("/api/ids/scan/{scan_id}", response_model=ScanStatus)
async def get_scan_status(
    scan_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get scan status"""
    try:
        status = await ids_service.get_scan_status(scan_id)
        return status
    except Exception as e:
        logger.error(f"Error getting scan status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get scan status")

# Threat Intelligence
@app.get("/api/threat-intel/indicators", response_model=List[ThreatIndicator])
async def get_threat_indicators(
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Get threat intelligence indicators"""
    try:
        indicators = await threat_intel.get_indicators(limit) if threat_intel else []
        return indicators
    except Exception as e:
        logger.error(f"Error getting threat indicators: {e}")
        raise HTTPException(status_code=500, detail="Failed to get threat indicators")

# Blockchain Audit
@app.get("/api/audit/blockchain", response_model=List[BlockchainBlock])
async def get_blockchain_audit(
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Get blockchain audit trail"""
    try:
        blocks = blockchain_audit.get_recent_blocks(limit) if blockchain_audit else []
        return blocks
    except Exception as e:
        logger.error(f"Error getting blockchain audit: {e}")
        raise HTTPException(status_code=500, detail="Failed to get blockchain audit")

# Manual Threat Management
@app.post("/api/threats/{threat_id}/block")
async def block_threat(
    threat_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Manually block a threat"""
    try:
        if ids_service:
            success = await ids_service.block_threat(threat_id)
            if success:
                return {"message": f"Threat {threat_id} blocked successfully"}
            else:
                raise HTTPException(status_code=404, detail="Threat not found")
        raise HTTPException(status_code=503, detail="IDS service not available")
    except Exception as e:
        logger.error(f"Error blocking threat: {e}")
        raise HTTPException(status_code=500, detail="Failed to block threat")

@app.post("/api/threats/{threat_id}/unblock")
async def unblock_threat(
    threat_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Manually unblock a threat"""
    try:
        if ids_service:
            success = await ids_service.unblock_threat(threat_id)
            if success:
                return {"message": f"Threat {threat_id} unblocked successfully"}
            else:
                raise HTTPException(status_code=404, detail="Threat not found")
        raise HTTPException(status_code=503, detail="IDS service not available")
    except Exception as e:
        logger.error(f"Error unblocking threat: {e}")
        raise HTTPException(status_code=500, detail="Failed to unblock threat")

@app.get("/api/threats/{threat_id}/details")
async def get_threat_details(
    threat_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed threat information and recommendations"""
    try:
        if ids_service:
            details = await ids_service.get_threat_details(threat_id)
            if details:
                return details
            else:
                raise HTTPException(status_code=404, detail="Threat not found")
        raise HTTPException(status_code=503, detail="IDS service not available")
    except Exception as e:
        logger.error(f"Error getting threat details: {e}")
        raise HTTPException(status_code=500, detail="Failed to get threat details")

# Temporary endpoint for testing - inject sample threats
@app.post("/api/inject-sample-threats")
async def inject_sample_threats():
    """Inject sample threats for testing the enhanced dashboard"""
    try:
        if not ids_service:
            raise HTTPException(status_code=503, detail="IDS service not available")
        
        from models.schemas import AttackType, ThreatLevel
        from datetime import datetime, timedelta
        import uuid
        import random
        
        # Sample threat scenarios
        sample_scenarios = [
            {
                "source_ip": "192.168.1.100",
                "destination_ip": "192.168.1.1",
                "attack_type": AttackType.FLOOD_ATTACK,
                "threat_level": ThreatLevel.HIGH,
                "confidence": 0.92,
                "description": "High-volume flood attack detected from internal network",
                "protocol": 6, "source_port": 45231, "destination_port": 80, "packet_size": 1500, "ttl": 64
            },
            {
                "source_ip": "10.0.0.55",
                "destination_ip": "192.168.1.10",
                "attack_type": AttackType.BOTNET_MIRAI,
                "threat_level": ThreatLevel.CRITICAL,
                "confidence": 0.98,
                "description": "Mirai botnet activity detected - IoT device compromise attempt",
                "protocol": 6, "source_port": 23, "destination_port": 23, "packet_size": 512, "ttl": 32
            },
            {
                "source_ip": "203.0.113.42",
                "destination_ip": "192.168.1.50",
                "attack_type": AttackType.INJECTION_ATTACK,
                "threat_level": ThreatLevel.HIGH,
                "confidence": 0.87,
                "description": "SQL injection attempt detected on web application",
                "protocol": 6, "source_port": 54321, "destination_port": 443, "packet_size": 2048, "ttl": 56
            },
            {
                "source_ip": "198.51.100.15",
                "destination_ip": "192.168.1.1",
                "attack_type": AttackType.RECONNAISSANCE,
                "threat_level": ThreatLevel.MEDIUM,
                "confidence": 0.75,
                "description": "Port scanning activity detected from external source",
                "protocol": 6, "source_port": 12345, "destination_port": 22, "packet_size": 64, "ttl": 48
            },
            {
                "source_ip": "172.16.0.99",
                "destination_ip": "192.168.1.25",
                "attack_type": AttackType.SPOOFING_MITM,
                "threat_level": ThreatLevel.HIGH,
                "confidence": 0.89,
                "description": "ARP spoofing attack detected - potential man-in-the-middle",
                "protocol": 1, "packet_size": 128, "ttl": 64
            }
        ]
        
        created_threats = []
        
        for i, scenario in enumerate(sample_scenarios):
            # Create raw packet data
            raw_data = {
                "protocol": scenario["protocol"],
                "packet_size": scenario["packet_size"],
                "ttl": scenario["ttl"],
                "source_port": scenario.get("source_port"),
                "destination_port": scenario.get("destination_port"),
                "tcp_flags": random.randint(1, 255) if scenario["protocol"] == 6 else None,
                "window_size": random.randint(1024, 65535) if scenario["protocol"] == 6 else None,
                "icmp_type": 8 if scenario["protocol"] == 1 else None,
                "icmp_code": 0 if scenario["protocol"] == 1 else None
            }
            
            # Create threat alert
            from models.schemas import ThreatAlert
            
            threat_alert = ThreatAlert(
                id=str(uuid.uuid4()),
                timestamp=datetime.utcnow() - timedelta(minutes=i*5),
                source_ip=scenario["source_ip"],
                destination_ip=scenario["destination_ip"],
                attack_type=scenario["attack_type"],
                threat_level=scenario["threat_level"],
                confidence=scenario["confidence"],
                description=scenario["description"],
                blocked=False,
                raw_data=raw_data
            )
            
            # Add to IDS service
            ids_service.recent_alerts.append(threat_alert)
            ids_service.attack_stats["total_attacks"] += 1
            ids_service.attack_stats["attack_types"][scenario["attack_type"].value] += 1
            
            created_threats.append({
                "id": threat_alert.id,
                "attack_type": threat_alert.attack_type.value,
                "source_ip": threat_alert.source_ip,
                "threat_level": threat_alert.threat_level.value
            })
            
            # Broadcast via WebSocket
            if websocket_manager:
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
                
                await websocket_manager.broadcast(json.dumps(threat_data))
        
        logger.info(f"Injected {len(created_threats)} sample threats for testing")
        
        return {
            "message": f"Successfully injected {len(created_threats)} sample threats",
            "threats": created_threats
        }
        
    except Exception as e:
        logger.error(f"Error injecting sample threats: {e}")
        raise HTTPException(status_code=500, detail="Failed to inject sample threats")

# Public endpoints for testing (no auth required)
@app.get("/api/public/threats/recent")
async def get_public_recent_threats(limit: int = 50):
    """Get recent threat alerts (public endpoint for testing)"""
    try:
        if not ids_service:
            return []
        
        alerts = await ids_service.get_recent_alerts(limit)
        
        # Convert to dict format for JSON serialization
        threats_data = []
        for alert in alerts:
            threat_dict = {
                "id": alert.id,
                "timestamp": alert.timestamp.isoformat() if hasattr(alert.timestamp, 'isoformat') else str(alert.timestamp),
                "source_ip": alert.source_ip,
                "destination_ip": alert.destination_ip,
                "attack_type": alert.attack_type.value if hasattr(alert.attack_type, 'value') else str(alert.attack_type),
                "threat_level": alert.threat_level.value if hasattr(alert.threat_level, 'value') else str(alert.threat_level),
                "confidence": alert.confidence,
                "description": alert.description,
                "blocked": alert.blocked,
                "raw_data": alert.raw_data
            }
            threats_data.append(threat_dict)
        
        return threats_data
    except Exception as e:
        logger.error(f"Error getting public recent threats: {e}")
        return []

@app.post("/api/public/threats/generate")
async def generate_test_threat():
    """Generate a single test threat for real-time testing"""
    try:
        if not ids_service:
            return {"error": "IDS service not available"}
        
        import random
        from models.schemas import ThreatAlert, AttackType, ThreatLevel
        
        # Random threat scenarios
        scenarios = [
            {
                "source_ip": f"192.168.1.{random.randint(100, 200)}",
                "destination_ip": "192.168.1.1",
                "attack_type": AttackType.FLOOD_ATTACK,
                "threat_level": ThreatLevel.HIGH,
                "description": "DDoS flood attack detected from suspicious IP"
            },
            {
                "source_ip": f"10.0.0.{random.randint(50, 100)}",
                "destination_ip": "192.168.1.10",
                "attack_type": AttackType.BOTNET_MIRAI,
                "threat_level": ThreatLevel.CRITICAL,
                "description": "Mirai botnet activity detected"
            },
            {
                "source_ip": f"203.0.113.{random.randint(1, 50)}",
                "destination_ip": "192.168.1.25",
                "attack_type": AttackType.INJECTION_ATTACK,
                "threat_level": ThreatLevel.HIGH,
                "description": "SQL injection attempt detected"
            },
            {
                "source_ip": f"198.51.100.{random.randint(10, 30)}",
                "destination_ip": "192.168.1.50",
                "attack_type": AttackType.RECONNAISSANCE,
                "threat_level": ThreatLevel.MEDIUM,
                "description": "Port scanning activity detected"
            },
            {
                "source_ip": f"172.16.0.{random.randint(80, 120)}",
                "destination_ip": "192.168.1.25",
                "attack_type": AttackType.SPOOFING_MITM,
                "threat_level": ThreatLevel.HIGH,
                "description": "ARP spoofing attack detected"
            }
        ]
        
        scenario = random.choice(scenarios)
        
        # Create threat alert
        threat_alert = ThreatAlert(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            source_ip=scenario["source_ip"],
            destination_ip=scenario["destination_ip"],
            attack_type=scenario["attack_type"],
            threat_level=scenario["threat_level"],
            confidence=random.uniform(0.75, 0.95),
            description=scenario["description"],
            blocked=False,
            raw_data={
                "protocol": random.choice([6, 17, 1]),
                "packet_size": random.randint(64, 1500),
                "ttl": random.randint(32, 128)
            }
        )
        
        # Add to IDS service
        ids_service.recent_alerts.append(threat_alert)
        ids_service.attack_stats["total_attacks"] += 1
        ids_service.attack_stats["attack_types"][scenario["attack_type"].value] += 1
        
        # Broadcast via WebSocket
        threat_data = {
            "type": "new_threat",
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
        
        await websocket_manager.broadcast_json(threat_data)
        
        logger.info(f"🚨 Generated test threat: {scenario['attack_type'].value} from {scenario['source_ip']}")
        
        return {
            "message": "Test threat generated successfully",
            "threat": threat_data["data"]
        }
        
    except Exception as e:
        logger.error(f"Error generating test threat: {e}")
        return {"error": str(e)}

@app.get("/api/public/stats")
async def get_public_stats():
    """Get public statistics for dashboard"""
    try:
        stats = {
            "total_threats": 0,
            "active_connections": websocket_manager.get_connection_count(),
            "threat_levels": {
                "LOW": 0,
                "MEDIUM": 0,
                "HIGH": 0,
                "CRITICAL": 0
            },
            "attack_types": {
                "Flood Attacks": 0,
                "Botnet/Mirai Attacks": 0,
                "Backdoors & Exploits": 0,
                "Injection Attacks": 0,
                "Reconnaissance": 0,
                "Spoofing / MITM": 0
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
        if ids_service:
            recent_alerts = await ids_service.get_recent_alerts(100)
            stats["total_threats"] = len(recent_alerts)
            
            # Count by threat level
            for alert in recent_alerts:
                level = alert.threat_level.value if hasattr(alert.threat_level, 'value') else str(alert.threat_level)
                if level in stats["threat_levels"]:
                    stats["threat_levels"][level] += 1
            
            # Get attack type stats from IDS service
            stats["attack_types"] = ids_service.attack_stats["attack_types"]
        
        return stats
    except Exception as e:
        logger.error(f"Error getting public stats: {e}")
        return {"error": str(e)}

# Local Network Monitoring Endpoints
@app.post("/api/public/monitoring/local-network-mode")
async def toggle_local_network_mode(enable: bool = True):
    """Enable/disable local network only monitoring mode"""
    try:
        from core.config import settings
        settings.LOCAL_NETWORK_ONLY = enable
        
        mode_status = "enabled" if enable else "disabled"
        logger.info(f"🏠 Local network monitoring mode {mode_status}")
        
        return {
            "message": f"Local network monitoring mode {mode_status}",
            "local_network_only": enable,
            "local_subnet": settings.LOCAL_NETWORK_SUBNET,
            "monitor_internal_attacks": settings.MONITOR_INTERNAL_ATTACKS
        }
        
    except Exception as e:
        logger.error(f"Error toggling local network mode: {e}")
        return {"error": str(e)}

@app.get("/api/public/monitoring/status")
async def get_monitoring_status():
    """Get current monitoring configuration status"""
    try:
        from core.config import settings
        from utils.network_utils import get_local_network_ips
        
        # Get local network info
        local_ips = get_local_network_ips(settings.LOCAL_NETWORK_SUBNET)[:10]  # First 10 IPs
        
        return {
            "local_network_only": settings.LOCAL_NETWORK_ONLY,
            "local_subnet": settings.LOCAL_NETWORK_SUBNET,
            "monitor_internal_attacks": settings.MONITOR_INTERNAL_ATTACKS,
            "network_interface": settings.DEFAULT_NETWORK_INTERFACE,
            "sample_local_ips": local_ips,
            "total_local_ips": len(get_local_network_ips(settings.LOCAL_NETWORK_SUBNET))
        }
        
    except Exception as e:
        logger.error(f"Error getting monitoring status: {e}")
        return {"error": str(e)}

@app.get("/api/public/threats/local")
async def get_local_threats(limit: int = 50, offset: int = 0, internal_only: bool = False):
    """Get threats filtered for local network"""
    try:
        from utils.network_utils import filter_local_threats
        from core.config import settings
        
        # Get all recent threats
        all_threats = []
        if ids_service and hasattr(ids_service, 'recent_alerts'):
            all_threats = [
                {
                    "id": alert.id,
                    "timestamp": alert.timestamp.isoformat(),
                    "source_ip": alert.source_ip,
                    "destination_ip": alert.destination_ip,
                    "attack_type": alert.attack_type.value,
                    "threat_level": alert.threat_level.value,
                    "confidence": alert.confidence,
                    "description": alert.description,
                    "blocked": alert.blocked,
                    "raw_data": alert.raw_data
                }
                for alert in ids_service.recent_alerts
            ]
        
        # Filter for local network threats
        local_threats = filter_local_threats(
            all_threats, 
            settings.LOCAL_NETWORK_SUBNET, 
            internal_only
        )
        
        # Apply pagination
        total = len(local_threats)
        paginated_threats = local_threats[offset:offset + limit]
        
        return {
            "threats": paginated_threats,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total,
            "filter_info": {
                "local_subnet": settings.LOCAL_NETWORK_SUBNET,
                "internal_only": internal_only,
                "total_all_threats": len(all_threats)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting local threats: {e}")
        return {"error": str(e)}

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Send periodic updates (increased interval to reduce load)
            await asyncio.sleep(10)
            
            # Check if websocket is still connected
            if websocket.client_state.name != 'CONNECTED':
                break
                
            # Get real-time data
            if ids_service and network_monitor:
                # Get recent alerts and convert to dict
                recent_alerts = await ids_service.get_recent_alerts(5)
                alerts_data = []
                for alert in recent_alerts:
                    alert_dict = {
                        "id": alert.id,
                        "timestamp": alert.timestamp.isoformat() if hasattr(alert.timestamp, 'isoformat') else str(alert.timestamp),
                        "source_ip": alert.source_ip,
                        "destination_ip": alert.destination_ip,
                        "attack_type": alert.attack_type.value if hasattr(alert.attack_type, 'value') else str(alert.attack_type),
                        "threat_level": alert.threat_level.value if hasattr(alert.threat_level, 'value') else str(alert.threat_level),
                        "confidence": alert.confidence,
                        "description": alert.description,
                        "blocked": alert.blocked,
                        "raw_data": alert.raw_data
                    }
                    alerts_data.append(alert_dict)
                
                data = {
                    "type": "stats_update",
                    "data": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "network_stats": await network_monitor.get_stats(),
                        "recent_alerts": alerts_data,
                        "threat_level": await threat_intel.get_current_threat_level() if threat_intel else "LOW"
                    }
                }
                await websocket_manager.send_personal_message(json.dumps(data), websocket)
                
    except WebSocketDisconnect:
        # Normal disconnection, no need to log
        websocket_manager.disconnect(websocket)
    except Exception as e:
        # Only log unexpected errors, not normal disconnections
        if "1001" not in str(e) and "1005" not in str(e) and "going away" not in str(e).lower():
            logger.error(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket)

# System configuration
@app.get("/api/system/config", response_model=SystemConfig)
async def get_system_config(current_user: dict = Depends(get_current_user)):
    """Get system configuration"""
    return SystemConfig(
        network_interfaces=await network_monitor.get_interfaces() if network_monitor else [],
        ml_model_status=await ids_service.get_model_status() if ids_service else "unknown",
        threat_feeds_enabled=await threat_intel.get_feeds_status() if threat_intel else [],
        blockchain_enabled=blockchain_audit is not None
    )

@app.post("/api/system/config")
async def update_system_config(
    config: SystemConfigUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update system configuration"""
    try:
        # Update configuration
        if network_monitor:
            await network_monitor.update_config(config.network_config)
        if ids_service:
            await ids_service.update_config(config.ids_config)
        if threat_intel:
            await threat_intel.update_config(config.threat_intel_config)
        
        # Add audit entry
        audit_data = {
            "action": "system_config_updated",
            "user": current_user["sub"],
            "timestamp": datetime.utcnow().isoformat(),
            "changes": config.dict()
        }
        blockchain_audit.add_block(audit_data)
        
        return {"status": "success", "message": "Configuration updated successfully"}
    except Exception as e:
        logger.error(f"Error updating system config: {e}")
        raise HTTPException(status_code=500, detail="Failed to update system configuration")

# =============================================================================
# DATABASE & PCAP ENDPOINTS
# =============================================================================

@app.get("/api/database/threats/recent")
async def get_database_threats(limit: int = 50, offset: int = 0):
    """Get recent threats from database with PCAP info"""
    try:
        threats = await database_service.get_recent_threats(limit=limit, offset=offset)
        return {
            "threats": threats,
            "total": len(threats),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error getting database threats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve threats from database")

@app.get("/api/database/stats")
async def get_database_stats():
    """Get database statistics including PCAP storage info"""
    try:
        stats = await database_service.get_threat_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve database statistics")

@app.get("/api/pcap/download/{threat_id}")
async def download_pcap_file(threat_id: str):
    """Download PCAP file for a specific threat"""
    try:
        # Get threat from database
        threats = await database_service.get_recent_threats(limit=1000)  # Search in recent threats
        threat = next((t for t in threats if t['id'] == threat_id), None)
        
        if not threat:
            raise HTTPException(status_code=404, detail="Threat not found")
        
        pcap_path = threat.get('pcap_file_path')
        if not pcap_path or not os.path.exists(pcap_path):
            raise HTTPException(status_code=404, detail="PCAP file not found")
        
        # Return file for download
        from fastapi.responses import FileResponse
        filename = f"threat_{threat_id}_{threat['attack_type']}.pcap"
        return FileResponse(
            path=pcap_path,
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading PCAP file: {e}")
        raise HTTPException(status_code=500, detail="Failed to download PCAP file")

@app.post("/api/database/cleanup")
async def cleanup_old_data(days_to_keep: int = 30):
    """Clean up old threat data and PCAP files"""
    try:
        await database_service.cleanup_old_data(days_to_keep=days_to_keep)
        return {"status": "success", "message": f"Cleaned up data older than {days_to_keep} days"}
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        raise HTTPException(status_code=500, detail="Failed to cleanup old data")

@app.post("/api/pcap/compress")
async def compress_old_pcap_files(days_old: int = 7):
    """Compress PCAP files older than specified days"""
    try:
        await database_service.compress_old_pcap_files(days_old=days_old)
        return {"status": "success", "message": f"Compressed PCAP files older than {days_old} days"}
    except Exception as e:
        logger.error(f"Error compressing PCAP files: {e}")
        raise HTTPException(status_code=500, detail="Failed to compress PCAP files")

@app.post("/api/database/query")
async def execute_sql_query(request: dict):
    """Execute custom SQL query for data analysis"""
    try:
        query = request.get("query", "").strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        # Security: Only allow SELECT statements
        if not query.upper().startswith("SELECT"):
            raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")
        
        # Execute query using database service
        result = await database_service.execute_custom_query(query)
        return {
            "columns": result["columns"],
            "rows": result["rows"],
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error executing SQL query: {e}")
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")

# =============================================================================
# PYTHON ANALYTICS ENDPOINTS
# =============================================================================

from services.python_executor import PythonExecutor

# Initialize Python executor
python_executor = None

def get_python_executor():
    global python_executor
    if python_executor is None:
        db_config = {
            "host": "localhost",
            "port": "5432",
            "database": "cybersec_ids",
            "user": "cybersec",
            "password": "secure_password_123"
        }
        python_executor = PythonExecutor(db_config)
    return python_executor

@app.post("/api/python/execute")
async def execute_python_script(request: dict):
    """
    Execute a Python script for data analysis
    """
    try:
        script_code = request.get("code", "")
        script_name = request.get("name", "analysis")
        
        if not script_code:
            raise HTTPException(status_code=400, detail="Script code is required")
        
        executor = get_python_executor()
        result = executor.execute_script(script_code, script_name)
        
        return {
            "success": result["success"],
            "output": result["output"],
            "error": result["error"],
            "execution_time": result["execution_time"],
            "generated_files": result["generated_files"],
            "timestamp": result["timestamp"]
        }
        
    except Exception as e:
        logger.error(f"Error executing Python script: {e}")
        raise HTTPException(status_code=500, detail=f"Script execution failed: {str(e)}")

@app.get("/api/python/test-db")
async def test_database_connection():
    """
    Test database connection for Python scripts
    """
    try:
        executor = get_python_executor()
        result = executor.test_database_connection()
        return result
        
    except Exception as e:
        logger.error(f"Error testing database connection: {e}")
        raise HTTPException(status_code=500, detail=f"Database test failed: {str(e)}")

@app.get("/api/python/sample-data")
async def get_sample_data(limit: int = 10):
    """
    Get sample data from the database for Python analysis
    """
    try:
        executor = get_python_executor()
        result = executor.get_sample_data(limit)
        return result
        
    except Exception as e:
        logger.error(f"Error fetching sample data: {e}")
        raise HTTPException(status_code=500, detail=f"Sample data fetch failed: {str(e)}")

@app.get("/api/python/download/{filename}")
async def download_analysis_file(filename: str):
    """
    Download generated analysis files (charts, reports, etc.)
    """
    try:
        from fastapi.responses import FileResponse
        import os
        
        file_path = f"/tmp/cybersec_analytics/{filename}"
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        raise HTTPException(status_code=500, detail=f"File download failed: {str(e)}")

# =============================================================================
# REPORTS ENDPOINTS
# =============================================================================

@app.get("/api/reports")
async def get_reports(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    analyst: Optional[str] = Query(None)
):
    """
    Get incident reports with filtering and pagination
    """
    try:
        # Build WHERE clause based on filters
        where_conditions = []
        params = []
        param_count = 1
        
        if status:
            where_conditions.append(f"status = ${param_count}")
            params.append(status)
            param_count += 1
            
        if severity:
            where_conditions.append(f"severity = ${param_count}")
            params.append(severity)
            param_count += 1
            
        if type:
            where_conditions.append(f"type = ${param_count}")
            params.append(type)
            param_count += 1
            
        if analyst:
            where_conditions.append(f"analyst ILIKE ${param_count}")
            params.append(f"%{analyst}%")
            param_count += 1
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        # Get reports with pagination
        query = f"""
            SELECT 
                id, title, type, severity, status, created_at, updated_at,
                description, analyst, resolution, metadata
            FROM incident_reports 
            {where_clause}
            ORDER BY created_at DESC 
            LIMIT ${param_count} OFFSET ${param_count + 1}
        """
        params.extend([limit, offset])
        
        result = await database_service.execute_query(query, params)
        reports = []
        
        for row in result:
            report = {
                "id": row[0],
                "title": row[1],
                "type": row[2],
                "severity": row[3],
                "status": row[4],
                "createdAt": row[5].isoformat() if row[5] else None,
                "updatedAt": row[6].isoformat() if row[6] else None,
                "description": row[7],
                "analyst": row[8],
                "resolution": row[9],
                "metadata": row[10] or {}
            }
            
            # Get affected systems
            systems_query = "SELECT system_name FROM report_affected_systems WHERE report_id = $1"
            systems_result = await database_service.execute_query(systems_query, [report["id"]])
            report["affectedSystems"] = [row[0] for row in systems_result]
            
            # Get threat count
            threats_query = "SELECT COUNT(*) FROM report_threats WHERE report_id = $1"
            threats_result = await database_service.execute_query(threats_query, [report["id"]])
            report["threatCount"] = threats_result[0][0] if threats_result else 0
            
            reports.append(report)
        
        # Get total count
        count_query = f"SELECT COUNT(*) FROM incident_reports {where_clause}"
        count_params = params[:-2]  # Remove limit and offset
        count_result = await database_service.execute_query(count_query, count_params)
        total_count = count_result[0][0] if count_result else 0
        
        return {
            "reports": reports,
            "total": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error fetching reports: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch reports: {str(e)}")

@app.get("/api/reports/stats")
async def get_reports_statistics():
    """
    Get reports statistics
    """
    try:
        query = "SELECT * FROM report_statistics"
        result = await database_service.execute_query(query, [])
        
        if result:
            row = result[0]
            return {
                "totalReports": row[0],
                "openReports": row[1],
                "investigatingReports": row[2],
                "resolvedReports": row[3],
                "criticalReports": row[4],
                "highReports": row[5],
                "mediumReports": row[6],
                "lowReports": row[7],
                "reportsLast24h": row[8],
                "reportsLast7d": row[9],
                "reportsLast30d": row[10]
            }
        else:
            return {
                "totalReports": 0,
                "openReports": 0,
                "investigatingReports": 0,
                "resolvedReports": 0,
                "criticalReports": 0,
                "highReports": 0,
                "mediumReports": 0,
                "lowReports": 0,
                "reportsLast24h": 0,
                "reportsLast7d": 0,
                "reportsLast30d": 0
            }
        
    except Exception as e:
        logger.error(f"Error fetching reports statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch reports statistics: {str(e)}")

@app.get("/api/reports/{report_id}")
async def get_report_details(report_id: str):
    """
    Get detailed information about a specific report
    """
    try:
        # Get main report data
        query = """
            SELECT 
                id, title, type, severity, status, created_at, updated_at,
                description, analyst, resolution, metadata
            FROM incident_reports 
            WHERE id = $1
        """
        result = await database_service.execute_query(query, [report_id])
        
        if not result:
            raise HTTPException(status_code=404, detail="Report not found")
        
        row = result[0]
        report = {
            "id": row[0],
            "title": row[1],
            "type": row[2],
            "severity": row[3],
            "status": row[4],
            "createdAt": row[5].isoformat() if row[5] else None,
            "updatedAt": row[6].isoformat() if row[6] else None,
            "description": row[7],
            "analyst": row[8],
            "resolution": row[9],
            "metadata": row[10] or {}
        }
        
        # Get affected systems
        systems_query = "SELECT system_name FROM report_affected_systems WHERE report_id = $1"
        systems_result = await database_service.execute_query(systems_query, [report_id])
        report["affectedSystems"] = [row[0] for row in systems_result]
        
        # Get threats
        threats_query = "SELECT threat_data FROM report_threats WHERE report_id = $1"
        threats_result = await database_service.execute_query(threats_query, [report_id])
        report["threats"] = [row[0] for row in threats_result if row[0]]
        
        # Get comments
        comments_query = """
            SELECT comment_text, author, created_at 
            FROM report_comments 
            WHERE report_id = $1 
            ORDER BY created_at ASC
        """
        comments_result = await database_service.execute_query(comments_query, [report_id])
        report["comments"] = [
            {
                "text": row[0],
                "author": row[1],
                "timestamp": row[2].isoformat() if row[2] else None
            }
            for row in comments_result
        ]
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching report details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch report details: {str(e)}")

@app.post("/api/reports")
async def create_report(report_data: dict):
    """
    Create a new incident report
    """
    try:
        # Validate required fields
        required_fields = ["title", "description", "analyst"]
        for field in required_fields:
            if not report_data.get(field):
                raise HTTPException(status_code=400, detail=f"Field '{field}' is required")
        
        # Generate report ID
        report_id = f"RPT-{int(datetime.now().timestamp())}"
        
        # Insert main report
        insert_query = """
            INSERT INTO incident_reports 
            (id, title, type, severity, status, description, analyst, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id, created_at
        """
        
        params = [
            report_id,
            report_data["title"],
            report_data.get("type", "incident"),
            report_data.get("severity", "medium"),
            report_data.get("status", "open"),
            report_data["description"],
            report_data["analyst"],
            json.dumps(report_data.get("metadata", {}))
        ]
        
        result = await database_service.execute_query(insert_query, params)
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create report")
        
        created_id, created_at = result[0]
        
        # Insert affected systems
        affected_systems = report_data.get("affectedSystems", [])
        if affected_systems:
            for system in affected_systems:
                if system.strip():
                    await database_service.execute_query(
                        "INSERT INTO report_affected_systems (report_id, system_name) VALUES ($1, $2)",
                        [created_id, system.strip()]
                    )
        
        # Insert threat associations
        threats = report_data.get("threats", [])
        if threats:
            for threat in threats:
                await database_service.execute_query(
                    "INSERT INTO report_threats (report_id, threat_data) VALUES ($1, $2)",
                    [created_id, json.dumps(threat)]
                )
        
        return {
            "id": created_id,
            "message": "Report created successfully",
            "createdAt": created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create report: {str(e)}")

@app.put("/api/reports/{report_id}")
async def update_report(report_id: str, report_data: dict):
    """
    Update an existing incident report
    """
    try:
        # Check if report exists
        check_query = "SELECT id FROM incident_reports WHERE id = $1"
        check_result = await database_service.execute_query(check_query, [report_id])
        
        if not check_result:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Update main report
        update_query = """
            UPDATE incident_reports 
            SET title = $2, type = $3, severity = $4, status = $5, 
                description = $6, analyst = $7, resolution = $8, metadata = $9
            WHERE id = $1
            RETURNING updated_at
        """
        
        params = [
            report_id,
            report_data.get("title", ""),
            report_data.get("type", "incident"),
            report_data.get("severity", "medium"),
            report_data.get("status", "open"),
            report_data.get("description", ""),
            report_data.get("analyst", ""),
            report_data.get("resolution"),
            json.dumps(report_data.get("metadata", {}))
        ]
        
        result = await database_service.execute_query(update_query, params)
        updated_at = result[0][0] if result else None
        
        return {
            "id": report_id,
            "message": "Report updated successfully",
            "updatedAt": updated_at.isoformat() if updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update report: {str(e)}")

@app.delete("/api/reports/{report_id}")
async def delete_report(report_id: str):
    """
    Delete an incident report
    """
    try:
        # Check if report exists
        check_query = "SELECT id FROM incident_reports WHERE id = $1"
        check_result = await database_service.execute_query(check_query, [report_id])
        
        if not check_result:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Delete report (cascade will handle related records)
        delete_query = "DELETE FROM incident_reports WHERE id = $1"
        await database_service.execute_query(delete_query, [report_id])
        
        return {
            "id": report_id,
            "message": "Report deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete report: {str(e)}")

@app.post("/api/reports/{report_id}/comments")
async def add_report_comment(report_id: str, comment_data: dict):
    """
    Add a comment to a report
    """
    try:
        # Check if report exists
        check_query = "SELECT id FROM incident_reports WHERE id = $1"
        check_result = await database_service.execute_query(check_query, [report_id])
        
        if not check_result:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Validate comment data
        if not comment_data.get("text"):
            raise HTTPException(status_code=400, detail="Comment text is required")
        
        # Insert comment
        insert_query = """
            INSERT INTO report_comments (report_id, comment_text, author)
            VALUES ($1, $2, $3)
            RETURNING id, created_at
        """
        
        params = [
            report_id,
            comment_data["text"],
            comment_data.get("author", "Anonymous")
        ]
        
        result = await database_service.execute_query(insert_query, params)
        
        if result:
            comment_id, created_at = result[0]
            return {
                "id": comment_id,
                "message": "Comment added successfully",
                "createdAt": created_at.isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to add comment")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding comment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add comment: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
