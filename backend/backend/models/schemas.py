"""
Pydantic models for API requests and responses
"""

from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

# Authentication Models
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: Optional[datetime] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

# Dashboard Models
class DashboardStats(BaseModel):
    total_devices: int
    active_threats: int
    blocked_attacks: int
    network_traffic: float  # Mbps
    threat_level: str
    uptime_hours: int
    last_updated: datetime

class ThreatLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AttackType(str, Enum):
    FLOOD_ATTACK = "Flood Attacks"
    BOTNET_MIRAI = "Botnet/Mirai Attacks"
    BACKDOOR_EXPLOIT = "Backdoors & Exploits"
    INJECTION_ATTACK = "Injection Attacks"
    RECONNAISSANCE = "Reconnaissance"
    SPOOFING_MITM = "Spoofing / MITM"
    BENIGN = "Benign"

# Threat Alert Models
class ThreatAlert(BaseModel):
    id: str
    timestamp: datetime
    source_ip: str
    destination_ip: str
    attack_type: AttackType
    threat_level: ThreatLevel
    confidence: float = Field(..., ge=0.0, le=1.0)
    description: str
    blocked: bool = False
    raw_data: Optional[Dict[str, Any]] = None

class ThreatIndicator(BaseModel):
    id: str
    type: str  # ip, domain, hash, etc.
    value: str
    threat_level: ThreatLevel
    source: str
    description: str
    first_seen: datetime
    last_seen: datetime
    tags: List[str] = []

# Network Models
class NetworkDevice(BaseModel):
    id: str
    ip_address: str
    mac_address: Optional[str] = None
    hostname: Optional[str] = None
    device_type: str
    vendor: Optional[str] = None
    os: Optional[str] = None
    first_seen: datetime
    last_seen: datetime
    is_trusted: bool = False
    risk_score: float = Field(..., ge=0.0, le=10.0)

class NetworkTopology(BaseModel):
    devices: List[NetworkDevice]
    connections: List[Dict[str, Any]]
    subnets: List[Dict[str, Any]]
    total_devices: int
    last_updated: datetime

class TrafficData(BaseModel):
    timestamp: datetime
    bytes_in: int
    bytes_out: int
    packets_in: int
    packets_out: int
    connections: int
    protocols: Dict[str, int]

class AttackData(BaseModel):
    timestamp: datetime
    attack_type: AttackType
    count: int
    blocked_count: int
    source_countries: Dict[str, int]
    target_ports: Dict[str, int]

# IDS/IPS Models
class ScanRequest(BaseModel):
    target: str = Field(..., description="Target IP, range, or hostname")
    scan_type: str = Field(default="comprehensive", description="Type of scan to perform")
    ports: Optional[str] = Field(None, description="Port range to scan")
    aggressive: bool = Field(default=False, description="Enable aggressive scanning")

class ScanResult(BaseModel):
    scan_id: str
    status: str
    message: str
    started_at: Optional[datetime] = None

class ScanStatus(BaseModel):
    scan_id: str
    status: str  # running, completed, failed
    progress: float = Field(..., ge=0.0, le=100.0)
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

class VulnerabilityResult(BaseModel):
    id: str
    severity: str
    title: str
    description: str
    solution: Optional[str] = None
    cve_id: Optional[str] = None
    cvss_score: Optional[float] = None
    affected_hosts: List[str]

# Blockchain Audit Models
class BlockchainBlock(BaseModel):
    index: int
    timestamp: str
    data: Dict[str, Any]
    previous_hash: str
    hash: str

# System Configuration Models
class NetworkConfig(BaseModel):
    interfaces: List[str]
    promiscuous_mode: bool = False
    packet_buffer_size: int = 1000
    capture_filter: Optional[str] = None

class IDSConfig(BaseModel):
    model_path: str
    confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    auto_block: bool = False
    alert_threshold: int = 5

class ThreatIntelConfig(BaseModel):
    enabled_feeds: List[str]
    update_interval: int = 3600  # seconds
    api_keys: Dict[str, str] = {}

class SystemConfig(BaseModel):
    network_interfaces: List[str]
    ml_model_status: str
    threat_feeds_enabled: List[str]
    blockchain_enabled: bool

class SystemConfigUpdate(BaseModel):
    network_config: Optional[NetworkConfig] = None
    ids_config: Optional[IDSConfig] = None
    threat_intel_config: Optional[ThreatIntelConfig] = None

# Analytics Models
class AttackTrend(BaseModel):
    date: datetime
    attack_count: int
    blocked_count: int
    top_attack_types: Dict[str, int]

class GeolocationData(BaseModel):
    country: str
    country_code: str
    city: Optional[str] = None
    latitude: float
    longitude: float
    attack_count: int

class ProtocolStats(BaseModel):
    protocol: str
    packet_count: int
    byte_count: int
    percentage: float

# Incident Response Models
class IncidentSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class IncidentStatus(str, Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class Incident(BaseModel):
    id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    assigned_to: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    tags: List[str] = []
    related_alerts: List[str] = []

class PlaybookAction(BaseModel):
    id: str
    name: str
    description: str
    command: str
    parameters: Dict[str, Any] = {}
    auto_execute: bool = False

class Playbook(BaseModel):
    id: str
    name: str
    description: str
    trigger_conditions: Dict[str, Any]
    actions: List[PlaybookAction]
    enabled: bool = True

# Compliance Models
class ComplianceFramework(str, Enum):
    NIST = "NIST"
    ISO27001 = "ISO27001"
    SOC2 = "SOC2"
    PCI_DSS = "PCI_DSS"

class ComplianceCheck(BaseModel):
    id: str
    framework: ComplianceFramework
    control_id: str
    title: str
    description: str
    status: str  # compliant, non_compliant, not_applicable
    evidence: Optional[str] = None
    last_checked: datetime

class ComplianceReport(BaseModel):
    framework: ComplianceFramework
    total_controls: int
    compliant_controls: int
    non_compliant_controls: int
    compliance_percentage: float
    checks: List[ComplianceCheck]
    generated_at: datetime

# ML Model Performance
class ModelMetrics(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    confusion_matrix: List[List[int]]
    feature_importance: Dict[str, float]
    last_trained: datetime
    training_samples: int

class ModelPrediction(BaseModel):
    prediction: AttackType
    confidence: float
    feature_values: Dict[str, float]
    timestamp: datetime

# API Response Models
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int
