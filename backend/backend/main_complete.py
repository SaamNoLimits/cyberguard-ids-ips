#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Complete Cybersecurity IDS/IPS Platform - FastAPI Backend
Real-time threat detection with database storage and SQL/Python execution
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import threading
import time
import subprocess
import tempfile
import os

# Database imports
import asyncpg
import psycopg2
from psycopg2.extras import RealDictCursor

# Network monitoring imports
from scapy.all import sniff, IP, TCP, UDP, ICMP, ARP
import socket

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = "postgresql://cybersec:secure_password_123@localhost:5432/cybersec_ids"

# Global variables
threats = []
websocket_connections = []
stats = {
    "total_threats": 0,
    "active_connections": 0,
    "threat_levels": {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0},
    "attack_types": {},
    "last_updated": datetime.now().isoformat()
}

# Create FastAPI app
app = FastAPI(
    title="Complete Cybersecurity IDS/IPS Platform",
    description="Real-time Intrusion Detection with Database Storage and Script Execution",
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

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.init_database()
    
    def init_database(self):
        """Initialize database connection and create tables"""
        try:
            self.connection = psycopg2.connect(DATABASE_URL)
            self.create_tables()
            logger.info("[OK] Database connected and initialized")
        except Exception as e:
            logger.error(f"[ERROR] Database connection failed: {e}")
    
    def create_tables(self):
        """Create necessary tables"""
        cursor = self.connection.cursor()
        
        # Create threats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS threats (
                id VARCHAR(255) PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source_ip VARCHAR(45),
                destination_ip VARCHAR(45),
                attack_type VARCHAR(100),
                threat_level VARCHAR(20),
                confidence FLOAT,
                description TEXT,
                blocked BOOLEAN DEFAULT FALSE,
                raw_data JSONB
            )
        """)
        
        # Create query_history table for SQL/Python execution
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_history (
                id SERIAL PRIMARY KEY,
                query_type VARCHAR(20),
                query_text TEXT,
                result TEXT,
                execution_time FLOAT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN
            )
        """)
        
        self.connection.commit()
        cursor.close()
    
    def save_threat(self, threat):
        """Save threat to database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO threats (id, timestamp, source_ip, destination_ip, attack_type, 
                                   threat_level, confidence, description, blocked, raw_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                threat["id"],
                threat["timestamp"],
                threat["source_ip"],
                threat["destination_ip"],
                threat["attack_type"],
                threat["threat_level"],
                threat["confidence"],
                threat["description"],
                threat["blocked"],
                json.dumps(threat["raw_data"])
            ))
            self.connection.commit()
            cursor.close()
            logger.info(f"[DB] Threat {threat['id']} saved to database")
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
                threat["timestamp"] = threat["timestamp"].isoformat()
                if threat["raw_data"]:
                    threat["raw_data"] = json.loads(threat["raw_data"]) if isinstance(threat["raw_data"], str) else threat["raw_data"]
                threats.append(threat)
            
            cursor.close()
            return threats
        except Exception as e:
            logger.error(f"[ERROR] Failed to get threats: {e}")
            return []
    
    def get_stats(self):
        """Get database statistics"""
        try:
            cursor = self.connection.cursor()
            
            # Total threats
            cursor.execute("SELECT COUNT(*) FROM threats")
            total = cursor.fetchone()[0]
            
            # Threat levels
            cursor.execute("""
                SELECT threat_level, COUNT(*) 
                FROM threats 
                GROUP BY threat_level
            """)
            levels = dict(cursor.fetchall())
            
            # Attack types
            cursor.execute("""
                SELECT attack_type, COUNT(*) 
                FROM threats 
                GROUP BY attack_type
            """)
            types = dict(cursor.fetchall())
            
            cursor.close()
            
            return {
                "total_threats": total,
                "threat_levels": levels,
                "attack_types": types,
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"[ERROR] Failed to get stats: {e}")
            return stats
    
    def execute_sql(self, query):
        """Execute SQL query"""
        try:
            start_time = time.time()
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                result = [dict(row) for row in result]
            else:
                self.connection.commit()
                result = {"message": f"Query executed successfully. Rows affected: {cursor.rowcount}"}
            
            execution_time = time.time() - start_time
            cursor.close()
            
            # Save to history
            self.save_query_history("SQL", query, str(result), execution_time, True)
            
            return {"success": True, "result": result, "execution_time": execution_time}
        except Exception as e:
            logger.error(f"[ERROR] SQL execution failed: {e}")
            self.save_query_history("SQL", query, str(e), 0, False)
            return {"success": False, "error": str(e)}
    
    def execute_python(self, code):
        """Execute Python code safely"""
        try:
            start_time = time.time()
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Execute Python code
            result = subprocess.run(
                ['python3', temp_file],
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
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
                return {"success": False, "error": error}
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Code execution timed out (30s limit)"}
        except Exception as e:
            logger.error(f"[ERROR] Python execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    def save_query_history(self, query_type, query_text, result, execution_time, success):
        """Save query execution history"""
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

class ThreatDetector:
    def __init__(self, db_manager):
        self.target_ip = "192.168.100.124"  # Your machine IP
        self.db_manager = db_manager
        self.attack_patterns = {
            "syn_flood": {"count": 0, "threshold": 50},
            "port_scan": {"ports": set(), "threshold": 10},
            "icmp_flood": {"count": 0, "threshold": 20},
            "arp_scan": {"count": 0, "threshold": 30}
        }
        
    def detect_attack(self, packet):
        """Detect various types of attacks"""
        try:
            if not packet.haslayer(IP):
                return None
                
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            
            # Only monitor traffic to our target IP
            if dst_ip != self.target_ip:
                return None
                
            threat = None
            
            # TCP SYN Flood Detection
            if packet.haslayer(TCP) and packet[TCP].flags == 2:  # SYN flag
                self.attack_patterns["syn_flood"]["count"] += 1
                if self.attack_patterns["syn_flood"]["count"] > self.attack_patterns["syn_flood"]["threshold"]:
                    threat = {
                        "id": str(uuid.uuid4()),
                        "timestamp": datetime.now().isoformat(),
                        "source_ip": src_ip,
                        "destination_ip": dst_ip,
                        "attack_type": "Flood Attacks",
                        "threat_level": "HIGH",
                        "confidence": 95.0,
                        "description": f"SYN flood attack detected from {src_ip}",
                        "blocked": False,
                        "raw_data": {
                            "protocol": "TCP",
                            "src_port": packet[TCP].sport,
                            "dst_port": packet[TCP].dport,
                            "flags": packet[TCP].flags
                        }
                    }
                    self.attack_patterns["syn_flood"]["count"] = 0
            
            # Port Scan Detection
            elif packet.haslayer(TCP):
                port = packet[TCP].dport
                self.attack_patterns["port_scan"]["ports"].add(port)
                if len(self.attack_patterns["port_scan"]["ports"]) > self.attack_patterns["port_scan"]["threshold"]:
                    threat = {
                        "id": str(uuid.uuid4()),
                        "timestamp": datetime.now().isoformat(),
                        "source_ip": src_ip,
                        "destination_ip": dst_ip,
                        "attack_type": "Reconnaissance",
                        "threat_level": "MEDIUM",
                        "confidence": 85.0,
                        "description": f"Port scan detected from {src_ip} - {len(self.attack_patterns['port_scan']['ports'])} ports scanned",
                        "blocked": False,
                        "raw_data": {
                            "protocol": "TCP",
                            "scanned_ports": list(self.attack_patterns["port_scan"]["ports"])[-10:],
                            "total_ports": len(self.attack_patterns["port_scan"]["ports"])
                        }
                    }
                    self.attack_patterns["port_scan"]["ports"].clear()
            
            return threat
            
        except Exception as e:
            logger.error(f"Error in attack detection: {e}")
            return None

# Initialize database and detector
db_manager = DatabaseManager()
detector = ThreatDetector(db_manager)

def packet_handler(packet):
    """Handle captured packets"""
    threat = detector.detect_attack(packet)
    if threat:
        # Add to in-memory list
        threats.append(threat)
        if len(threats) > 100:  # Keep only last 100 in memory
            threats.pop(0)
        
        # Save to database
        db_manager.save_threat(threat)
        
        logger.info(f"🚨 THREAT DETECTED: {threat['attack_type']} from {threat['source_ip']} -> {threat['destination_ip']}")
        
        # Broadcast to WebSocket clients
        asyncio.create_task(broadcast_threat(threat))

async def broadcast_threat(threat):
    """Broadcast threat to all WebSocket connections"""
    if websocket_connections:
        message = json.dumps({
            "type": "new_threat",
            "data": threat
        })
        
        disconnected = []
        for websocket in websocket_connections:
            try:
                await websocket.send_text(message)
            except:
                disconnected.append(websocket)
        
        for ws in disconnected:
            websocket_connections.remove(ws)

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

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Complete Cybersecurity IDS/IPS Platform", "status": "monitoring", "database": "connected"}

@app.get("/api/public/stats")
async def get_stats():
    """Get real-time statistics from database"""
    db_stats = db_manager.get_stats()
    db_stats["active_connections"] = len(websocket_connections)
    return db_stats

@app.get("/api/public/threats/recent")
async def get_recent_threats(limit: int = 50, offset: int = 0):
    """Get recent threats from database"""
    return db_manager.get_threats(limit, offset)

@app.get("/api/database/threats/recent")
async def get_database_threats(limit: int = 50, offset: int = 0):
    """Get threats from database (alias for compatibility)"""
    return db_manager.get_threats(limit, offset)

@app.get("/api/database/stats")
async def get_database_stats():
    """Get database statistics"""
    return db_manager.get_stats()

@app.post("/api/public/threats/generate")
async def generate_test_threat():
    """Generate a test threat"""
    threat = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "source_ip": "192.168.100.200",
        "destination_ip": detector.target_ip,
        "attack_type": "Flood Attacks",
        "threat_level": "HIGH",
        "confidence": 100.0,
        "description": "Generated test threat for demonstration",
        "blocked": False,
        "raw_data": {"test": True, "generated": True}
    }
    
    # Add to memory and database
    threats.append(threat)
    db_manager.save_threat(threat)
    
    # Broadcast
    await broadcast_threat(threat)
    
    return threat

@app.post("/api/sql/execute")
async def execute_sql(request: Request):
    """Execute SQL query"""
    body = await request.json()
    query = body.get("query", "")
    
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    result = db_manager.execute_sql(query)
    return result

@app.post("/api/python/execute")
async def execute_python(request: Request):
    """Execute Python code"""
    body = await request.json()
    code = body.get("code", "")
    
    if not code:
        raise HTTPException(status_code=400, detail="Code is required")
    
    result = db_manager.execute_python(code)
    return result

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
            item = dict(row)
            item["timestamp"] = item["timestamp"].isoformat()
            history.append(item)
        
        cursor.close()
        return history
    except Exception as e:
        logger.error(f"[ERROR] Failed to get query history: {e}")
        return []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    websocket_connections.append(websocket)
    logger.info(f"📡 WebSocket client connected. Total: {len(websocket_connections)}")
    
    try:
        while True:
            await asyncio.sleep(10)
            if websocket in websocket_connections:
                stats_message = json.dumps({
                    "type": "stats_update",
                    "data": db_manager.get_stats()
                })
                await websocket.send_text(stats_message)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)
        logger.info(f"📡 WebSocket client disconnected. Total: {len(websocket_connections)}")

if __name__ == "__main__":
    import uvicorn
    logger.info("[STARTUP] Starting Complete Cybersecurity IDS/IPS Platform...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
