#!/usr/bin/env python3
"""
Real PostgreSQL Backend - Connects to Docker PostgreSQL
"""

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import logging
import subprocess
import tempfile
import os
from datetime import datetime
from typing import List, Dict, Any
import asyncio
import time

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
    description="Advanced Intrusion Detection & Prevention System with Real PostgreSQL",
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

# Database connection
def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None

def init_database():
    """Initialize database tables"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Create threats table
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
        
        # Create query history table
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
        
        # Insert some sample data if tables are empty
        cursor.execute("SELECT COUNT(*) FROM threats")
        if cursor.fetchone()[0] == 0:
            sample_threats = [
                ('192.168.100.200', '192.168.100.124', 'Port Scan', 'HIGH', 0.95, 'Automated port scan detected', '{"ports": [22, 80, 443, 3389]}'),
                ('34.160.144.191', '192.168.100.124', 'Reconnaissance', 'MEDIUM', 0.75, 'Suspicious reconnaissance activity', '{"user_agent": "Nmap NSE"}'),
                ('192.168.100.150', '192.168.100.124', 'Flood Attack', 'HIGH', 0.90, 'ICMP flood detected', '{"packet_count": 1000}'),
                ('10.0.0.100', '192.168.100.124', 'Brute Force', 'CRITICAL', 0.98, 'SSH brute force attempt', '{"attempts": 50}'),
                ('172.16.0.50', '192.168.100.124', 'Malware', 'CRITICAL', 0.99, 'Malware communication detected', '{"signature": "Trojan.Generic"}')
            ]
            
            for threat in sample_threats:
                cursor.execute("""
                    INSERT INTO threats (source_ip, dest_ip, attack_type, threat_level, confidence, description, raw_data)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, threat)
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        if conn:
            conn.close()
        return False

# Initialize database on startup
init_database()

@app.get("/")
async def root():
    return {"message": "Cybersecurity IDS/IPS Platform API - Real PostgreSQL", "status": "running"}

@app.get("/api/public/stats")
async def get_public_stats():
    """Get real statistics from PostgreSQL"""
    conn = get_db_connection()
    if not conn:
        return {"error": "Database connection failed"}
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Total threats
        cursor.execute("SELECT COUNT(*) as total FROM threats")
        total_threats = cursor.fetchone()['total']
        
        # Threats by level
        cursor.execute("SELECT threat_level, COUNT(*) as count FROM threats GROUP BY threat_level")
        threat_levels = {row['threat_level']: row['count'] for row in cursor.fetchall()}
        
        # Threats by type
        cursor.execute("SELECT attack_type, COUNT(*) as count FROM threats GROUP BY attack_type ORDER BY count DESC")
        attack_types = {row['attack_type']: row['count'] for row in cursor.fetchall()}
        
        cursor.close()
        conn.close()
        
        return {
            "total_threats": total_threats,
            "threat_levels": threat_levels,
            "attack_types": attack_types,
            "active_connections": 5,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        if conn:
            conn.close()
        return {"error": str(e)}

@app.get("/api/public/threats/recent")
async def get_recent_threats(limit: int = 50, offset: int = 0):
    """Get recent threats from PostgreSQL"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
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
        conn.close()
        return threats
        
    except Exception as e:
        logger.error(f"Failed to get threats: {e}")
        if conn:
            conn.close()
        return []

@app.get("/api/database/threats/recent")
async def get_database_threats(limit: int = 50, offset: int = 0):
    """Get recent threats from database"""
    return await get_recent_threats(limit, offset)

@app.get("/api/database/tables")
async def get_database_tables():
    """Get all database tables and their info from PostgreSQL"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get table names first
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename
        """)
        
        table_names = [row['tablename'] for row in cursor.fetchall()]
        tables = []
        
        for table_name in table_names:
            try:
                # Get row count
                cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                row_count = cursor.fetchone()['count']
                
                # Get table size
                cursor.execute(f"SELECT pg_size_pretty(pg_total_relation_size('{table_name}')) as size")
                size = cursor.fetchone()['size']
                
                table_info = {
                    'schemaname': 'public',
                    'tablename': table_name,
                    'tableowner': 'cybersec',
                    'tablespace': None,
                    'hasindexes': True,
                    'hasrules': False,
                    'hastriggers': False,
                    'row_count': row_count,
                    'size': size
                }
                
                tables.append(table_info)
                
            except Exception as table_error:
                logger.error(f"Error processing table {table_name}: {table_error}")
                continue
        
        cursor.close()
        conn.close()
        return tables
        
    except Exception as e:
        logger.error(f"Failed to get database tables: {e}")
        if conn:
            conn.close()
        return []

@app.get("/api/database/table/{table_name}/columns")
async def get_table_columns(table_name: str):
    """Get columns info for a specific table from PostgreSQL"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
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
        conn.close()
        return columns
        
    except Exception as e:
        logger.error(f"Failed to get table columns: {e}")
        if conn:
            conn.close()
        return []

@app.get("/api/database/table/{table_name}/data")
async def get_table_data(table_name: str, limit: int = 100, offset: int = 0):
    """Get data from a specific table from PostgreSQL"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
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
        conn.close()
        return data
        
    except Exception as e:
        logger.error(f"Failed to get table data: {e}")
        if conn:
            conn.close()
        return []

@app.post("/api/sql/execute")
async def execute_sql_query(request: dict):
    """Execute SQL query on PostgreSQL"""
    query = request.get("query", "")
    start_time = time.time()
    
    conn = get_db_connection()
    if not conn:
        return {"success": False, "error": "Database connection failed"}
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query)
        
        if query.strip().upper().startswith('SELECT'):
            result = [dict(row) for row in cursor.fetchall()]
            # Convert datetime objects to strings
            for row in result:
                for key, value in row.items():
                    if hasattr(value, 'isoformat'):
                        row[key] = value.isoformat()
        else:
            conn.commit()
            result = f"Query executed successfully. Rows affected: {cursor.rowcount}"
        
        execution_time = time.time() - start_time
        
        # Save to query history
        cursor.execute("""
            INSERT INTO query_history (query_type, query_text, result, execution_time, success)
            VALUES (%s, %s, %s, %s, %s)
        """, ("SQL", query, json.dumps(result), execution_time, True))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "result": result,
            "execution_time": execution_time
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"SQL execution failed: {e}")
        
        # Save failed query to history
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO query_history (query_type, query_text, result, execution_time, success)
                VALUES (%s, %s, %s, %s, %s)
            """, ("SQL", query, str(e), execution_time, False))
            conn.commit()
            cursor.close()
        except:
            pass
        
        if conn:
            conn.close()
        
        return {
            "success": False,
            "error": str(e),
            "execution_time": execution_time
        }

@app.post("/api/python/execute")
async def execute_python_code(request: dict):
    """Execute Python code"""
    code = request.get("code", "")
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
        
        # Save to query history
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                success = result.returncode == 0
                output = result.stdout if success else result.stderr
                cursor.execute("""
                    INSERT INTO query_history (query_type, query_text, result, execution_time, success)
                    VALUES (%s, %s, %s, %s, %s)
                """, ("Python", code, output, execution_time, success))
                conn.commit()
                cursor.close()
                conn.close()
            except:
                pass
        
        if result.returncode == 0:
            return {
                "success": True,
                "result": result.stdout,
                "execution_time": execution_time
            }
        else:
            return {
                "success": False,
                "error": result.stderr,
                "execution_time": execution_time
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
            "execution_time": time.time() - start_time
        }

@app.get("/api/query/history")
async def get_query_history(limit: int = 20):
    """Get query execution history from PostgreSQL"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
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
        conn.close()
        return history
        
    except Exception as e:
        logger.error(f"Failed to get query history: {e}")
        if conn:
            conn.close()
        return []

@app.websocket("/ws")
async def websocket_endpoint(websocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    try:
        while True:
            # Keep connection alive
            await asyncio.sleep(30)
            await websocket.send_text('{"type": "ping", "timestamp": "' + datetime.now().isoformat() + '"}')
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get comprehensive dashboard statistics from real database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get total threat alerts
        cursor.execute("SELECT COUNT(*) as total FROM threat_alerts")
        total_threats = cursor.fetchone()['total']
        
        # Get active threats (last 24 hours)
        cursor.execute("""
            SELECT COUNT(*) as active 
            FROM threat_alerts 
            WHERE timestamp >= NOW() - INTERVAL '24 hours'
        """)
        active_threats = cursor.fetchone()['active']
        
        # Get blocked attacks
        cursor.execute("""
            SELECT COUNT(*) as blocked 
            FROM threat_alerts 
            WHERE blocked = true
        """)
        blocked_attacks = cursor.fetchone()['blocked']
        
        # Get threat level distribution
        cursor.execute("""
            SELECT threat_level, COUNT(*) as count 
            FROM threat_alerts 
            GROUP BY threat_level 
            ORDER BY count DESC 
            LIMIT 1
        """)
        dominant_threat_level = cursor.fetchone()
        threat_level = dominant_threat_level['threat_level'] if dominant_threat_level else 'LOW'
        
        # Get unique source IPs (simulating network devices)
        cursor.execute("SELECT COUNT(DISTINCT source_ip) as devices FROM threat_alerts")
        total_devices = cursor.fetchone()['devices']
        
        # Calculate network traffic (simulated based on alerts)
        network_traffic = min(active_threats * 0.5, 100.0)  # Simulate Mbps
        
        # Calculate uptime (simulated)
        uptime_hours = 24 * 7  # Simulate 1 week uptime
        
        cursor.close()
        conn.close()
        
        return {
            "total_devices": total_devices,
            "active_threats": active_threats,
            "blocked_attacks": blocked_attacks,
            "network_traffic": round(network_traffic, 1),
            "threat_level": threat_level,
            "uptime_hours": uptime_hours,
            "last_updated": datetime.now().isoformat(),
            "total_threats": total_threats
        }
        
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/threats/recent")
async def get_recent_threats(limit: int = 20):
    """Get recent threat alerts with proper formatting"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT 
                id::text,
                timestamp,
                source_ip,
                destination_ip,
                attack_type,
                threat_level,
                confidence,
                description,
                blocked
            FROM threat_alerts 
            ORDER BY timestamp DESC 
            LIMIT %s
        """, (limit,))
        
        threats = cursor.fetchall()
        
        # Format threats for frontend
        formatted_threats = []
        for threat in threats:
            formatted_threats.append({
                "id": threat['id'],
                "timestamp": threat['timestamp'].isoformat() if threat['timestamp'] else datetime.now().isoformat(),
                "source_ip": threat['source_ip'] or 'Unknown',
                "destination_ip": threat['destination_ip'] or 'Unknown',
                "attack_type": threat['attack_type'] or 'Unknown',
                "threat_level": threat['threat_level'] or 'LOW',
                "confidence": float(threat['confidence']) if threat['confidence'] else 0.5,
                "description": threat['description'] or 'No description available',
                "blocked": bool(threat['blocked'])
            })
        
        cursor.close()
        conn.close()
        
        return {"threats": formatted_threats}
        
    except Exception as e:
        logger.error(f"Recent threats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/analytics")
async def get_dashboard_analytics():
    """Get analytics data for dashboard charts"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Attack timeline (last 24 hours by hour)
        cursor.execute("""
            SELECT 
                DATE_TRUNC('hour', timestamp) as hour,
                COUNT(*) as total_count,
                COUNT(CASE WHEN blocked = true THEN 1 END) as blocked_count
            FROM threat_alerts 
            WHERE timestamp >= NOW() - INTERVAL '24 hours'
            GROUP BY DATE_TRUNC('hour', timestamp)
            ORDER BY hour
        """)
        
        timeline_data = []
        for row in cursor.fetchall():
            timeline_data.append({
                "timestamp": row['hour'].isoformat() if row['hour'] else datetime.now().isoformat(),
                "count": row['total_count'],
                "blocked_count": row['blocked_count']
            })
        
        # Attack types distribution
        cursor.execute("""
            SELECT attack_type, COUNT(*) as count 
            FROM threat_alerts 
            GROUP BY attack_type 
            ORDER BY count DESC 
            LIMIT 10
        """)
        
        attack_types = []
        for row in cursor.fetchall():
            attack_types.append({
                "name": row['attack_type'],
                "value": row['count']
            })
        
        # Threat levels distribution
        cursor.execute("""
            SELECT threat_level, COUNT(*) as count 
            FROM threat_alerts 
            GROUP BY threat_level
        """)
        
        threat_levels = []
        for row in cursor.fetchall():
            threat_levels.append({
                "name": row['threat_level'],
                "value": row['count']
            })
        
        cursor.close()
        conn.close()
        
        return {
            "timeline": timeline_data,
            "attack_types": attack_types,
            "threat_levels": threat_levels
        }
        
    except Exception as e:
        logger.error(f"Dashboard analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Real PostgreSQL Cybersecurity IDS/IPS Platform...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
