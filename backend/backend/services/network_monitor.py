"""
Network Monitoring Service
Real-time packet capture and analysis
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import deque, defaultdict
import json
import socket
import struct
import threading
import time
import random
import asyncio

# Try to import scapy, fallback to mock if not available
try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP, get_if_list
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Scapy not available, using mock network monitoring")

from models.schemas import NetworkDevice, NetworkTopology, TrafficData, ThreatAlert, AttackType, ThreatLevel
from core.config import settings
from services.kali_attack_detector import KaliAttackDetector
from services.database_service import database_service
from utils.network_utils import is_local_network_ip, is_internal_attack

logger = logging.getLogger(__name__)

class NetworkMonitor:
    """Real-time network monitoring service"""
    
    def __init__(self, ids_service=None, websocket_manager=None):
        self.is_monitoring = False
        self.packet_buffer = deque(maxlen=settings.PACKET_CAPTURE_BUFFER_SIZE)
        self.devices = {}
        self.traffic_stats = defaultdict(int)
        self.monitoring_thread = None
        self.interfaces = []
        self.current_interface = settings.DEFAULT_NETWORK_INTERFACE
        self.ids_service = ids_service
        self.websocket_manager = websocket_manager
        self.event_loop = None
        self.kali_detector = KaliAttackDetector()
        
        # PCAP capture enhancement
        self.pcap_buffer = {}  # Store raw packet data for threats
        self.active_captures = {}  # Track ongoing attack captures
        self.pcap_window_seconds = 30  # Capture window for each threat
        
    async def start(self):
        """Start network monitoring"""
        try:
            await self.initialize_interfaces()
            self.is_monitoring = True
            self.event_loop = asyncio.get_event_loop()  # Store the main event loop
            
            if SCAPY_AVAILABLE:
                # Start packet capture in background thread
                self.monitoring_thread = threading.Thread(
                    target=self._start_packet_capture,
                    daemon=True
                )
                self.monitoring_thread.start()
                logger.info(f"✅ Network monitoring started on interface: {self.current_interface}")
            else:
                # Start mock monitoring
                asyncio.create_task(self._mock_monitoring())
                logger.info("✅ Mock network monitoring started (Scapy not available)")
                
        except Exception as e:
            logger.error(f"❌ Failed to start network monitoring: {e}")
            raise
    
    async def stop(self):
        """Stop network monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            # Note: Scapy sniff() doesn't have a clean stop mechanism
            # In production, you'd want to implement proper thread termination
            pass
        logger.info("⏹️ Network monitoring stopped")
    
    async def initialize_interfaces(self):
        """Initialize network interfaces"""
        try:
            if SCAPY_AVAILABLE:
                self.interfaces = get_if_list()
            else:
                # Mock interfaces
                self.interfaces = ["eth0", "lo", "wlan0"]
            
            logger.info(f"Available network interfaces: {self.interfaces}")
            
            # Validate current interface
            if self.current_interface not in self.interfaces and self.interfaces:
                self.current_interface = self.interfaces[0]
                logger.info(f"Using interface: {self.current_interface}")
                
        except Exception as e:
            logger.error(f"Error initializing interfaces: {e}")
            self.interfaces = ["eth0"]  # Fallback
    
    def _start_packet_capture(self):
        """Start packet capture using Scapy"""
        try:
            sniff(
                iface=self.current_interface,
                prn=self._process_packet,
                stop_filter=lambda x: not self.is_monitoring,
                store=False
            )
        except Exception as e:
            logger.error(f"Packet capture error: {e}")
            if "Operation not permitted" in str(e):
                logger.warning("⚠️  Packet capture requires root privileges or proper capabilities")
                logger.info("💡 To enable real packet capture, run with:")
                logger.info("   sudo python -m uvicorn main:app --host 0.0.0.0 --port 8001")
                logger.info("   OR set capabilities: sudo setcap cap_net_raw+ep $(which python3)")
                logger.info("🧪 For now, using sample threats for testing")
            # Continue without packet capture for now
            pass
    
    def _process_packet(self, packet):
        """Process captured packet"""
        try:
            logger.info(f"📦 Packet captured: {packet.summary()}")
            if IP in packet:
                packet_info = self._extract_packet_features(packet)
                self.packet_buffer.append(packet_info)
                self._update_device_info(packet_info)
                self._update_traffic_stats(packet_info)
                logger.info(f"✅ Packet processed: {packet_info['source_ip']} -> {packet_info['destination_ip']}")
                
                # Store raw packet data for potential PCAP capture
                packet_key = f"{packet_info['source_ip']}_{packet_info['destination_ip']}"
                if packet_key not in self.pcap_buffer:
                    self.pcap_buffer[packet_key] = []
                
                # Store raw packet bytes with timestamp
                raw_packet_data = {
                    'timestamp': datetime.now(),
                    'raw_bytes': bytes(packet),
                    'packet_info': packet_info
                }
                self.pcap_buffer[packet_key].append(raw_packet_data)
                
                # Limit buffer size per connection (keep last 100 packets)
                if len(self.pcap_buffer[packet_key]) > 100:
                    self.pcap_buffer[packet_key] = self.pcap_buffer[packet_key][-100:]
                
                # Real-time attack detection
                if self.ids_service and self.ids_service.is_initialized and self.event_loop:
                    # Schedule the async task in the main event loop
                    asyncio.run_coroutine_threadsafe(
                        self._analyze_packet_for_threats(packet_info, packet),
                        self.event_loop
                    )
                
                # Kali attack detection (signature-based)
                kali_attack = self.kali_detector.analyze_packet(packet_info)
                if kali_attack and self.event_loop:
                    asyncio.run_coroutine_threadsafe(
                        self._send_kali_attack_alert(kali_attack),
                        self.event_loop
                    )
                
        except Exception as e:
            logger.error(f"Error processing packet: {e}")
    
    async def _analyze_packet_for_threats(self, packet_info, raw_packet=None):
        """Analyze packet for potential threats using ML model"""
        try:
            # Check if we should filter for local network only
            if settings.LOCAL_NETWORK_ONLY:
                source_ip = packet_info.get('source_ip', '')
                dest_ip = packet_info.get('destination_ip', '')
                
                # Skip if neither source nor destination is in local network
                if not (is_local_network_ip(source_ip, settings.LOCAL_NETWORK_SUBNET) or 
                       is_local_network_ip(dest_ip, settings.LOCAL_NETWORK_SUBNET)):
                    return
                    
                # If monitoring internal attacks only, skip external traffic
                if settings.MONITOR_INTERNAL_ATTACKS and not is_internal_attack(source_ip, dest_ip, settings.LOCAL_NETWORK_SUBNET):
                    # Allow attacks FROM local network (like Kali) to external targets
                    if not is_local_network_ip(source_ip, settings.LOCAL_NETWORK_SUBNET):
                        return
            
            # Call IDS service for threat detection
            threat_alert = await self.ids_service.predict_attack(packet_info)
            
            # If threat detected, send real-time alert
            if threat_alert.attack_type.value != 'BENIGN' and threat_alert.confidence > 0.7:
                # Add local network indicator
                is_local_source = is_local_network_ip(threat_alert.source_ip, settings.LOCAL_NETWORK_SUBNET)
                is_local_dest = is_local_network_ip(threat_alert.destination_ip, settings.LOCAL_NETWORK_SUBNET)
                
                local_indicator = ""
                if is_local_source and is_local_dest:
                    local_indicator = "🏠 INTERNAL ATTACK "
                elif is_local_source:
                    local_indicator = "🏠 LOCAL SOURCE "
                elif is_local_dest:
                    local_indicator = "🏠 LOCAL TARGET "
                
                logger.warning(f"🚨 {local_indicator}THREAT DETECTED: {threat_alert.attack_type.value} from {threat_alert.source_ip} -> {threat_alert.destination_ip} (Confidence: {threat_alert.confidence:.2%})")
                
                # Send real-time alert via WebSocket
                if self.websocket_manager:
                    alert_data = {
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
                            "blocked": threat_alert.blocked
                        }
                    }
                    await self.websocket_manager.broadcast_json(alert_data)
                
                # 💾 SAVE THREAT TO DATABASE WITH PCAP DATA
                try:
                    # Generate PCAP data for this threat
                    pcap_data = await self._generate_pcap_for_threat(
                        threat_alert.source_ip, 
                        threat_alert.destination_ip,
                        threat_alert.id
                    )
                    
                    # Save threat alert to database with PCAP
                    success = await database_service.save_threat_alert(threat_alert, pcap_data)
                    if success:
                        logger.info(f"💾 ✅ Threat {threat_alert.id} saved to database with PCAP data")
                    else:
                        logger.error(f"💾 ❌ Failed to save threat {threat_alert.id} to database")
                        
                except Exception as db_error:
                    logger.error(f"💾 Database save error: {db_error}")
                    
        except Exception as e:
            logger.error(f"Error analyzing packet for threats: {e}")
    
    async def _send_kali_attack_alert(self, kali_attack: Dict[str, Any]):
        """Send Kali attack alert via WebSocket"""
        try:
            logger.warning(f"🎯 KALI ATTACK ALERT: {kali_attack['description']} from {kali_attack['source_ip']}")
            
            # Send real-time alert via WebSocket
            if self.websocket_manager:
                alert_data = {
                    "type": "kali_attack_alert",
                    "data": kali_attack
                }
                await self.websocket_manager.broadcast_json(alert_data)
                
        except Exception as e:
            logger.error(f"Error sending Kali attack alert: {e}")
    
    async def _generate_pcap_for_threat(self, source_ip: str, dest_ip: str, threat_id: str) -> bytes:
        """Generate PCAP data for a detected threat"""
        try:
            # Import required libraries for PCAP generation
            try:
                from scapy.all import wrpcap, PcapWriter
                import io
            except ImportError:
                logger.warning("Scapy not available for PCAP generation")
                return None
            
            # Find relevant packets in buffer
            packet_key1 = f"{source_ip}_{dest_ip}"
            packet_key2 = f"{dest_ip}_{source_ip}"  # Bidirectional traffic
            
            relevant_packets = []
            
            # Collect packets from both directions
            for key in [packet_key1, packet_key2]:
                if key in self.pcap_buffer:
                    # Get packets from last 30 seconds
                    cutoff_time = datetime.now() - timedelta(seconds=self.pcap_window_seconds)
                    recent_packets = [
                        pkt for pkt in self.pcap_buffer[key] 
                        if pkt['timestamp'] >= cutoff_time
                    ]
                    relevant_packets.extend(recent_packets)
            
            if not relevant_packets:
                logger.warning(f"No packets found for threat {threat_id}")
                return None
            
            # Sort packets by timestamp
            relevant_packets.sort(key=lambda x: x['timestamp'])
            
            # Create PCAP data in memory
            pcap_buffer = io.BytesIO()
            
            # Write PCAP header and packets
            try:
                # Create a temporary file-like object for scapy
                temp_packets = []
                for pkt_data in relevant_packets:
                    try:
                        # Reconstruct packet from raw bytes
                        from scapy.all import Ether
                        packet = Ether(pkt_data['raw_bytes'])
                        temp_packets.append(packet)
                    except Exception as e:
                        logger.debug(f"Could not reconstruct packet: {e}")
                        continue
                
                if temp_packets:
                    # Write packets to PCAP format
                    wrpcap(pcap_buffer, temp_packets)
                    pcap_data = pcap_buffer.getvalue()
                    
                    logger.info(f"💾 Generated PCAP with {len(temp_packets)} packets for threat {threat_id}")
                    return pcap_data
                else:
                    logger.warning(f"No valid packets to write for threat {threat_id}")
                    return None
                    
            except Exception as e:
                logger.error(f"Error writing PCAP data: {e}")
                return None
            
        except Exception as e:
            logger.error(f"Error generating PCAP for threat: {e}")
            return None
        finally:
            if 'pcap_buffer' in locals():
                pcap_buffer.close()
    
    def _extract_packet_features(self, packet) -> Dict[str, Any]:
        """Extract features from network packet for ML analysis"""
        features = {
            'timestamp': datetime.utcnow().isoformat(),
            'source_ip': packet[IP].src,
            'destination_ip': packet[IP].dst,
            'protocol': packet[IP].proto,
            'packet_size': len(packet),
            'ttl': packet[IP].ttl,
        }
        
        # TCP specific features
        if TCP in packet:
            tcp_layer = packet[TCP]
            features.update({
                'source_port': tcp_layer.sport,
                'destination_port': tcp_layer.dport,
                'tcp_flags': int(tcp_layer.flags),
                'window_size': tcp_layer.window,
                'fin_flag': 1 if tcp_layer.flags.F else 0,
                'syn_flag': 1 if tcp_layer.flags.S else 0,
                'rst_flag': 1 if tcp_layer.flags.R else 0,
                'psh_flag': 1 if tcp_layer.flags.P else 0,
                'ack_flag': 1 if tcp_layer.flags.A else 0,
                'urg_flag': 1 if tcp_layer.flags.U else 0,
            })
        
        # UDP specific features
        elif UDP in packet:
            udp_layer = packet[UDP]
            features.update({
                'source_port': udp_layer.sport,
                'destination_port': udp_layer.dport,
                'udp_length': udp_layer.len,
            })
        
        # ICMP specific features
        elif ICMP in packet:
            icmp_layer = packet[ICMP]
            features.update({
                'icmp_type': icmp_layer.type,
                'icmp_code': icmp_layer.code,
            })
        
        return features
    
    def _update_device_info(self, packet_info: Dict[str, Any]):
        """Update device information"""
        source_ip = packet_info['source_ip']
        dest_ip = packet_info['destination_ip']
        
        # Update source device
        if source_ip not in self.devices:
            self.devices[source_ip] = NetworkDevice(
                id=source_ip,
                ip_address=source_ip,
                device_type="unknown",
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow(),
                risk_score=0.0
            )
        else:
            self.devices[source_ip].last_seen = datetime.utcnow()
        
        # Update destination device
        if dest_ip not in self.devices:
            self.devices[dest_ip] = NetworkDevice(
                id=dest_ip,
                ip_address=dest_ip,
                device_type="unknown",
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow(),
                risk_score=0.0
            )
        else:
            self.devices[dest_ip].last_seen = datetime.utcnow()
    
    def _update_traffic_stats(self, packet_info: Dict[str, Any]):
        """Update traffic statistics"""
        self.traffic_stats['total_packets'] += 1
        self.traffic_stats['total_bytes'] += packet_info.get('packet_size', 0)
        
        protocol = packet_info.get('protocol', 0)
        protocol_name = {1: 'ICMP', 6: 'TCP', 17: 'UDP'}.get(protocol, 'OTHER')
        self.traffic_stats[f'{protocol_name}_packets'] += 1
    
    async def _mock_monitoring(self):
        """Mock network monitoring for testing"""
        import random
        
        while self.is_monitoring:
            # Generate mock packet data
            mock_packet = {
                'timestamp': datetime.utcnow().isoformat(),
                'source_ip': f"192.168.1.{random.randint(1, 254)}",
                'destination_ip': f"10.0.0.{random.randint(1, 254)}",
                'protocol': random.choice([1, 6, 17]),
                'packet_size': random.randint(64, 1500),
                'source_port': random.randint(1024, 65535),
                'destination_port': random.choice([80, 443, 22, 21, 25, 53]),
            }
            
            self.packet_buffer.append(mock_packet)
            self._update_device_info(mock_packet)
            self._update_traffic_stats(mock_packet)
            
            await asyncio.sleep(0.1)  # 10 packets per second
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get network monitoring statistics"""
        return {
            'total_devices': len(self.devices),
            'total_packets': self.traffic_stats.get('total_packets', 0),
            'total_bytes': self.traffic_stats.get('total_bytes', 0),
            'traffic_mbps': self.traffic_stats.get('total_bytes', 0) * 8 / 1024 / 1024,
            'tcp_packets': self.traffic_stats.get('TCP_packets', 0),
            'udp_packets': self.traffic_stats.get('UDP_packets', 0),
            'icmp_packets': self.traffic_stats.get('ICMP_packets', 0),
            'monitoring_status': self.is_monitoring,
            'current_interface': self.current_interface,
            'buffer_size': len(self.packet_buffer)
        }
    
    async def get_topology(self) -> NetworkTopology:
        """Get network topology"""
        devices = list(self.devices.values())
        
        # Generate mock connections
        connections = []
        for i, device in enumerate(devices[:10]):  # Limit for demo
            if i < len(devices) - 1:
                connections.append({
                    'source': device.ip_address,
                    'target': devices[i + 1].ip_address,
                    'connection_count': 1,
                    'last_seen': datetime.utcnow().isoformat()
                })
        
        # Generate mock subnets
        subnets = [
            {
                'network': '192.168.1.0/24',
                'device_count': len([d for d in devices if d.ip_address.startswith('192.168.1.')]),
                'description': 'Internal Network'
            },
            {
                'network': '10.0.0.0/24',
                'device_count': len([d for d in devices if d.ip_address.startswith('10.0.0.')]),
                'description': 'DMZ Network'
            }
        ]
        
        return NetworkTopology(
            devices=devices,
            connections=connections,
            subnets=subnets,
            total_devices=len(devices),
            last_updated=datetime.utcnow()
        )
    
    async def get_traffic_analytics(self, hours: int = 24) -> List[TrafficData]:
        """Get traffic analytics data"""
        analytics = []
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        for i in range(hours):
            timestamp = start_time + timedelta(hours=i)
            
            # Generate sample traffic data
            traffic_data = TrafficData(
                timestamp=timestamp,
                bytes_in=random.randint(1000000, 10000000),  # 1-10 MB
                bytes_out=random.randint(500000, 5000000),   # 0.5-5 MB
                packets_in=random.randint(1000, 10000),
                packets_out=random.randint(500, 5000),
                connections=random.randint(10, 100),
                protocols={
                    'TCP': random.randint(50, 80),
                    'UDP': random.randint(10, 30),
                    'ICMP': random.randint(1, 10)
                }
            )
            analytics.append(traffic_data)
        
        return analytics
    
    async def get_interfaces(self) -> List[str]:
        """Get available network interfaces"""
        return self.interfaces
    
    async def update_config(self, config):
        """Update network monitoring configuration"""
        if hasattr(config, 'interface') and config.interface in self.interfaces:
            self.current_interface = config.interface
            logger.info(f"Network interface updated to: {self.current_interface}")
        
        if hasattr(config, 'buffer_size'):
            self.packet_buffer = deque(maxlen=config.buffer_size)
            logger.info(f"Packet buffer size updated to: {config.buffer_size}")
    
    def get_recent_packets(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent packets for analysis"""
        return list(self.packet_buffer)[-limit:]
