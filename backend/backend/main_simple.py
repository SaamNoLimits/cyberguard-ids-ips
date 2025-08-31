#!/usr/bin/env python3
"""
Simple FastAPI Backend for testing
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Cybersecurity IDS/IPS Platform",
    description="Advanced Intrusion Detection & Prevention System",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Cybersecurity IDS/IPS Platform API", "status": "running"}

@app.get("/api/public/stats")
async def get_public_stats():
    """Get public statistics"""
    return {
        "total_threats": 1234,
        "active_connections": 5,
        "threat_levels": {
            "LOW": 100,
            "MEDIUM": 200,
            "HIGH": 800,
            "CRITICAL": 134
        },
        "attack_types": {
            "Flood Attacks": 800,
            "Botnet/Mirai": 200,
            "Injection": 100,
            "Reconnaissance": 80,
            "Spoofing/MITM": 54
        },
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/public/threats/recent")
async def get_recent_threats(limit: int = 50):
    """Get recent threats"""
    threats = []
    for i in range(min(limit, 10)):
        threats.append({
            "id": f"threat-{i}",
            "timestamp": datetime.now().isoformat(),
            "source_ip": f"192.168.100.{100 + i}",
            "destination_ip": "192.168.100.124",
            "attack_type": "Flood Attacks",
            "threat_level": "HIGH",
            "confidence": 95.5,
            "description": f"Flood attack detected from {i}",
            "blocked": False,
            "raw_data": {}
        })
    return threats

@app.post("/api/public/threats/generate")
async def generate_threat():
    """Generate a test threat"""
    threat = {
        "id": f"generated-{datetime.now().timestamp()}",
        "timestamp": datetime.now().isoformat(),
        "source_ip": "192.168.100.200",
        "destination_ip": "192.168.100.124",
        "attack_type": "Flood Attacks",
        "threat_level": "HIGH",
        "confidence": 100.0,
        "description": "Generated test threat",
        "blocked": False,
        "raw_data": {}
    }
    return threat

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
