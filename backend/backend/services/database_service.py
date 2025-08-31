"""
Database service for persistent threat storage and PCAP management
"""

import os
import hashlib
import gzip
import shutil
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, desc, func, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import uuid
import logging

from models.database_models import Base, ThreatAlert, PcapFile, NetworkDevice, AuditLog
from models.schemas import ThreatAlert as ThreatAlertSchema
from core.config import settings

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.pcap_storage_path = os.path.join(os.path.dirname(__file__), "..", "..", "pcap_storage")
        self.ensure_pcap_directory()
        
    async def initialize(self):
        """Initialize database connection and create tables"""
        try:
            # Create database engine
            self.engine = create_engine(
                settings.DATABASE_URL,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=settings.DEBUG
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            
            logger.info("✅ Database service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize database: {e}")
            return False
    
    def ensure_pcap_directory(self):
        """Ensure PCAP storage directory exists"""
        os.makedirs(self.pcap_storage_path, exist_ok=True)
        
        # Create subdirectories by date
        today = datetime.now().strftime("%Y-%m-%d")
        daily_path = os.path.join(self.pcap_storage_path, today)
        os.makedirs(daily_path, exist_ok=True)
        
    def get_db_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    async def save_threat_alert(self, threat_alert: ThreatAlertSchema, pcap_data: Optional[bytes] = None) -> bool:
        """Save threat alert to database with optional PCAP data"""
        try:
            db = self.get_db_session()
            
            # Create PCAP file if data provided
            pcap_file_path = None
            if pcap_data:
                pcap_file_path = await self.save_pcap_data(threat_alert.id, pcap_data, threat_alert.source_ip)
            
            # Create database record
            db_threat = ThreatAlert(
                id=threat_alert.id,
                timestamp=threat_alert.timestamp,
                source_ip=threat_alert.source_ip,
                destination_ip=threat_alert.destination_ip,
                attack_type=threat_alert.attack_type.value,
                threat_level=threat_alert.threat_level.value,
                confidence=threat_alert.confidence,
                description=threat_alert.description,
                blocked=threat_alert.blocked,
                raw_data=threat_alert.raw_data,
                pcap_file_path=pcap_file_path,
                packet_count=1,  # Will be updated if more packets are associated
                duration_seconds=0.0,
                bytes_transferred=threat_alert.raw_data.get('packet_size', 0) if threat_alert.raw_data else 0
            )
            
            db.add(db_threat)
            db.commit()
            db.refresh(db_threat)
            
            logger.info(f"✅ Threat alert {threat_alert.id} saved to database")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"❌ Database error saving threat alert: {e}")
            db.rollback()
            return False
        except Exception as e:
            logger.error(f"❌ Error saving threat alert: {e}")
            return False
        finally:
            db.close()
    
    async def save_pcap_data(self, threat_id: str, pcap_data: bytes, source_ip: str) -> str:
        """Save PCAP data to file and return file path"""
        try:
            # Create filename with timestamp and threat ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"threat_{threat_id}_{timestamp}_{source_ip.replace('.', '_')}.pcap"
            
            # Create daily directory
            today = datetime.now().strftime("%Y-%m-%d")
            daily_path = os.path.join(self.pcap_storage_path, today)
            os.makedirs(daily_path, exist_ok=True)
            
            file_path = os.path.join(daily_path, filename)
            
            # Write PCAP data
            with open(file_path, 'wb') as f:
                f.write(pcap_data)
            
            # Calculate file hash
            file_hash = hashlib.sha256(pcap_data).hexdigest()
            
            # Save PCAP file record to database
            db = self.get_db_session()
            pcap_record = PcapFile(
                id=str(uuid.uuid4()),
                filename=filename,
                file_path=file_path,
                file_size=len(pcap_data),
                packet_count=1,  # Will be updated with actual count
                start_time=datetime.now(),
                end_time=datetime.now(),
                duration_seconds=0.0,
                interface_name="captured",
                created_at=datetime.now(),
                threat_alert_ids=[threat_id],
                file_hash=file_hash,
                compressed=False
            )
            
            db.add(pcap_record)
            db.commit()
            db.close()
            
            logger.info(f"✅ PCAP file saved: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"❌ Error saving PCAP data: {e}")
            return None
    
    async def get_recent_threats(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get recent threats from database"""
        try:
            db = self.get_db_session()
            
            threats = db.query(ThreatAlert)\
                       .order_by(desc(ThreatAlert.timestamp))\
                       .offset(offset)\
                       .limit(limit)\
                       .all()
            
            result = []
            for threat in threats:
                threat_dict = {
                    "id": threat.id,
                    "timestamp": threat.timestamp.isoformat(),
                    "source_ip": threat.source_ip,
                    "destination_ip": threat.destination_ip,
                    "attack_type": threat.attack_type,
                    "threat_level": threat.threat_level,
                    "confidence": threat.confidence,
                    "description": threat.description,
                    "blocked": threat.blocked,
                    "raw_data": threat.raw_data,
                    "pcap_file_path": threat.pcap_file_path,
                    "packet_count": threat.packet_count,
                    "duration_seconds": threat.duration_seconds,
                    "bytes_transferred": threat.bytes_transferred
                }
                result.append(threat_dict)
            
            db.close()
            return result
            
        except Exception as e:
            logger.error(f"❌ Error getting recent threats: {e}")
            return []
    
    async def get_threat_statistics(self) -> Dict[str, Any]:
        """Get threat statistics from database"""
        try:
            db = self.get_db_session()
            
            # Total threats
            total_threats = db.query(ThreatAlert).count()
            
            # Threats by level
            threat_levels = db.query(
                ThreatAlert.threat_level,
                func.count(ThreatAlert.id)
            ).group_by(ThreatAlert.threat_level).all()
            
            # Threats by type
            attack_types = db.query(
                ThreatAlert.attack_type,
                func.count(ThreatAlert.id)
            ).group_by(ThreatAlert.attack_type).all()
            
            # Recent threats (last 24 hours)
            yesterday = datetime.now() - timedelta(hours=24)
            recent_threats = db.query(ThreatAlert)\
                              .filter(ThreatAlert.timestamp >= yesterday)\
                              .count()
            
            # PCAP files count
            pcap_count = db.query(PcapFile).count()
            
            # Total storage used
            total_storage = db.query(func.sum(PcapFile.file_size)).scalar() or 0
            
            db.close()
            
            return {
                "total_threats": total_threats,
                "recent_threats_24h": recent_threats,
                "threat_levels": dict(threat_levels),
                "attack_types": dict(attack_types),
                "pcap_files_count": pcap_count,
                "total_storage_bytes": total_storage,
                "storage_path": self.pcap_storage_path
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting threat statistics: {e}")
            return {}
    
    async def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old threat data and PCAP files"""
        try:
            db = self.get_db_session()
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Get old PCAP files to delete
            old_pcap_files = db.query(PcapFile)\
                              .filter(PcapFile.created_at < cutoff_date)\
                              .all()
            
            # Delete physical PCAP files
            for pcap_file in old_pcap_files:
                try:
                    if os.path.exists(pcap_file.file_path):
                        os.remove(pcap_file.file_path)
                    if pcap_file.compressed_path and os.path.exists(pcap_file.compressed_path):
                        os.remove(pcap_file.compressed_path)
                except Exception as e:
                    logger.warning(f"Could not delete PCAP file {pcap_file.file_path}: {e}")
            
            # Delete database records
            deleted_pcap = db.query(PcapFile)\
                            .filter(PcapFile.created_at < cutoff_date)\
                            .delete()
            
            deleted_threats = db.query(ThreatAlert)\
                               .filter(ThreatAlert.timestamp < cutoff_date)\
                               .delete()
            
            db.commit()
            db.close()
            
            logger.info(f"✅ Cleanup completed: {deleted_threats} threats, {deleted_pcap} PCAP files deleted")
            
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
    
    async def compress_old_pcap_files(self, days_old: int = 7):
        """Compress PCAP files older than specified days"""
        try:
            db = self.get_db_session()
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            old_files = db.query(PcapFile)\
                         .filter(PcapFile.created_at < cutoff_date)\
                         .filter(PcapFile.compressed == False)\
                         .all()
            
            for pcap_file in old_files:
                try:
                    if os.path.exists(pcap_file.file_path):
                        compressed_path = pcap_file.file_path + ".gz"
                        
                        with open(pcap_file.file_path, 'rb') as f_in:
                            with gzip.open(compressed_path, 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                        
                        # Update database record
                        pcap_file.compressed = True
                        pcap_file.compressed_path = compressed_path
                        
                        # Remove original file
                        os.remove(pcap_file.file_path)
                        
                        logger.info(f"✅ Compressed PCAP file: {pcap_file.filename}")
                
                except Exception as e:
                    logger.warning(f"Could not compress PCAP file {pcap_file.file_path}: {e}")
            
            db.commit()
            db.close()
            
        except Exception as e:
            logger.error(f"❌ Error compressing PCAP files: {e}")
    
    async def execute_custom_query(self, query: str) -> Dict[str, Any]:
        """Execute custom SQL query and return results"""
        try:
            db = self.get_db_session()
            
            # Execute the query
            result = db.execute(text(query))
            
            # Get column names
            columns = list(result.keys()) if result.keys() else []
            
            # Get all rows
            rows = [list(row) for row in result.fetchall()]
            
            db.close()
            
            return {
                "columns": columns,
                "rows": rows
            }
            
        except Exception as e:
            logger.error(f"❌ Error executing custom query: {e}")
            raise e
    
    async def execute_query(self, query: str, params: List[Any] = None) -> List[tuple]:
        """Execute parameterized SQL query and return raw results"""
        try:
            db = self.get_db_session()
            
            # Convert PostgreSQL-style parameters ($1, $2) to SQLAlchemy style (:param1, :param2)
            if params:
                # Replace $1, $2, etc. with :param1, :param2, etc.
                converted_query = query
                param_dict = {}
                for i, param in enumerate(params, 1):
                    converted_query = converted_query.replace(f'${i}', f':param{i}')
                    param_dict[f'param{i}'] = param
                
                result = db.execute(text(converted_query), param_dict)
            else:
                result = db.execute(text(query))
            
            # Get all rows as tuples
            rows = result.fetchall()
            
            db.close()
            
            return rows
            
        except Exception as e:
            logger.error(f"❌ Error executing parameterized query: {e}")
            db.rollback()
            raise e

# Global database service instance
database_service = DatabaseService()
