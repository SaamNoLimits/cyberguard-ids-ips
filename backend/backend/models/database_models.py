"""
Database models for the cybersecurity platform
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

class ThreatAlert(Base):
    __tablename__ = "threat_alerts"
    
    id = Column(String(36), primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    source_ip = Column(String(45), index=True)
    destination_ip = Column(String(45), index=True)
    attack_type = Column(String(50), index=True)
    threat_level = Column(String(20), index=True)
    confidence = Column(Float)
    description = Column(Text)
    blocked = Column(Boolean, default=False)
    raw_data = Column(JSON)
    pcap_file_path = Column(String(500))  # Path to associated PCAP file
    packet_count = Column(Integer, default=0)  # Number of packets in this attack
    duration_seconds = Column(Float, default=0.0)  # Attack duration
    bytes_transferred = Column(Integer, default=0)  # Total bytes in attack
    geolocation_data = Column(JSON)  # GeoIP data for source IP
    threat_intelligence = Column(JSON)  # External threat intel data

class NetworkDevice(Base):
    __tablename__ = "network_devices"
    
    id = Column(String(36), primary_key=True)
    ip_address = Column(String(45), unique=True, index=True)
    mac_address = Column(String(17), index=True)
    hostname = Column(String(255))
    device_type = Column(String(50))
    vendor = Column(String(100))
    os = Column(String(100))
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    is_trusted = Column(Boolean, default=False)
    risk_score = Column(Float, default=0.0)

class PcapFile(Base):
    __tablename__ = "pcap_files"
    
    id = Column(String(36), primary_key=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)  # Size in bytes
    packet_count = Column(Integer)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration_seconds = Column(Float)
    interface_name = Column(String(50))
    capture_filter = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    threat_alert_ids = Column(JSON)  # List of associated threat alert IDs
    file_hash = Column(String(64))  # SHA256 hash for integrity
    compressed = Column(Boolean, default=False)
    compressed_path = Column(String(500))

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    event_type = Column(String(50), index=True)
    user_id = Column(Integer, index=True)
    description = Column(Text)
    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
