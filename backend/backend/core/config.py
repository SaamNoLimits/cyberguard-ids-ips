"""
Configuration settings for the cybersecurity platform
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Cybersecurity IDS/IPS Platform"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Advanced Intrusion Detection & Prevention System"
    
    # Security
    SECRET_KEY: str = Field(default="your-super-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"
    
    # Database
    DATABASE_URL: str = Field(default="postgresql://cybersec:password@localhost/cybersec_ids")
    ASYNC_DATABASE_URL: str = Field(default="postgresql+asyncpg://cybersec:password@localhost/cybersec_ids")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://localhost:3000",
        "https://localhost:3001",
    ]
    
    # ML Model Configuration
    ML_MODEL_PATH: str = Field(default="../IoTCIC/iot_ids_lightgbm_20250819_132715.pkl")
    MODEL_CONFIDENCE_THRESHOLD: float = 0.7
    MODEL_UPDATE_INTERVAL: int = 3600  # seconds
    
    # Network Monitoring
    DEFAULT_NETWORK_INTERFACE: str = "wlp0s20f3"
    NETWORK_INTERFACE: str = Field(default="auto")
    CAPTURE_FILTER: str = Field(default="")
    PACKET_CAPTURE_BUFFER_SIZE: int = 1000
    NETWORK_SCAN_TIMEOUT: int = 300  # seconds
    
    # Local Network Filtering
    LOCAL_NETWORK_ONLY: bool = Field(default=False)
    LOCAL_NETWORK_SUBNET: str = Field(default="192.168.100.0/24")
    MONITOR_INTERNAL_ATTACKS: bool = Field(default=True)
    
    # Threat Intelligence
    THREAT_INTEL_UPDATE_INTERVAL: int = 3600  # seconds
    VIRUSTOTAL_API_KEY: Optional[str] = None
    ABUSEIPDB_API_KEY: Optional[str] = None
    OTXALIENVAUL_API_KEY: Optional[str] = None
    
    # Blockchain Audit
    BLOCKCHAIN_ENABLED: bool = True
    BLOCKCHAIN_DIFFICULTY: int = 4
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/cybersec_platform.log"
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS: int = 100
    
    # Background Tasks
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2")
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 9090
    
    # Development
    DEBUG: bool = Field(default=False)
    TESTING: bool = Field(default=False)
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
