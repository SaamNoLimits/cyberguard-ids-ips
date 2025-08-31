"""
Intrusion Detection System Service
Integrates with the trained LightGBM model from IoTCIC analysis
"""

import asyncio
import pickle
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import uuid
import logging
from pathlib import Path

from models.schemas import ThreatAlert, AttackType, ThreatLevel, ScanResult, ScanStatus, AttackData
from core.config import settings

logger = logging.getLogger(__name__)

class IDSService:
    """Intrusion Detection System Service"""
    
    def __init__(self):
        self.model_pipeline = None
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_names = None
        self.is_initialized = False
        self.active_scans = {}
        self.recent_alerts = []
        self.attack_stats = {
            "total_attacks": 0,
            "blocked_attacks": 0,
            "attack_types": {
                "Flood Attacks": 0,
                "Botnet/Mirai Attacks": 0,
                "Backdoors & Exploits": 0,
                "Injection Attacks": 0,
                "Reconnaissance": 0,
                "Spoofing / MITM": 0,
                "Benign": 0
            },
            "hourly_stats": []
        }
        
    async def initialize(self):
        """Initialize the IDS service"""
        try:
            await self.load_ml_model()
            self.is_initialized = True
            logger.info("✅ IDS Service initialized successfully")
            
            # Generate sample threats for testing
            await self._generate_sample_threats()
        except Exception as e:
            logger.error(f"❌ Failed to initialize IDS Service: {e}")
            raise
    
    async def load_ml_model(self):
        """Load the trained IoT IDS model"""
        try:
            model_path = Path(settings.ML_MODEL_PATH)
            if not model_path.exists():
                # Try alternative paths
                alt_paths = [
                    "../IoTCIC/iot_ids_lightgbm_20250819_132715.pkl",
                    "../../IoTCIC/iot_ids_lightgbm_20250819_132715.pkl",
                    "./models/iot_ids_lightgbm.pkl"
                ]
                
                for alt_path in alt_paths:
                    if Path(alt_path).exists():
                        model_path = Path(alt_path)
                        break
                else:
                    raise FileNotFoundError(f"Model file not found at {settings.ML_MODEL_PATH}")
            
            with open(model_path, 'rb') as f:
                self.model_pipeline = pickle.load(f)
            
            # Extract components
            self.model = self.model_pipeline.get('model')
            self.scaler = self.model_pipeline.get('scaler')
            self.label_encoder = self.model_pipeline.get('label_encoder')
            self.feature_names = self.model_pipeline.get('feature_names', [])
            
            logger.info(f"✅ ML Model loaded from {model_path}")
            logger.info(f"Model type: {self.model_pipeline.get('model_type', 'Unknown')}")
            logger.info(f"Features: {len(self.feature_names)}")
            
            if self.label_encoder:
                logger.info(f"Classes: {list(self.label_encoder.classes_)}")
            
        except Exception as e:
            logger.error(f"❌ Error loading ML model: {e}")
            raise
    
    async def predict_attack(self, network_features: Dict[str, Any]) -> ThreatAlert:
        """Predict if network traffic is malicious"""
        if not self.is_initialized or not self.model:
            raise RuntimeError("IDS Service not initialized")
        
        try:
            # Convert features to DataFrame
            if isinstance(network_features, dict):
                # Ensure all required features are present
                feature_data = {}
                for feature in self.feature_names:
                    feature_data[feature] = network_features.get(feature, 0.0)
                
                df = pd.DataFrame([feature_data])
            else:
                df = pd.DataFrame([network_features], columns=self.feature_names)
            
            # Scale features
            scaled_features = self.scaler.transform(df)
            
            # Make prediction
            prediction = self.model.predict(scaled_features)[0]
            prediction_proba = self.model.predict_proba(scaled_features)[0]
            
            # Get class name and confidence
            class_name = self.label_encoder.inverse_transform([prediction])[0]
            confidence = max(prediction_proba)
            
            # Determine threat level
            threat_level = self._get_threat_level(class_name, confidence)
            
            # Create threat alert
            alert = ThreatAlert(
                id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                source_ip=network_features.get('source_ip', '0.0.0.0'),
                destination_ip=network_features.get('destination_ip', '0.0.0.0'),
                attack_type=AttackType(class_name) if class_name != 'Benign' else AttackType.BENIGN,
                threat_level=ThreatLevel(threat_level),
                confidence=confidence,
                description=f"Detected {class_name} with {confidence:.2%} confidence",
                blocked=False,  # Manual blocking only - no auto-blocking
                raw_data=network_features
            )
            
            # Store alert if malicious
            if class_name != 'Benign':
                self.recent_alerts.append(alert)
                self.recent_alerts = self.recent_alerts[-100:]  # Keep last 100 alerts
                
                # Update stats
                self.attack_stats["total_attacks"] += 1
                if alert.blocked:
                    self.attack_stats["blocked_attacks"] += 1
                
                self.attack_stats["attack_types"][class_name] = \
                    self.attack_stats["attack_types"].get(class_name, 0) + 1
            
            return alert
            
        except Exception as e:
            logger.error(f"Error predicting attack: {e}")
            raise
    
    def _get_threat_level(self, class_name: str, confidence: float) -> str:
        """Determine threat level based on attack type and confidence"""
        if class_name == 'Benign':
            return 'LOW'
        
        # Define threat levels based on attack taxonomy
        threat_mapping = {
            'Flood Attacks': 'HIGH',
            'Botnet/Mirai Attacks': 'HIGH',
            'Backdoors & Exploits': 'CRITICAL',
            'Injection Attacks': 'HIGH',
            'Spoofing / MITM': 'MEDIUM',
            'Reconnaissance': 'LOW'
        }
        
        base_level = threat_mapping.get(class_name, 'MEDIUM')
        
        # Adjust based on confidence
        if confidence < 0.7:
            level_downgrade = {
                'CRITICAL': 'HIGH',
                'HIGH': 'MEDIUM',
                'MEDIUM': 'LOW',
                'LOW': 'LOW'
            }
            return level_downgrade.get(base_level, 'LOW')
        
        return base_level
    
    async def start_scan(self, scan_request) -> str:
        """Start a network security scan"""
        scan_id = str(uuid.uuid4())
        
        scan_status = ScanStatus(
            scan_id=scan_id,
            status="running",
            progress=0.0,
            started_at=datetime.utcnow()
        )
        
        self.active_scans[scan_id] = scan_status
        
        # Start scan in background
        asyncio.create_task(self._perform_scan(scan_id, scan_request))
        
        return scan_id
    
    async def _perform_scan(self, scan_id: str, scan_request):
        """Perform the actual network scan"""
        try:
            scan_status = self.active_scans[scan_id]
            
            # Simulate network scanning process
            results = {
                "target": scan_request.target,
                "open_ports": [],
                "services": [],
                "vulnerabilities": [],
                "os_detection": None
            }
            
            # Update progress
            for progress in range(0, 101, 10):
                scan_status.progress = progress
                await asyncio.sleep(0.5)  # Simulate scan time
                
                if progress == 30:
                    results["open_ports"] = [22, 80, 443, 8080]
                elif progress == 60:
                    results["services"] = [
                        {"port": 22, "service": "ssh", "version": "OpenSSH 8.0"},
                        {"port": 80, "service": "http", "version": "nginx 1.18"},
                        {"port": 443, "service": "https", "version": "nginx 1.18"}
                    ]
                elif progress == 90:
                    results["os_detection"] = "Linux 5.4"
            
            # Complete scan
            scan_status.status = "completed"
            scan_status.results = results
            scan_status.completed_at = datetime.utcnow()
            
        except Exception as e:
            scan_status.status = "failed"
            scan_status.error = str(e)
            logger.error(f"Scan {scan_id} failed: {e}")
    
    async def get_scan_status(self, scan_id: str) -> ScanStatus:
        """Get scan status"""
        if scan_id not in self.active_scans:
            raise ValueError(f"Scan {scan_id} not found")
        
        return self.active_scans[scan_id]
    
    async def get_recent_alerts(self, limit: int = 10) -> List[ThreatAlert]:
        """Get recent threat alerts"""
        return self.recent_alerts[-limit:]
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get IDS statistics"""
        return {
            "total_attacks": self.attack_stats["total_attacks"],
            "blocked_attacks": self.attack_stats["blocked_attacks"],
            "attack_types": self.attack_stats["attack_types"],
            "detection_rate": len(self.recent_alerts),
            "model_loaded": self.model is not None,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def get_attack_analytics(self, hours: int = 24) -> List[AttackData]:
        """Get attack analytics data"""
        # Generate sample analytics data
        analytics = []
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        for i in range(hours):
            timestamp = start_time + timedelta(hours=i)
            
            # Simulate attack data
            attack_data = AttackData(
                timestamp=timestamp,
                attack_type=AttackType.FLOOD_ATTACK,
                count=np.random.randint(0, 50),
                blocked_count=np.random.randint(0, 30),
                source_countries={"US": 10, "CN": 8, "RU": 5},
                target_ports={"80": 15, "443": 12, "22": 8}
            )
            analytics.append(attack_data)
        
        return analytics
    
    async def get_model_status(self) -> str:
        """Get ML model status"""
        if not self.model:
            return "not_loaded"
        return "loaded"
    
    async def update_config(self, config):
        """Update IDS configuration"""
        # Update configuration settings
        if hasattr(config, 'confidence_threshold'):
            settings.MODEL_CONFIDENCE_THRESHOLD = config.confidence_threshold
        
        logger.info("IDS configuration updated")
    
    async def block_threat(self, threat_id: str) -> bool:
        """Manually block a threat by ID"""
        try:
            # Find the threat in recent alerts
            for alert in self.recent_alerts:
                if alert.id == threat_id:
                    alert.blocked = True
                    self.attack_stats["blocked_attacks"] += 1
                    logger.info(f"Threat {threat_id} manually blocked")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error blocking threat {threat_id}: {e}")
            return False
    
    async def unblock_threat(self, threat_id: str) -> bool:
        """Manually unblock a threat by ID"""
        try:
            # Find the threat in recent alerts
            for alert in self.recent_alerts:
                if alert.id == threat_id:
                    if alert.blocked:
                        alert.blocked = False
                        self.attack_stats["blocked_attacks"] -= 1
                        logger.info(f"Threat {threat_id} manually unblocked")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error unblocking threat {threat_id}: {e}")
            return False
    
    async def get_threat_details(self, threat_id: str) -> Dict[str, Any]:
        """Get detailed threat information and security recommendations"""
        try:
            # Find the threat in recent alerts
            for alert in self.recent_alerts:
                if alert.id == threat_id:
                    # Generate detailed analysis and recommendations
                    recommendations = self._generate_security_recommendations(alert)
                    
                    return {
                        "threat_info": {
                            "id": alert.id,
                            "timestamp": alert.timestamp.isoformat(),
                            "source_ip": alert.source_ip,
                            "destination_ip": alert.destination_ip,
                            "attack_type": alert.attack_type.value,
                            "threat_level": alert.threat_level.value,
                            "confidence": alert.confidence,
                            "description": alert.description,
                            "blocked": alert.blocked
                        },
                        "packet_analysis": {
                            "protocol": {1: 'ICMP', 6: 'TCP', 17: 'UDP'}.get(alert.raw_data.get('protocol', 0), 'Unknown'),
                            "packet_size": alert.raw_data.get('packet_size', 0),
                            "ttl": alert.raw_data.get('ttl', 0),
                            "source_port": alert.raw_data.get('source_port'),
                            "destination_port": alert.raw_data.get('destination_port'),
                            "tcp_flags": alert.raw_data.get('tcp_flags'),
                            "window_size": alert.raw_data.get('window_size'),
                            "icmp_type": alert.raw_data.get('icmp_type'),
                            "icmp_code": alert.raw_data.get('icmp_code')
                        },
                        "risk_assessment": {
                            "severity": alert.threat_level.value,
                            "confidence_score": alert.confidence,
                            "potential_impact": self._assess_potential_impact(alert),
                            "attack_vector": self._identify_attack_vector(alert)
                        },
                        "recommendations": recommendations,
                        "mitigation_steps": self._generate_mitigation_steps(alert)
                    }
            return None
        except Exception as e:
            logger.error(f"Error getting threat details for {threat_id}: {e}")
            return None
    
    def _generate_security_recommendations(self, alert: ThreatAlert) -> List[str]:
        """Generate security recommendations based on attack type"""
        attack_type = alert.attack_type.value
        recommendations = []
        
        if attack_type == "Flood Attacks":
            recommendations.extend([
                "Implement rate limiting on network interfaces",
                "Configure DDoS protection mechanisms",
                "Set up traffic shaping policies",
                "Monitor bandwidth usage patterns",
                "Consider using a CDN or DDoS mitigation service"
            ])
        elif attack_type == "Botnet/Mirai Attacks":
            recommendations.extend([
                "Immediately isolate affected devices",
                "Change default credentials on IoT devices",
                "Update firmware on all network devices",
                "Implement network segmentation",
                "Monitor for C&C communication patterns"
            ])
        elif attack_type == "Backdoors & Exploits":
            recommendations.extend([
                "Perform immediate system integrity check",
                "Scan for unauthorized access points",
                "Review system logs for suspicious activities",
                "Apply latest security patches",
                "Implement application whitelisting"
            ])
        elif attack_type == "Injection Attacks":
            recommendations.extend([
                "Validate and sanitize all input data",
                "Implement parameterized queries",
                "Use web application firewalls",
                "Regular security code reviews",
                "Apply principle of least privilege"
            ])
        elif attack_type == "Reconnaissance":
            recommendations.extend([
                "Implement network monitoring and logging",
                "Configure intrusion detection systems",
                "Limit information disclosure",
                "Use network segmentation",
                "Monitor for port scanning activities"
            ])
        elif attack_type == "Spoofing / MITM":
            recommendations.extend([
                "Implement strong authentication mechanisms",
                "Use encrypted communication protocols",
                "Deploy certificate pinning",
                "Monitor for ARP spoofing",
                "Implement network access control"
            ])
        
        # General recommendations
        recommendations.extend([
            "Update security policies and procedures",
            "Conduct security awareness training",
            "Regular security assessments",
            "Implement continuous monitoring"
        ])
        
        return recommendations
    
    def _assess_potential_impact(self, alert: ThreatAlert) -> str:
        """Assess potential impact of the threat"""
        if alert.threat_level.value == "CRITICAL":
            return "High - Potential for system compromise, data breach, or service disruption"
        elif alert.threat_level.value == "HIGH":
            return "Medium-High - May lead to unauthorized access or data exposure"
        elif alert.threat_level.value == "MEDIUM":
            return "Medium - Could affect system performance or availability"
        else:
            return "Low - Minimal impact on system security"
    
    def _identify_attack_vector(self, alert: ThreatAlert) -> str:
        """Identify the attack vector"""
        protocol = {1: 'ICMP', 6: 'TCP', 17: 'UDP'}.get(alert.raw_data.get('protocol', 0), 'Unknown')
        port = alert.raw_data.get('destination_port')
        
        if port:
            common_ports = {
                22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
                80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS",
                993: "IMAPS", 995: "POP3S", 3389: "RDP"
            }
            service = common_ports.get(port, f"Port {port}")
            return f"{protocol} traffic targeting {service}"
        else:
            return f"{protocol} network traffic"
    
    def _generate_mitigation_steps(self, alert: ThreatAlert) -> List[str]:
        """Generate immediate mitigation steps"""
        steps = [
            "1. Analyze the threat details and assess immediate risk",
            "2. Document the incident for compliance and analysis",
            "3. Check for similar patterns in network traffic",
            "4. Review firewall and security policies"
        ]
        
        if alert.confidence > 0.8:
            steps.insert(1, "2. Consider blocking the source IP address")
            steps.insert(2, "3. Notify security team immediately")
        
        if alert.threat_level.value in ["CRITICAL", "HIGH"]:
            steps.insert(0, "0. URGENT: Isolate affected systems if possible")
        
        return steps
    
    async def _generate_sample_threats(self):
        """Generate sample threats for testing the dashboard"""
        try:
            from datetime import datetime, timedelta
            import uuid
            import random
            
            logger.info("🧪 Generating sample threats for testing...")
            
            # Sample threat scenarios - using string values
            sample_scenarios = [
                {
                    "source_ip": "192.168.1.100",
                    "destination_ip": "192.168.1.1",
                    "attack_type": "Flood Attacks",
                    "threat_level": "HIGH",
                    "confidence": 0.92,
                    "description": "High-volume flood attack detected from internal network"
                },
                {
                    "source_ip": "10.0.0.55",
                    "destination_ip": "192.168.1.10",
                    "attack_type": "Botnet/Mirai Attacks",
                    "threat_level": "CRITICAL",
                    "confidence": 0.98,
                    "description": "Mirai botnet activity detected - IoT device compromise attempt"
                },
                {
                    "source_ip": "203.0.113.42",
                    "destination_ip": "192.168.1.50",
                    "attack_type": "Injection Attacks",
                    "threat_level": "HIGH",
                    "confidence": 0.87,
                    "description": "SQL injection attempt detected on web application"
                },
                {
                    "source_ip": "198.51.100.15",
                    "destination_ip": "192.168.1.1",
                    "attack_type": "Reconnaissance",
                    "threat_level": "MEDIUM",
                    "confidence": 0.75,
                    "description": "Port scanning activity detected from external source"
                },
                {
                    "source_ip": "172.16.0.99",
                    "destination_ip": "192.168.1.25",
                    "attack_type": "Spoofing / MITM",
                    "threat_level": "HIGH",
                    "confidence": 0.89,
                    "description": "ARP spoofing attack detected - potential man-in-the-middle"
                }
            ]
            
            for i, scenario in enumerate(sample_scenarios):
                # Create raw packet data
                raw_data = {
                    "protocol": 6,  # TCP
                    "packet_size": random.randint(64, 2048),
                    "ttl": random.randint(32, 128),
                    "source_port": random.randint(1024, 65535),
                    "destination_port": random.choice([22, 23, 80, 443, 3389]),
                    "tcp_flags": random.randint(1, 255),
                    "window_size": random.randint(1024, 65535)
                }
                
                # Create threat alert with proper enum conversion
                attack_type_enum = AttackType(scenario["attack_type"])
                threat_level_enum = ThreatLevel(scenario["threat_level"])
                
                threat_alert = ThreatAlert(
                    id=str(uuid.uuid4()),
                    timestamp=datetime.utcnow() - timedelta(minutes=i*5),
                    source_ip=scenario["source_ip"],
                    destination_ip=scenario["destination_ip"],
                    attack_type=attack_type_enum,
                    threat_level=threat_level_enum,
                    confidence=scenario["confidence"],
                    description=scenario["description"],
                    blocked=False,
                    raw_data=raw_data
                )
                
                # Add to recent alerts
                self.recent_alerts.append(threat_alert)
                self.attack_stats["total_attacks"] += 1
                self.attack_stats["attack_types"][attack_type_enum.value] += 1
                
                logger.info(f"  📡 Generated sample threat: {attack_type_enum.value} from {scenario['source_ip']}")
            
            logger.info(f"✅ Generated {len(sample_scenarios)} sample threats for testing")
            
        except Exception as e:
            logger.error(f"❌ Error generating sample threats: {e}")
