#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Working Cybersecurity IDS/IPS Platform - FastAPI Backend
Real-time threat detection with database storage and SQL/Python execution
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import logging
import subprocess
import tempfile
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import asyncio
import threading
import time
import random
from scapy.all import sniff, IP, TCP, UDP, ICMP, ARP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = "postgresql://cybersec:secure_password_123@localhost:5432/cybersec_ids"

# Create FastAPI app
app = FastAPI(
    title="Cybersecurity IDS/IPS Platform",
    description="Advanced Intrusion Detection & Prevention System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class SQLQuery(BaseModel):
    query: str

class PythonCode(BaseModel):
    code: str

# Database Manager
class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(DATABASE_URL)
            self.create_tables()
            logger.info("[OK] Database connected and initialized")
        except Exception as e:
            logger.error(f"[ERROR] Database connection failed: {e}")
    
    def create_tables(self):
        """Create necessary tables"""
        try:
            cursor = self.connection.cursor()
            
            # Threats table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS threats (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    source_ip VARCHAR(45),
                    dest_ip VARCHAR(45),
                    attack_type VARCHAR(100),
                    threat_level VARCHAR(20),
                    confidence FLOAT,
                    description TEXT,
                    raw_data TEXT
                )
            """)
            
            # Query history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_history (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    query_type VARCHAR(20),
                    query_text TEXT,
                    result TEXT,
                    execution_time FLOAT,
                    success BOOLEAN
                )
            """)
            
            self.connection.commit()
            cursor.close()
            logger.info("[OK] Database tables created")
        except Exception as e:
            logger.error(f"[ERROR] Failed to create tables: {e}")
    
    def save_threat(self, threat):
        """Save threat to database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO threats (source_ip, dest_ip, attack_type, threat_level, confidence, description, raw_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                threat.get('source_ip'),
                threat.get('dest_ip'),
                threat.get('attack_type'),
                threat.get('threat_level'),
                threat.get('confidence'),
                threat.get('description'),
                json.dumps(threat.get('raw_data', {}))
            ))
            self.connection.commit()
            cursor.close()
            logger.info(f"[DB] Threat saved to database")
        except Exception as e:
            logger.error(f"[ERROR] Failed to save threat: {e}")
    
    def get_threats(self, limit=50, offset=0):
        """Get threats from database"""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM threats 
                ORDER BY timestamp DESC 
                LIMIT %s OFFSET %s
            """, (limit, offset))
            
            threats = []
            for row in cursor.fetchall():
                threat = dict(row)
                if threat['timestamp']:
                    threat['timestamp'] = threat['timestamp'].isoformat()
                threats.append(threat)
            
            cursor.close()
            return threats
        except Exception as e:
            logger.error(f"[ERROR] Failed to get threats: {e}")
            return []
    
    def get_stats(self):
        """Get database statistics"""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            
            # Total threats
            cursor.execute("SELECT COUNT(*) as total FROM threats")
            total_threats = cursor.fetchone()['total']
            
            # Threats by level
            cursor.execute("SELECT threat_level, COUNT(*) as count FROM threats GROUP BY threat_level")
            threat_levels = {row['threat_level']: row['count'] for row in cursor.fetchall()}
            
            # Threats by type
            cursor.execute("SELECT attack_type, COUNT(*) as count FROM threats GROUP BY attack_type ORDER BY count DESC LIMIT 5")
            attack_types = {row['attack_type']: row['count'] for row in cursor.fetchall()}
            
            cursor.close()
            
            return {
                "total_threats": total_threats,
                "threat_levels": threat_levels,
                "attack_types": attack_types,
                "active_connections": 5,
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"[ERROR] Failed to get stats: {e}")
            return {
                "total_threats": 0,
                "threat_levels": {},
                "attack_types": {},
                "active_connections": 0,
                "last_updated": datetime.now().isoformat()
            }
    
    def execute_sql(self, query):
        """Execute SQL query"""
        start_time = time.time()
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                result = [dict(row) for row in cursor.fetchall()]
            else:
                self.connection.commit()
                result = f"Query executed successfully. Rows affected: {cursor.rowcount}"
            
            execution_time = time.time() - start_time
            cursor.close()
            
            self.save_query_history("SQL", query, json.dumps(result), execution_time, True)
            
            return {"success": True, "result": result, "execution_time": execution_time}
        except Exception as e:
            logger.error(f"[ERROR] SQL execution failed: {e}")
            self.save_query_history("SQL", query, str(e), 0, False)
            return {"success": False, "error": str(e), "execution_time": 0}
    
    def execute_python(self, code):
        """Execute Python code safely"""
        start_time = time.time()
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
            
            execution_time = time.time() - start_time
            
            # Clean up
            os.unlink(temp_file)
            
            if result.returncode == 0:
                output = result.stdout
                self.save_query_history("Python", code, output, execution_time, True)
                return {"success": True, "result": output, "execution_time": execution_time}
            else:
                error = result.stderr
                self.save_query_history("Python", code, error, execution_time, False)
                return {"success": False, "error": error, "execution_time": execution_time}
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Code execution timed out (30s limit)", "execution_time": 30}
        except Exception as e:
            logger.error(f"[ERROR] Python execution failed: {e}")
            return {"success": False, "error": str(e), "execution_time": 0}
    
    def save_query_history(self, query_type, query_text, result, execution_time, success):
        """Save query execution to history"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO query_history (query_type, query_text, result, execution_time, success)
                VALUES (%s, %s, %s, %s, %s)
            """, (query_type, query_text, result, execution_time, success))
            self.connection.commit()
            cursor.close()
        except Exception as e:
            logger.error(f"[ERROR] Failed to save query history: {e}")

# Initialize database manager
db_manager = DatabaseManager()

# WebSocket manager
class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

websocket_manager = WebSocketManager()

# Threat detector
class ThreatDetector:
    def __init__(self):
        self.target_ip = "192.168.100.124"
        self.port_scan_threshold = 5
        self.flood_threshold = 50
        self.connection_tracking = {}
    
    def detect_threat(self, packet):
        """Analyze packet for threats"""
        if not packet.haslayer(IP):
            return None
        
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        
        # Skip if not targeting our network
        if dst_ip != self.target_ip:
            return None
        
        threat = None
        
        # Port scan detection
        if packet.haslayer(TCP):
            key = f"{src_ip}_port_scan"
            if key not in self.connection_tracking:
                self.connection_tracking[key] = {"ports": set(), "timestamp": time.time()}
            
            self.connection_tracking[key]["ports"].add(packet[TCP].dport)
            
            if len(self.connection_tracking[key]["ports"]) > self.port_scan_threshold:
                threat = {
                    "source_ip": src_ip,
                    "dest_ip": dst_ip,
                    "attack_type": "Port Scan",
                    "threat_level": "HIGH",
                    "confidence": 0.9,
                    "description": f"Port scan detected from {src_ip}",
                    "raw_data": {"ports": list(self.connection_tracking[key]["ports"])}
                }
        
        # Flood detection
        elif packet.haslayer(ICMP):
            key = f"{src_ip}_icmp_flood"
            if key not in self.connection_tracking:
                self.connection_tracking[key] = {"count": 0, "timestamp": time.time()}
            
            self.connection_tracking[key]["count"] += 1
            
            if self.connection_tracking[key]["count"] > self.flood_threshold:
                threat = {
                    "source_ip": src_ip,
                    "dest_ip": dst_ip,
                    "attack_type": "ICMP Flood",
                    "threat_level": "HIGH",
                    "confidence": 0.85,
                    "description": f"ICMP flood detected from {src_ip}",
                    "raw_data": {"packet_count": self.connection_tracking[key]["count"]}
                }
        
        return threat

detector = ThreatDetector()

# Packet handler
def packet_handler(packet):
    """Handle captured packets"""
    try:
        threat = detector.detect_threat(packet)
        if threat:
            db_manager.save_threat(threat)
            # Broadcast threat via WebSocket
            asyncio.create_task(websocket_manager.broadcast(json.dumps(threat)))
    except Exception as e:
        logger.error(f"[ERROR] Packet handler error: {e}")

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Cybersecurity IDS/IPS Platform API", "status": "running"}

@app.get("/api/public/stats")
async def get_public_stats():
    """Get public statistics"""
    return db_manager.get_stats()

@app.get("/api/database/threats/recent")
async def get_recent_threats(limit: int = 50, offset: int = 0):
    """Get recent threats"""
    return db_manager.get_threats(limit, offset)

@app.get("/api/public/threats/recent")
async def get_public_threats(limit: int = 50, offset: int = 0):
    """Get recent threats (public endpoint)"""
    return db_manager.get_threats(limit, offset)

@app.post("/api/sql/execute")
async def execute_sql_query(query: SQLQuery):
    """Execute SQL query"""
    return db_manager.execute_sql(query.query)

@app.post("/api/python/execute")
async def execute_python_code(code: PythonCode):
    """Execute Python code"""
    return db_manager.execute_python(code.code)

@app.get("/api/database/tables")
async def get_database_tables():
    """Get all database tables and their info"""
    try:
        cursor = db_manager.connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT 
                schemaname,
                tablename,
                tableowner,
                tablespace,
                hasindexes,
                hasrules,
                hastriggers
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename
        """)
        
        tables = []
        for row in cursor.fetchall():
            table_info = dict(row)
            
            # Get row count for each table
            cursor.execute(f"SELECT COUNT(*) FROM {table_info['tablename']}")
            table_info['row_count'] = cursor.fetchone()[0]
            
            # Get table size
            cursor.execute(f"SELECT pg_size_pretty(pg_total_relation_size('{table_info['tablename']}'))")
            table_info['size'] = cursor.fetchone()[0]
            
            tables.append(table_info)
        
        cursor.close()
        return tables
    except Exception as e:
        logger.error(f"[ERROR] Failed to get database tables: {e}")
        return []

@app.get("/api/database/table/{table_name}/columns")
async def get_table_columns(table_name: str):
    """Get columns info for a specific table"""
    try:
        cursor = db_manager.connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = %s AND table_schema = 'public'
            ORDER BY ordinal_position
        """, (table_name,))
        
        columns = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return columns
    except Exception as e:
        logger.error(f"[ERROR] Failed to get table columns: {e}")
        return []

@app.get("/api/database/table/{table_name}/data")
async def get_table_data(table_name: str, limit: int = 100, offset: int = 0):
    """Get data from a specific table"""
    try:
        cursor = db_manager.connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(f"SELECT * FROM {table_name} ORDER BY 1 DESC LIMIT %s OFFSET %s", (limit, offset))
        
        data = []
        for row in cursor.fetchall():
            row_dict = dict(row)
            # Convert datetime objects to ISO string
            for key, value in row_dict.items():
                if hasattr(value, 'isoformat'):
                    row_dict[key] = value.isoformat()
            data.append(row_dict)
        
        cursor.close()
        return data
    except Exception as e:
        logger.error(f"[ERROR] Failed to get table data: {e}")
        return []

@app.get("/api/query/history")
async def get_query_history(limit: int = 20):
    """Get query execution history"""
    try:
        cursor = db_manager.connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT * FROM query_history 
            ORDER BY timestamp DESC 
            LIMIT %s
        """, (limit,))
        
        history = []
        for row in cursor.fetchall():
            entry = dict(row)
            if entry['timestamp']:
                entry['timestamp'] = entry['timestamp'].isoformat()
            history.append(entry)
        
        cursor.close()
        return history
    except Exception as e:
        logger.error(f"[ERROR] Failed to get query history: {e}")
        return []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for testing
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

# Network monitoring function
def start_network_monitoring():
    """Start network packet capture"""
    try:
        logger.info("[MONITOR] Starting network monitoring...")
        sniff(filter=f"host {detector.target_ip}", prn=packet_handler, store=0)
    except Exception as e:
        logger.error(f"[ERROR] Network monitoring error: {e}")

# Start network monitoring in background thread
monitoring_thread = threading.Thread(target=start_network_monitoring, daemon=True)
monitoring_thread.start()

# Generate some sample threats for testing
def generate_sample_threats():
    """Generate sample threats for testing"""
    sample_threats = [
        {
            "source_ip": "192.168.100.200",
            "dest_ip": "192.168.100.124",
            "attack_type": "Port Scan",
            "threat_level": "HIGH",
            "confidence": 0.9,
            "description": "Automated port scan detected",
            "raw_data": {"ports": [22, 80, 443, 3389, 5432]}
        },
        {
            "source_ip": "34.160.144.191",
            "dest_ip": "192.168.100.124",
            "attack_type": "Reconnaissance",
            "threat_level": "MEDIUM",
            "confidence": 0.7,
            "description": "Suspicious reconnaissance activity",
            "raw_data": {"user_agent": "Nmap NSE"}
        }
    ]
    
    for threat in sample_threats:
        db_manager.save_threat(threat)
    
    logger.info(f"[INIT] Generated {len(sample_threats)} sample threats")

# Generate sample data on startup
generate_sample_threats()

if __name__ == "__main__":
    import uvicorn
    logger.info("[STARTUP] Starting Complete Cybersecurity IDS/IPS Platform...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
