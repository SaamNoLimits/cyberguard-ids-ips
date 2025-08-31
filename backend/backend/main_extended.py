#!/usr/bin/env python3
"""
Extended FastAPI Backend with Database Support
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import logging
import subprocess
import tempfile
import os
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

@app.get("/api/database/threats/recent")
async def get_database_threats(limit: int = 50):
    """Get recent threats from database"""
    # Same as public endpoint for now
    return await get_recent_threats(limit)

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

@app.get("/api/database/tables")
async def get_database_tables():
    """Get all database tables and their info"""
    # Mock database tables
    return [
        {
            "tablename": "threats",
            "row_count": 1234,
            "size": "256 kB",
            "tableowner": "cybersec",
            "hasindexes": True,
            "hasrules": False,
            "hastriggers": False
        },
        {
            "tablename": "query_history",
            "row_count": 45,
            "size": "32 kB",
            "tableowner": "cybersec",
            "hasindexes": True,
            "hasrules": False,
            "hastriggers": False
        }
    ]

@app.get("/api/database/table/{table_name}/columns")
async def get_table_columns(table_name: str):
    """Get columns info for a specific table"""
    if table_name == "threats":
        return [
            {"column_name": "id", "data_type": "integer", "is_nullable": "NO", "column_default": "nextval('threats_id_seq'::regclass)", "character_maximum_length": None},
            {"column_name": "timestamp", "data_type": "timestamp without time zone", "is_nullable": "YES", "column_default": "CURRENT_TIMESTAMP", "character_maximum_length": None},
            {"column_name": "source_ip", "data_type": "character varying", "is_nullable": "YES", "column_default": None, "character_maximum_length": 45},
            {"column_name": "dest_ip", "data_type": "character varying", "is_nullable": "YES", "column_default": None, "character_maximum_length": 45},
            {"column_name": "attack_type", "data_type": "character varying", "is_nullable": "YES", "column_default": None, "character_maximum_length": 100},
            {"column_name": "threat_level", "data_type": "character varying", "is_nullable": "YES", "column_default": None, "character_maximum_length": 20},
            {"column_name": "confidence", "data_type": "double precision", "is_nullable": "YES", "column_default": None, "character_maximum_length": None},
            {"column_name": "description", "data_type": "text", "is_nullable": "YES", "column_default": None, "character_maximum_length": None}
        ]
    elif table_name == "query_history":
        return [
            {"column_name": "id", "data_type": "integer", "is_nullable": "NO", "column_default": "nextval('query_history_id_seq'::regclass)", "character_maximum_length": None},
            {"column_name": "timestamp", "data_type": "timestamp without time zone", "is_nullable": "YES", "column_default": "CURRENT_TIMESTAMP", "character_maximum_length": None},
            {"column_name": "query_type", "data_type": "character varying", "is_nullable": "YES", "column_default": None, "character_maximum_length": 20},
            {"column_name": "query_text", "data_type": "text", "is_nullable": "YES", "column_default": None, "character_maximum_length": None},
            {"column_name": "result", "data_type": "text", "is_nullable": "YES", "column_default": None, "character_maximum_length": None},
            {"column_name": "execution_time", "data_type": "double precision", "is_nullable": "YES", "column_default": None, "character_maximum_length": None},
            {"column_name": "success", "data_type": "boolean", "is_nullable": "YES", "column_default": None, "character_maximum_length": None}
        ]
    return []

@app.get("/api/database/table/{table_name}/data")
async def get_table_data(table_name: str, limit: int = 100, offset: int = 0):
    """Get data from a specific table"""
    if table_name == "threats":
        data = []
        for i in range(min(limit, 10)):
            data.append({
                "id": i + 1,
                "timestamp": datetime.now().isoformat(),
                "source_ip": f"192.168.100.{100 + i}",
                "dest_ip": "192.168.100.124",
                "attack_type": "Flood Attacks" if i % 2 == 0 else "Port Scan",
                "threat_level": "HIGH" if i % 3 == 0 else "MEDIUM",
                "confidence": 95.5 - i,
                "description": f"Threat detected from source {i}"
            })
        return data
    elif table_name == "query_history":
        return [
            {
                "id": 1,
                "timestamp": datetime.now().isoformat(),
                "query_type": "SQL",
                "query_text": "SELECT COUNT(*) FROM threats",
                "result": "1234",
                "execution_time": 0.0234,
                "success": True
            },
            {
                "id": 2,
                "timestamp": datetime.now().isoformat(),
                "query_type": "Python",
                "query_text": "print('Hello World')",
                "result": "Hello World\n",
                "execution_time": 0.0123,
                "success": True
            }
        ]
    return []

@app.post("/api/sql/execute")
async def execute_sql_query(request: dict):
    """Execute SQL query"""
    query = request.get("query", "")
    
    # Mock SQL execution
    if "SELECT" in query.upper():
        result = [
            {"count": 1234, "avg_confidence": 85.5},
            {"attack_type": "Flood Attacks", "count": 800},
            {"attack_type": "Port Scan", "count": 200}
        ]
    else:
        result = "Query executed successfully. Rows affected: 1"
    
    return {
        "success": True,
        "result": result,
        "execution_time": 0.0234
    }

@app.post("/api/python/execute")
async def execute_python_code(request: dict):
    """Execute Python code"""
    code = request.get("code", "")
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        # Execute Python code
        result = subprocess.run(
            ['python3', temp_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Clean up
        os.unlink(temp_file)
        
        if result.returncode == 0:
            return {
                "success": True,
                "result": result.stdout,
                "execution_time": 0.1234
            }
        else:
            return {
                "success": False,
                "error": result.stderr,
                "execution_time": 0.1234
            }
            
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Code execution timed out (30s limit)",
            "execution_time": 30.0
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "execution_time": 0.0
        }

@app.get("/api/query/history")
async def get_query_history(limit: int = 20):
    """Get query execution history"""
    history = []
    for i in range(min(limit, 5)):
        history.append({
            "id": i + 1,
            "timestamp": datetime.now().isoformat(),
            "query_type": "SQL" if i % 2 == 0 else "Python",
            "query_text": f"SELECT * FROM threats LIMIT {i + 1}" if i % 2 == 0 else f"print('Query {i + 1}')",
            "result": f"Query {i + 1} result",
            "execution_time": 0.0234 + i * 0.01,
            "success": True
        })
    return history

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Extended Cybersecurity IDS/IPS Platform...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
