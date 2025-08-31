"""
Python Script Execution Service
Executes Python scripts for data analysis and visualization
"""

import os
import sys
import subprocess
import tempfile
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import psycopg2
from datetime import datetime

logger = logging.getLogger(__name__)

class PythonExecutor:
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.output_dir = Path("/tmp/cybersec_analytics")
        self.output_dir.mkdir(exist_ok=True)
        
    def execute_script(self, script_code: str, script_name: str = "analysis") -> Dict[str, Any]:
        """
        Execute a Python script and return results
        """
        try:
            # Create temporary script file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                # Inject database connection at the beginning of the script
                db_host = self.db_config.get("host", "localhost")
                db_port = self.db_config.get("port", "5432")
                db_name = self.db_config.get("database", "cybersec_ids")
                db_user = self.db_config.get("user", "cybersec")
                db_password = self.db_config.get("password", "secure_password_123")
                
                db_injection = f"""
# Auto-injected database connection
import os
import sys
sys.path.append('/home/saamnolimits/Desktop/pfaf/backend/backend/venv_new/lib/python3.12/site-packages')

# Database configuration
os.environ['DB_HOST'] = '{db_host}'
os.environ['DB_PORT'] = '{db_port}'
os.environ['DB_NAME'] = '{db_name}'
os.environ['DB_USER'] = '{db_user}'
os.environ['DB_PASSWORD'] = '{db_password}'

# Database connection helpers
def get_db_connection():
    import psycopg2
    return psycopg2.connect(
        host=os.environ['DB_HOST'],
        port=os.environ['DB_PORT'],
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD']
    )

# SQLAlchemy engine for pandas
try:
    from sqlalchemy import create_engine
    db_url = f"postgresql://{{os.environ['DB_USER']}}:{{os.environ['DB_PASSWORD']}}@{{os.environ['DB_HOST']}}:{{os.environ['DB_PORT']}}/{{os.environ['DB_NAME']}}"
    engine = create_engine(db_url)
except ImportError:
    print("SQLAlchemy not available, using psycopg2 directly")
    engine = None

# Original script starts here
"""
                f.write(db_injection + script_code)
                script_path = f.name
            
            # Execute the script
            start_time = datetime.now()
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=str(self.output_dir)
            )
            end_time = datetime.now()
            
            # Clean up temporary file
            os.unlink(script_path)
            
            execution_time = (end_time - start_time).total_seconds()
            
            # Check for generated files
            generated_files = []
            for file_path in self.output_dir.glob("*"):
                if file_path.is_file() and file_path.stat().st_mtime > start_time.timestamp():
                    generated_files.append({
                        "name": file_path.name,
                        "path": str(file_path),
                        "size": file_path.stat().st_size
                    })
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "execution_time": execution_time,
                "generated_files": generated_files,
                "timestamp": datetime.now().isoformat()
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "Script execution timed out (5 minutes)",
                "execution_time": 300,
                "generated_files": [],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error executing Python script: {e}")
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "execution_time": 0,
                "generated_files": [],
                "timestamp": datetime.now().isoformat()
            }
    
    def test_database_connection(self) -> Dict[str, Any]:
        """
        Test database connection and return basic stats
        """
        try:
            conn = psycopg2.connect(
                host=self.db_config.get("host", "localhost"),
                port=self.db_config.get("port", "5432"),
                database=self.db_config.get("database", "cybersec_ids"),
                user=self.db_config.get("user", "cybersec"),
                password=self.db_config.get("password", "secure_password_123")
            )
            
            with conn.cursor() as cursor:
                # Get table info
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                tables = [row[0] for row in cursor.fetchall()]
                
                # Get threat_alerts count if table exists
                threat_count = 0
                if 'threat_alerts' in tables:
                    cursor.execute("SELECT COUNT(*) FROM threat_alerts")
                    threat_count = cursor.fetchone()[0]
                
            conn.close()
            
            return {
                "success": True,
                "message": "Database connection successful",
                "tables": tables,
                "threat_count": threat_count,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return {
                "success": False,
                "message": f"Database connection failed: {str(e)}",
                "tables": [],
                "threat_count": 0,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_sample_data(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get sample data from threat_alerts table
        """
        try:
            conn = psycopg2.connect(
                host=self.db_config.get("host", "localhost"),
                port=self.db_config.get("port", "5432"),
                database=self.db_config.get("database", "cybersec_ids"),
                user=self.db_config.get("user", "cybersec"),
                password=self.db_config.get("password", "secure_password_123")
            )
            
            with conn.cursor() as cursor:
                cursor.execute(f"""
                    SELECT 
                        id, timestamp, source_ip, destination_ip, 
                        attack_type, threat_level, confidence, blocked
                    FROM threat_alerts 
                    ORDER BY timestamp DESC 
                    LIMIT {limit}
                """)
                
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                
                data = []
                for row in rows:
                    data.append(dict(zip(columns, row)))
            
            conn.close()
            
            return {
                "success": True,
                "data": data,
                "count": len(data),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching sample data: {e}")
            return {
                "success": False,
                "data": [],
                "count": 0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
