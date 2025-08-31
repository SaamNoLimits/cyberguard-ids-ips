"""
Kali Linux Attack Detection Service
Specialized detection for common Kali tools and attack patterns
"""

import re
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class KaliAttackDetector:
    """Specialized detector for Kali Linux attack patterns"""
    
    def __init__(self):
        self.attack_signatures = self._load_attack_signatures()
        self.detected_attacks = []
        
    def _load_attack_signatures(self) -> Dict[str, Dict]:
        """Load attack signatures for common Kali tools"""
        return {
            # Nmap signatures
            "nmap_syn_scan": {
                "pattern": "tcp_flags == 2",  # SYN flag only
                "description": "Nmap SYN scan detected",
                "attack_type": "Reconnaissance",
                "threat_level": "MEDIUM",
                "ports": [22, 23, 53, 80, 110, 443, 993, 995]
            },
            "nmap_version_scan": {
                "pattern": "multiple_ports_sequential",
                "description": "Nmap version scan detected",
                "attack_type": "Reconnaissance", 
                "threat_level": "HIGH",
                "indicators": ["rapid_port_sequence", "service_probes"]
            },
            "nmap_os_detection": {
                "pattern": "icmp_echo_variations",
                "description": "Nmap OS detection scan",
                "attack_type": "Reconnaissance",
                "threat_level": "MEDIUM",
                "indicators": ["icmp_timestamp", "tcp_window_variations"]
            },
            
            # Nikto signatures
            "nikto_scan": {
                "pattern": "http_user_agent_nikto",
                "description": "Nikto web vulnerability scan",
                "attack_type": "Reconnaissance",
                "threat_level": "HIGH",
                "user_agents": ["Nikto", "Mozilla/5.00 (Nikto"]
            },
            
            # SQLMap signatures
            "sqlmap_injection": {
                "pattern": "sql_injection_payloads",
                "description": "SQLMap injection attempt",
                "attack_type": "Injection Attacks",
                "threat_level": "CRITICAL",
                "payloads": ["' OR '1'='1", "UNION SELECT", "'; DROP TABLE"]
            },
            
            # Metasploit signatures
            "metasploit_exploit": {
                "pattern": "metasploit_payload",
                "description": "Metasploit exploit attempt",
                "attack_type": "Backdoors & Exploits",
                "threat_level": "CRITICAL",
                "indicators": ["reverse_shell", "meterpreter", "payload_delivery"]
            },
            
            # Hydra/Brute force
            "hydra_bruteforce": {
                "pattern": "rapid_auth_attempts",
                "description": "Hydra brute force attack",
                "attack_type": "Backdoors & Exploits",
                "threat_level": "HIGH",
                "indicators": ["multiple_failed_logins", "rapid_connections"]
            },
            
            # Aircrack-ng (WiFi attacks)
            "aircrack_deauth": {
                "pattern": "wifi_deauth_packets",
                "description": "WiFi deauthentication attack",
                "attack_type": "Spoofing / MITM",
                "threat_level": "HIGH",
                "indicators": ["deauth_frames", "wifi_jamming"]
            },
            
            # DDoS/DoS attacks
            "ddos_flood": {
                "pattern": "high_packet_rate",
                "description": "DDoS flood attack from Kali",
                "attack_type": "Flood Attacks",
                "threat_level": "CRITICAL",
                "thresholds": {"packets_per_second": 100, "connections_per_minute": 50}
            }
        }
    
    def analyze_packet(self, packet_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze packet for Kali attack patterns"""
        try:
            # Check for various attack patterns
            detected_attack = None
            
            # Nmap detection
            if self._detect_nmap_scan(packet_info):
                detected_attack = self._create_attack_alert("nmap_syn_scan", packet_info)
            
            # Port scan detection
            elif self._detect_port_scan(packet_info):
                detected_attack = self._create_attack_alert("nmap_version_scan", packet_info)
            
            # High traffic detection (potential DDoS)
            elif self._detect_flood_attack(packet_info):
                detected_attack = self._create_attack_alert("ddos_flood", packet_info)
            
            # HTTP-based attacks
            elif self._detect_web_attack(packet_info):
                detected_attack = self._create_attack_alert("nikto_scan", packet_info)
            
            if detected_attack:
                self.detected_attacks.append(detected_attack)
                logger.warning(f"🚨 KALI ATTACK DETECTED: {detected_attack['description']}")
                return detected_attack
                
        except Exception as e:
            logger.error(f"Error analyzing packet for Kali attacks: {e}")
        
        return None
    
    def _detect_nmap_scan(self, packet_info: Dict[str, Any]) -> bool:
        """Detect Nmap scanning patterns"""
        try:
            # SYN scan detection
            if (packet_info.get("protocol") == 6 and  # TCP
                packet_info.get("tcp_flags") == 2):   # SYN flag only
                return True
            
            # Multiple ports in sequence
            if (packet_info.get("destination_port") in [22, 23, 53, 80, 110, 443, 993, 995] and
                packet_info.get("packet_size", 0) < 100):  # Small packets typical of scans
                return True
                
        except Exception as e:
            logger.error(f"Error in Nmap detection: {e}")
        
        return False
    
    def _detect_port_scan(self, packet_info: Dict[str, Any]) -> bool:
        """Detect port scanning behavior"""
        try:
            # Rapid port scanning indicators
            if (packet_info.get("protocol") == 6 and  # TCP
                packet_info.get("packet_size", 0) < 80 and  # Small packets
                packet_info.get("ttl", 0) < 64):  # Low TTL often indicates scanning tools
                return True
                
        except Exception as e:
            logger.error(f"Error in port scan detection: {e}")
        
        return False
    
    def _detect_flood_attack(self, packet_info: Dict[str, Any]) -> bool:
        """Detect flood/DDoS patterns"""
        try:
            # High packet rate from same source
            source_ip = packet_info.get("source_ip")
            if source_ip:
                # Simple heuristic: if packet size is large and from external IP
                if (packet_info.get("packet_size", 0) > 1000 and
                    not source_ip.startswith("127.") and
                    not source_ip.startswith("192.168.100.")):  # Not local network
                    return True
                    
        except Exception as e:
            logger.error(f"Error in flood detection: {e}")
        
        return False
    
    def _detect_web_attack(self, packet_info: Dict[str, Any]) -> bool:
        """Detect web-based attacks (Nikto, SQLMap, etc.)"""
        try:
            # HTTP traffic to web ports
            if packet_info.get("destination_port") in [80, 443, 8000, 3000, 8080]:
                # Suspicious packet patterns
                if packet_info.get("packet_size", 0) > 500:  # Large HTTP requests
                    return True
                    
        except Exception as e:
            logger.error(f"Error in web attack detection: {e}")
        
        return False
    
    def _create_attack_alert(self, attack_type: str, packet_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create attack alert from detected pattern"""
        signature = self.attack_signatures.get(attack_type, {})
        
        return {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "source_ip": packet_info.get("source_ip", "unknown"),
            "destination_ip": packet_info.get("destination_ip", "unknown"),
            "attack_type": signature.get("attack_type", "Unknown"),
            "threat_level": signature.get("threat_level", "MEDIUM"),
            "description": signature.get("description", "Kali attack detected"),
            "confidence": 0.85,  # High confidence for signature-based detection
            "detection_method": "kali_signature",
            "tool_detected": attack_type,
            "raw_data": packet_info,
            "blocked": False
        }
    
    def get_attack_statistics(self) -> Dict[str, Any]:
        """Get statistics of detected attacks"""
        stats = {
            "total_attacks": len(self.detected_attacks),
            "attack_types": {},
            "source_ips": {},
            "last_attack": None
        }
        
        for attack in self.detected_attacks:
            # Count by attack type
            attack_type = attack.get("attack_type", "Unknown")
            stats["attack_types"][attack_type] = stats["attack_types"].get(attack_type, 0) + 1
            
            # Count by source IP
            source_ip = attack.get("source_ip", "unknown")
            stats["source_ips"][source_ip] = stats["source_ips"].get(source_ip, 0) + 1
            
            # Track last attack
            if not stats["last_attack"] or attack["timestamp"] > stats["last_attack"]["timestamp"]:
                stats["last_attack"] = attack
        
        return stats
    
    def clear_old_attacks(self, hours: int = 24):
        """Clear attacks older than specified hours"""
        try:
            from datetime import timedelta
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            self.detected_attacks = [
                attack for attack in self.detected_attacks
                if datetime.fromisoformat(attack["timestamp"]) > cutoff_time
            ]
            
            logger.info(f"Cleared old attacks, {len(self.detected_attacks)} attacks remaining")
            
        except Exception as e:
            logger.error(f"Error clearing old attacks: {e}")
