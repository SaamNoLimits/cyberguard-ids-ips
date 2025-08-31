"""
Threat Intelligence Service
Integrates with external threat feeds and provides threat analysis
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import hashlib

from models.schemas import ThreatIndicator, ThreatLevel
from core.config import settings

logger = logging.getLogger(__name__)

class ThreatIntelligenceService:
    """Threat Intelligence Service"""
    
    def __init__(self):
        self.threat_indicators = []
        self.threat_feeds = {
            'malicious_ips': [],
            'malicious_domains': [],
            'malware_hashes': []
        }
        self.current_threat_level = ThreatLevel.LOW
        self.last_update = None
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize threat intelligence service"""
        try:
            await self.load_threat_feeds()
            self.is_initialized = True
            
            # Start periodic updates
            asyncio.create_task(self._periodic_update())
            
            logger.info("✅ Threat Intelligence Service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Threat Intelligence Service: {e}")
            raise
    
    async def load_threat_feeds(self):
        """Load threat intelligence feeds"""
        try:
            # Load built-in threat indicators
            await self._load_builtin_indicators()
            
            # Load from external feeds if API keys are available
            if settings.VIRUSTOTAL_API_KEY:
                await self._load_virustotal_feed()
            
            if settings.ABUSEIPDB_API_KEY:
                await self._load_abuseipdb_feed()
            
            self.last_update = datetime.utcnow()
            logger.info(f"Loaded {len(self.threat_indicators)} threat indicators")
            
        except Exception as e:
            logger.error(f"Error loading threat feeds: {e}")
    
    async def _load_builtin_indicators(self):
        """Load built-in threat indicators"""
        # Sample malicious IPs (known botnets, C&C servers)
        malicious_ips = [
            "185.220.100.240", "185.220.100.241", "185.220.100.242",
            "198.98.51.189", "23.129.64.131", "45.142.212.61",
            "89.248.165.74", "94.102.49.190", "185.220.101.182"
        ]
        
        # Sample malicious domains
        malicious_domains = [
            "malware-traffic-analysis.net",
            "suspicious-domain.com",
            "botnet-c2.org",
            "phishing-site.net"
        ]
        
        # Create threat indicators
        for ip in malicious_ips:
            indicator = ThreatIndicator(
                id=hashlib.md5(ip.encode()).hexdigest(),
                type="ip",
                value=ip,
                threat_level=ThreatLevel.HIGH,
                source="builtin",
                description=f"Known malicious IP: {ip}",
                first_seen=datetime.utcnow() - timedelta(days=30),
                last_seen=datetime.utcnow(),
                tags=["malware", "botnet"]
            )
            self.threat_indicators.append(indicator)
        
        for domain in malicious_domains:
            indicator = ThreatIndicator(
                id=hashlib.md5(domain.encode()).hexdigest(),
                type="domain",
                value=domain,
                threat_level=ThreatLevel.MEDIUM,
                source="builtin",
                description=f"Suspicious domain: {domain}",
                first_seen=datetime.utcnow() - timedelta(days=15),
                last_seen=datetime.utcnow(),
                tags=["phishing", "malware"]
            )
            self.threat_indicators.append(indicator)
    
    async def _load_virustotal_feed(self):
        """Load indicators from VirusTotal API"""
        try:
            # This is a placeholder - implement actual VirusTotal API integration
            logger.info("VirusTotal feed integration not implemented yet")
        except Exception as e:
            logger.error(f"Error loading VirusTotal feed: {e}")
    
    async def _load_abuseipdb_feed(self):
        """Load indicators from AbuseIPDB API"""
        try:
            # This is a placeholder - implement actual AbuseIPDB API integration
            logger.info("AbuseIPDB feed integration not implemented yet")
        except Exception as e:
            logger.error(f"Error loading AbuseIPDB feed: {e}")
    
    async def _periodic_update(self):
        """Periodically update threat feeds"""
        while True:
            try:
                await asyncio.sleep(settings.THREAT_INTEL_UPDATE_INTERVAL)
                await self.load_threat_feeds()
                await self._calculate_threat_level()
                logger.info("Threat intelligence feeds updated")
            except Exception as e:
                logger.error(f"Error in periodic threat intel update: {e}")
    
    async def _calculate_threat_level(self):
        """Calculate current threat level based on indicators"""
        high_threats = len([i for i in self.threat_indicators if i.threat_level == ThreatLevel.HIGH])
        critical_threats = len([i for i in self.threat_indicators if i.threat_level == ThreatLevel.CRITICAL])
        
        if critical_threats > 0:
            self.current_threat_level = ThreatLevel.CRITICAL
        elif high_threats > 10:
            self.current_threat_level = ThreatLevel.HIGH
        elif high_threats > 5:
            self.current_threat_level = ThreatLevel.MEDIUM
        else:
            self.current_threat_level = ThreatLevel.LOW
    
    async def check_ip_reputation(self, ip_address: str) -> Optional[ThreatIndicator]:
        """Check IP reputation against threat feeds"""
        for indicator in self.threat_indicators:
            if indicator.type == "ip" and indicator.value == ip_address:
                return indicator
        return None
    
    async def check_domain_reputation(self, domain: str) -> Optional[ThreatIndicator]:
        """Check domain reputation against threat feeds"""
        for indicator in self.threat_indicators:
            if indicator.type == "domain" and indicator.value == domain:
                return indicator
        return None
    
    async def check_hash_reputation(self, file_hash: str) -> Optional[ThreatIndicator]:
        """Check file hash reputation against threat feeds"""
        for indicator in self.threat_indicators:
            if indicator.type == "hash" and indicator.value == file_hash:
                return indicator
        return None
    
    async def add_custom_indicator(self, indicator: ThreatIndicator):
        """Add custom threat indicator"""
        self.threat_indicators.append(indicator)
        logger.info(f"Added custom threat indicator: {indicator.value}")
    
    async def get_indicators(self, limit: int = 100) -> List[ThreatIndicator]:
        """Get threat indicators"""
        return self.threat_indicators[:limit]
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get threat intelligence statistics"""
        stats = {
            "total_indicators": len(self.threat_indicators),
            "ip_indicators": len([i for i in self.threat_indicators if i.type == "ip"]),
            "domain_indicators": len([i for i in self.threat_indicators if i.type == "domain"]),
            "hash_indicators": len([i for i in self.threat_indicators if i.type == "hash"]),
            "high_threat_indicators": len([i for i in self.threat_indicators if i.threat_level == ThreatLevel.HIGH]),
            "critical_threat_indicators": len([i for i in self.threat_indicators if i.threat_level == ThreatLevel.CRITICAL]),
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "current_threat_level": self.current_threat_level.value
        }
        
        # Calculate active threats (indicators seen in last 24 hours)
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        active_threats = len([
            i for i in self.threat_indicators 
            if i.last_seen > recent_cutoff
        ])
        stats["active_threats"] = active_threats
        
        return stats
    
    async def get_current_threat_level(self) -> str:
        """Get current threat level"""
        return self.current_threat_level.value
    
    async def get_feeds_status(self) -> List[str]:
        """Get status of threat feeds"""
        feeds = ["builtin"]
        
        if settings.VIRUSTOTAL_API_KEY:
            feeds.append("virustotal")
        
        if settings.ABUSEIPDB_API_KEY:
            feeds.append("abuseipdb")
        
        return feeds
    
    async def update_config(self, config):
        """Update threat intelligence configuration"""
        if hasattr(config, 'enabled_feeds'):
            logger.info(f"Threat intelligence feeds updated: {config.enabled_feeds}")
        
        if hasattr(config, 'update_interval'):
            settings.THREAT_INTEL_UPDATE_INTERVAL = config.update_interval
            logger.info(f"Update interval changed to: {config.update_interval} seconds")
    
    async def enrich_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich alert with threat intelligence data"""
        enriched = alert_data.copy()
        
        # Check source IP
        if 'source_ip' in alert_data:
            ip_intel = await self.check_ip_reputation(alert_data['source_ip'])
            if ip_intel:
                enriched['source_ip_reputation'] = {
                    'threat_level': ip_intel.threat_level.value,
                    'source': ip_intel.source,
                    'tags': ip_intel.tags,
                    'description': ip_intel.description
                }
        
        # Check destination IP
        if 'destination_ip' in alert_data:
            ip_intel = await self.check_ip_reputation(alert_data['destination_ip'])
            if ip_intel:
                enriched['destination_ip_reputation'] = {
                    'threat_level': ip_intel.threat_level.value,
                    'source': ip_intel.source,
                    'tags': ip_intel.tags,
                    'description': ip_intel.description
                }
        
        return enriched
