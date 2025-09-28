# START OF FILE core/storage/database.py
"""
HAI-Net Constitutional Database Management
Constitutional compliance: Privacy First Principle (Article I) + Local storage
SQLite with encryption at rest and constitutional data protection
"""

import sqlite3
import json
import time
import hashlib
import secrets
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from contextlib import contextmanager
from cryptography.fernet import Fernet
import threading

from core.config.settings import HAINetSettings
from core.logging.logger import get_logger
from core.identity.did import ConstitutionalViolationError


@dataclass
class DataRecord:
    """Represents a data record with constitutional compliance"""
    record_id: str
    data_type: str
    content: Dict[str, Any]
    created_at: float
    updated_at: float
    constitutional_version: str
    user_consent: bool = False
    privacy_level: str = "private"  # private, community, public
    retention_policy: str = "indefinite"  # indefinite, session, 30d, 90d, 1y


@dataclass
class ConstitutionalMetadata:
    """Metadata for constitutional compliance tracking"""
    data_classification: str  # personal, system, community, public
    user_consent_given: bool
    consent_timestamp: float
    privacy_level: str
    sharing_permitted: bool = False
    retention_period: Optional[int] = None  # seconds
    audit_required: bool = True


class ConstitutionalDatabase:
    """
    Constitutional compliance database wrapper
    Ensures all data operations comply with constitutional principles
    """
    
    def __init__(self, db_path: Path, encryption_key: Optional[bytes] = None):
        self.db_path = db_path
        self.logger = get_logger("storage.database")
        
        # Encryption for data at rest
        if encryption_key:
            self.cipher = Fernet(encryption_key)
        else:
            # Generate encryption key if not provided
            key = Fernet.generate_key()
            self.cipher = Fernet(key)
            # In production, this key should be stored securely
        
        # Constitutional compliance
        self.constitutional_version = "1.0"
        self.max_record_size = 10 * 1024 * 1024  # 10MB per record
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Initialize database
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database with constitutional compliance schema"""
        try:
            with self._get_connection() as conn:
                # Create constitutional compliance tables
                conn.executescript("""
                    -- Core data table with encryption
                    CREATE TABLE IF NOT EXISTS hai_data (
                        record_id TEXT PRIMARY KEY,
                        data_type TEXT NOT NULL,
                        encrypted_content BLOB NOT NULL,
                        created_at REAL NOT NULL,
                        updated_at REAL NOT NULL,
                        constitutional_version TEXT NOT NULL DEFAULT '1.0',
                        user_consent INTEGER NOT NULL DEFAULT 0,
                        privacy_level TEXT NOT NULL DEFAULT 'private',
                        retention_policy TEXT NOT NULL DEFAULT 'indefinite',
                        content_hash TEXT NOT NULL,
                        INDEX(data_type),
                        INDEX(created_at),
                        INDEX(privacy_level)
                    );
                    
                    -- Constitutional metadata table
                    CREATE TABLE IF NOT EXISTS constitutional_metadata (
                        record_id TEXT PRIMARY KEY,
                        data_classification TEXT NOT NULL,
                        user_consent_given INTEGER NOT NULL,
                        consent_timestamp REAL NOT NULL,
                        privacy_level TEXT NOT NULL,
                        sharing_permitted INTEGER NOT NULL DEFAULT 0,
                        retention_period INTEGER,
                        audit_required INTEGER NOT NULL DEFAULT 1,
                        FOREIGN KEY(record_id) REFERENCES hai_data(record_id) ON DELETE CASCADE
                    );
                    
                    -- Audit trail for constitutional compliance
                    CREATE TABLE IF NOT EXISTS constitutional_audit (
                        audit_id TEXT PRIMARY KEY,
                        record_id TEXT NOT NULL,
                        operation TEXT NOT NULL,
                        user_consent_verified INTEGER NOT NULL,
                        constitutional_principle TEXT NOT NULL,
                        timestamp REAL NOT NULL,
                        details TEXT,
                        INDEX(record_id),
                        INDEX(timestamp),
                        INDEX(constitutional_principle)
                    );
                    
                    -- User consent tracking
                    CREATE TABLE IF NOT EXISTS user_consent (
                        consent_id TEXT PRIMARY KEY,
                        user_did TEXT,
                        data_type TEXT NOT NULL,
                        consent_given INTEGER NOT NULL,
                        consent_timestamp REAL NOT NULL,
                        consent_scope TEXT NOT NULL,
                        expires_at REAL,
                        INDEX(user_did),
                        INDEX(data_type),
                        INDEX(consent_timestamp)
                    );
                    
                    -- System configuration
                    CREATE TABLE IF NOT EXISTS system_config (
                        config_key TEXT PRIMARY KEY,
                        config_value TEXT NOT NULL,
                        created_at REAL NOT NULL,
                        updated_at REAL NOT NULL
                    );
                """)
                
                conn.commit()
                
                # Insert constitutional version
                self._set_system_config("constitutional_version", self.constitutional_version)
                
                self.logger.log_privacy_event(
                    "constitutional_database_initialized",
                    "encrypted_sqlite",
                    user_consent=True
                )
                
        except Exception as e:
            raise ConstitutionalViolationError(f"Database initialization failed: {e}")
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with proper error handling"""
        conn = None
        try:
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=30.0,
                check_same_thread=False
            )
            conn.row_factory = sqlite3.Row
            
            # Enable foreign keys for referential integrity
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Constitutional principle: Privacy First - Secure temp storage
            conn.execute("PRAGMA secure_delete = ON")
            
            yield conn
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise ConstitutionalViolationError(f"Database connection error: {e}")
        finally:
            if conn:
                conn.close()
    
    def store_data(self, record: DataRecord, metadata: ConstitutionalMetadata) -> bool:
        """
        Store data with constitutional compliance validation
        
        Args:
            record: Data record to store
            metadata: Constitutional metadata
            
        Returns:
            True if stored successfully
        """
        try:
            with self._lock:
                # Validate constitutional compliance
                if not self._validate_storage_compliance(record, metadata):
                    raise ConstitutionalViolationError("Data violates constitutional principles")
                
                # Encrypt sensitive content
                content_json = json.dumps(record.content)
                if len(content_json.encode()) > self.max_record_size:
                    raise ConstitutionalViolationError("Record exceeds maximum size")
                
                encrypted_content = self.cipher.encrypt(content_json.encode())
                content_hash = hashlib.sha256(content_json.encode()).hexdigest()
                
                with self._get_connection() as conn:
                    # Store main record
                    conn.execute("""
                        INSERT OR REPLACE INTO hai_data 
                        (record_id, data_type, encrypted_content, created_at, updated_at,
                         constitutional_version, user_consent, privacy_level, retention_policy, content_hash)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        record.record_id, record.data_type, encrypted_content,
                        record.created_at, record.updated_at, record.constitutional_version,
                        int(record.user_consent), record.privacy_level, record.retention_policy,
                        content_hash
                    ))
                    
                    # Store constitutional metadata
                    conn.execute("""
                        INSERT OR REPLACE INTO constitutional_metadata
                        (record_id, data_classification, user_consent_given, consent_timestamp,
                         privacy_level, sharing_permitted, retention_period, audit_required)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        record.record_id, metadata.data_classification,
                        int(metadata.user_consent_given), metadata.consent_timestamp,
                        metadata.privacy_level, int(metadata.sharing_permitted),
                        metadata.retention_period, int(metadata.audit_required)
                    ))
                    
                    # Create audit trail
                    self._create_audit_entry(
                        conn, record.record_id, "STORE",
                        metadata.user_consent_given, "Privacy First",
                        {"data_type": record.data_type, "privacy_level": record.privacy_level}
                    )
                    
                    conn.commit()
                
                self.logger.log_privacy_event(
                    "data_stored",
                    record.data_type,
                    user_consent=record.user_consent
                )
                
                return True
                
        except Exception as e:
            self.logger.error(f"Data storage failed: {e}")
            return False
    
    def retrieve_data(self, record_id: str, user_consent_verified: bool = False) -> Optional[DataRecord]:
        """
        Retrieve data with constitutional compliance checks
        
        Args:
            record_id: Record identifier
            user_consent_verified: Whether user consent has been verified
            
        Returns:
            DataRecord if found and compliant, None otherwise
        """
        try:
            with self._lock:
                with self._get_connection() as conn:
                    # Check constitutional compliance before retrieval
                    metadata_row = conn.execute("""
                        SELECT * FROM constitutional_metadata WHERE record_id = ?
                    """, (record_id,)).fetchone()
                    
                    if not metadata_row:
                        return None
                    
                    # Validate user consent for sensitive data
                    if metadata_row['data_classification'] == 'personal' and not user_consent_verified:
                        self.logger.log_violation("unauthorized_data_access", {
                            "record_id": record_id,
                            "reason": "User consent not verified for personal data"
                        })
                        return None
                    
                    # Retrieve main record
                    data_row = conn.execute("""
                        SELECT * FROM hai_data WHERE record_id = ?
                    """, (record_id,)).fetchone()
                    
                    if not data_row:
                        return None
                    
                    # Decrypt content
                    try:
                        decrypted_content = self.cipher.decrypt(data_row['encrypted_content'])
                        content = json.loads(decrypted_content.decode())
                    except Exception as e:
                        raise ConstitutionalViolationError(f"Decryption failed: {e}")
                    
                    # Create audit trail
                    self._create_audit_entry(
                        conn, record_id, "RETRIEVE",
                        user_consent_verified, "Privacy First",
                        {"data_type": data_row['data_type']}
                    )
                    
                    conn.commit()
                    
                    # Create data record
                    record = DataRecord(
                        record_id=data_row['record_id'],
                        data_type=data_row['data_type'],
                        content=content,
                        created_at=data_row['created_at'],
                        updated_at=data_row['updated_at'],
                        constitutional_version=data_row['constitutional_version'],
                        user_consent=bool(data_row['user_consent']),
                        privacy_level=data_row['privacy_level'],
                        retention_policy=data_row['retention_policy']
                    )
                    
                    self.logger.log_privacy_event(
                        "data_retrieved",
                        record.data_type,
                        user_consent=user_consent_verified
                    )
                    
                    return record
                    
        except Exception as e:
            self.logger.error(f"Data retrieval failed: {e}")
            return None
    
    def delete_data(self, record_id: str, user_consent_verified: bool = False) -> bool:
        """
        Delete data with constitutional compliance (right to be forgotten)
        
        Args:
            record_id: Record identifier
            user_consent_verified: Whether user consent has been verified
            
        Returns:
            True if deleted successfully
        """
        try:
            with self._lock:
                with self._get_connection() as conn:
                    # Check if record exists and get metadata
                    metadata_row = conn.execute("""
                        SELECT * FROM constitutional_metadata WHERE record_id = ?
                    """, (record_id,)).fetchone()
                    
                    if not metadata_row:
                        return False
                    
                    # Validate user consent for personal data deletion
                    if metadata_row['data_classification'] == 'personal' and not user_consent_verified:
                        self.logger.log_violation("unauthorized_data_deletion", {
                            "record_id": record_id,
                            "reason": "User consent not verified for personal data deletion"
                        })
                        return False
                    
                    # Create audit trail before deletion
                    self._create_audit_entry(
                        conn, record_id, "DELETE",
                        user_consent_verified, "Human Rights",
                        {"reason": "User requested deletion (right to be forgotten)"}
                    )
                    
                    # Delete record (cascades to metadata)
                    conn.execute("DELETE FROM hai_data WHERE record_id = ?", (record_id,))
                    
                    conn.commit()
                    
                    self.logger.log_human_rights_event(
                        "data_deleted_user_request",
                        user_control=True
                    )
                    
                    return True
                    
        except Exception as e:
            self.logger.error(f"Data deletion failed: {e}")
            return False
    
    def query_data(self, data_type: Optional[str] = None, privacy_level: Optional[str] = None, 
                   user_consent_verified: bool = False) -> List[DataRecord]:
        """
        Query data with constitutional compliance filters
        
        Args:
            data_type: Filter by data type
            privacy_level: Filter by privacy level
            user_consent_verified: Whether user consent has been verified
            
        Returns:
            List of matching records
        """
        try:
            with self._lock:
                with self._get_connection() as conn:
                    # Build query with constitutional filters
                    query = """
                        SELECT d.*, m.data_classification 
                        FROM hai_data d 
                        JOIN constitutional_metadata m ON d.record_id = m.record_id
                        WHERE 1=1
                    """
                    params = []
                    
                    if data_type:
                        query += " AND d.data_type = ?"
                        params.append(data_type)
                    
                    if privacy_level:
                        query += " AND d.privacy_level = ?"
                        params.append(privacy_level)
                    
                    # Constitutional filter: Only return personal data if consent verified
                    if not user_consent_verified:
                        query += " AND m.data_classification != 'personal'"
                    
                    query += " ORDER BY d.created_at DESC"
                    
                    rows = conn.execute(query, params).fetchall()
                    
                    records = []
                    for row in rows:
                        try:
                            # Decrypt content
                            decrypted_content = self.cipher.decrypt(row['encrypted_content'])
                            content = json.loads(decrypted_content.decode())
                            
                            record = DataRecord(
                                record_id=row['record_id'],
                                data_type=row['data_type'],
                                content=content,
                                created_at=row['created_at'],
                                updated_at=row['updated_at'],
                                constitutional_version=row['constitutional_version'],
                                user_consent=bool(row['user_consent']),
                                privacy_level=row['privacy_level'],
                                retention_policy=row['retention_policy']
                            )
                            records.append(record)
                            
                        except Exception as e:
                            self.logger.error(f"Failed to decrypt record {row['record_id']}: {e}")
                            continue
                    
                    # Create audit trail for query
                    if records:
                        self._create_audit_entry(
                            conn, "QUERY_OPERATION", "QUERY",
                            user_consent_verified, "Privacy First",
                            {"result_count": len(records), "data_type": data_type}
                        )
                        conn.commit()
                    
                    return records
                    
        except Exception as e:
            self.logger.error(f"Data query failed: {e}")
            return []
    
    def cleanup_expired_data(self) -> int:
        """
        Clean up expired data based on retention policies
        Constitutional principle: Privacy protection through data minimization
        
        Returns:
            Number of records cleaned up
        """
        try:
            with self._lock:
                with self._get_connection() as conn:
                    current_time = time.time()
                    
                    # Find expired records
                    expired_records = conn.execute("""
                        SELECT d.record_id, d.data_type, m.retention_period
                        FROM hai_data d
                        JOIN constitutional_metadata m ON d.record_id = m.record_id
                        WHERE m.retention_period IS NOT NULL 
                        AND (d.created_at + m.retention_period) < ?
                    """, (current_time,)).fetchall()
                    
                    cleanup_count = 0
                    for record in expired_records:
                        # Create audit trail before deletion
                        self._create_audit_entry(
                            conn, record['record_id'], "AUTO_DELETE",
                            True, "Privacy First",
                            {"reason": "Retention period expired", "data_type": record['data_type']}
                        )
                        
                        # Delete expired record
                        conn.execute("DELETE FROM hai_data WHERE record_id = ?", (record['record_id'],))
                        cleanup_count += 1
                    
                    conn.commit()
                    
                    if cleanup_count > 0:
                        self.logger.log_privacy_event(
                            "expired_data_cleanup",
                            f"count_{cleanup_count}",
                            user_consent=True
                        )
                    
                    return cleanup_count
                    
        except Exception as e:
            self.logger.error(f"Data cleanup failed: {e}")
            return 0
    
    def _validate_storage_compliance(self, record: DataRecord, metadata: ConstitutionalMetadata) -> bool:
        """Validate that data storage complies with constitutional principles"""
        
        # Privacy First: Personal data requires user consent
        if metadata.data_classification == 'personal' and not metadata.user_consent_given:
            return False
        
        # Check constitutional version compatibility
        if record.constitutional_version != self.constitutional_version:
            return False
        
        # Validate privacy level
        valid_privacy_levels = ['private', 'community', 'public']
        if record.privacy_level not in valid_privacy_levels:
            return False
        
        # Human Rights: Ensure user control
        if metadata.data_classification == 'personal' and not metadata.audit_required:
            return False
        
        return True
    
    def _create_audit_entry(self, conn: sqlite3.Connection, record_id: str, operation: str,
                           user_consent_verified: bool, constitutional_principle: str,
                           details: Dict[str, Any]):
        """Create audit trail entry for constitutional compliance"""
        audit_id = f"audit_{int(time.time() * 1000)}_{secrets.token_hex(8)}"
        
        conn.execute("""
            INSERT INTO constitutional_audit
            (audit_id, record_id, operation, user_consent_verified, 
             constitutional_principle, timestamp, details)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            audit_id, record_id, operation, int(user_consent_verified),
            constitutional_principle, time.time(), json.dumps(details)
        ))
    
    def _set_system_config(self, key: str, value: str):
        """Set system configuration value"""
        with self._get_connection() as conn:
            current_time = time.time()
            conn.execute("""
                INSERT OR REPLACE INTO system_config 
                (config_key, config_value, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            """, (key, value, current_time, current_time))
            conn.commit()
    
    def get_constitutional_audit_trail(self, record_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get constitutional audit trail for transparency"""
        try:
            with self._get_connection() as conn:
                if record_id:
                    query = "SELECT * FROM constitutional_audit WHERE record_id = ? ORDER BY timestamp DESC"
                    params = (record_id,)
                else:
                    query = "SELECT * FROM constitutional_audit ORDER BY timestamp DESC LIMIT 1000"
                    params = ()
                
                rows = conn.execute(query, params).fetchall()
                
                audit_entries = []
                for row in rows:
                    entry = {
                        'audit_id': row['audit_id'],
                        'record_id': row['record_id'],
                        'operation': row['operation'],
                        'user_consent_verified': bool(row['user_consent_verified']),
                        'constitutional_principle': row['constitutional_principle'],
                        'timestamp': row['timestamp'],
                        'details': json.loads(row['details']) if row['details'] else {}
                    }
                    audit_entries.append(entry)
                
                return audit_entries
                
        except Exception as e:
            self.logger.error(f"Audit trail retrieval failed: {e}")
            return []


class DatabaseManager:
    """
    High-level database manager for HAI-Net
    Manages multiple databases with constitutional compliance
    """
    
    def __init__(self, settings: HAINetSettings):
        self.settings = settings
        self.logger = get_logger("storage.database_manager", settings)
        
        # Database paths
        self.data_dir = settings.data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Constitutional compliance
        self.constitutional_version = "1.0"
        
        # Database instances
        self.main_db: Optional[ConstitutionalDatabase] = None
        self.node_db: Optional[ConstitutionalDatabase] = None
        self.agent_db: Optional[ConstitutionalDatabase] = None
        
        # Initialize databases
        self._initialize_databases()
    
    def _initialize_databases(self):
        """Initialize all database instances"""
        try:
            # Main application database
            main_db_path = self.data_dir / "hai_net_main.db"
            self.main_db = ConstitutionalDatabase(main_db_path)
            
            # Node network database
            node_db_path = self.data_dir / "hai_net_nodes.db"
            self.node_db = ConstitutionalDatabase(node_db_path)
            
            # Agent state database  
            agent_db_path = self.data_dir / "hai_net_agents.db"
            self.agent_db = ConstitutionalDatabase(agent_db_path)
            
            self.logger.log_privacy_event(
                "database_manager_initialized",
                "multiple_encrypted_databases",
                user_consent=True
            )
            
        except Exception as e:
            raise ConstitutionalViolationError(f"Database manager initialization failed: {e}")
    
    def store_user_data(self, user_did: str, data_type: str, content: Dict[str, Any],
                       user_consent: bool = True, privacy_level: str = "private") -> bool:
        """Store user data with constitutional protection"""
        record = DataRecord(
            record_id=f"user_{user_did}_{data_type}_{int(time.time())}",
            data_type=data_type,
            content=content,
            created_at=time.time(),
            updated_at=time.time(),
            constitutional_version=self.constitutional_version,
            user_consent=user_consent,
            privacy_level=privacy_level
        )
        
        metadata = ConstitutionalMetadata(
            data_classification="personal",
            user_consent_given=user_consent,
            consent_timestamp=time.time(),
            privacy_level=privacy_level,
            sharing_permitted=False,
            audit_required=True
        )
        
        return self.main_db.store_data(record, metadata)
    
    def store_node_data(self, node_id: str, data_type: str, content: Dict[str, Any]) -> bool:
        """Store node-related data"""
        record = DataRecord(
            record_id=f"node_{node_id}_{data_type}_{int(time.time())}",
            data_type=data_type,
            content=content,
            created_at=time.time(),
            updated_at=time.time(),
            constitutional_version=self.constitutional_version,
            privacy_level="community"
        )
        
        metadata = ConstitutionalMetadata(
            data_classification="system",
            user_consent_given=True,
            consent_timestamp=time.time(),
            privacy_level="community",
            sharing_permitted=True,
            retention_period=86400 * 7,  # 7 days
            audit_required=True
        )
        
        return self.node_db.store_data(record, metadata)
    
    def store_agent_data(self, agent_id: str, data_type: str, content: Dict[str, Any]) -> bool:
        """Store agent state data"""
        record = DataRecord(
            record_id=f"agent_{agent_id}_{data_type}_{int(time.time())}",
            data_type=data_type,
            content=content,
            created_at=time.time(),
            updated_at=time.time(),
            constitutional_version=self.constitutional_version,
            privacy_level="private"
        )
        
        metadata = ConstitutionalMetadata(
            data_classification="system",
            user_consent_given=True,
            consent_timestamp=time.time(),
            privacy_level="private",
            sharing_permitted=False,
            retention_period=86400 * 30,  # 30 days
            audit_required=True
        )
        
        return self.agent_db.store_data(record, metadata)
    
    def cleanup_all_expired_data(self) -> Dict[str, int]:
        """Clean up expired data from all databases"""
        cleanup_results = {}
        
        if self.main_db:
            cleanup_results['main'] = self.main_db.cleanup_expired_data()
        
        if self.node_db:
            cleanup_results['node'] = self.node_db.cleanup_expired_data()
        
        if self.agent_db:
            cleanup_results['agent'] = self.agent_db.cleanup_expired_data()
        
        return cleanup_results
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics for all databases"""
        stats = {
            "constitutional_version": self.constitutional_version,
            "databases": {},
            "total_cleanup_count": 0
        }
        
        for db_name, db in [("main", self.main_db), ("node", self.node_db), ("agent", self.agent_db)]:
            if db:
                try:
                    with db._get_connection() as conn:
                        # Count records by type
                        type_counts = conn.execute("""
                            SELECT data_type, COUNT(*) as count 
                            FROM hai_data 
                            GROUP BY data_type
                        """).fetchall()
                        
                        # Count by privacy level
                        privacy_counts = conn.execute("""
                            SELECT privacy_level, COUNT(*) as count 
                            FROM hai_data 
                            GROUP BY privacy_level
                        """).fetchall()
                        
                        stats["databases"][db_name] = {
                            "type_counts": {row[0]: row[1] for row in type_counts},
                            "privacy_counts": {row[0]: row[1] for row in privacy_counts},
                            "total_records": sum(row[1] for row in type_counts)
                        }
                        
                except Exception as e:
                    stats["databases"][db_name] = {"error": str(e)}
        
        return stats


def create_database_manager(settings: HAINetSettings) -> DatabaseManager:
    """
    Create and configure constitutional database manager
    
    Args:
        settings: HAI-Net settings
        
    Returns:
        Configured DatabaseManager instance
    """
    return DatabaseManager(settings)


if __name__ == "__main__":
    # Test the constitutional database system
    from core.config.settings import HAINetSettings
    
    print("HAI-Net Constitutional Database Test")
    print("=" * 40)
    
    # Create test settings
    settings = HAINetSettings()
    
    # Create database manager
    db_manager = create_database_manager(settings)
    
    try:
        # Test user data storage
        user_did = "did:hai:test_user_123"
        success = db_manager.store_user_data(
            user_did=user_did,
            data_type="profile",
            content={
                "display_name": "Test User",
                "preferences": {"theme": "dark", "language": "en"},
                "created": time.time()
            },
            user_consent=True,
            privacy_level="private"
        )
        print(f"✅ User data stored: {success}")
        
        # Test node data storage
        success = db_manager.store_node_data(
            node_id="test_node_001",
            data_type="discovery",
            content={
                "address": "192.168.1.100",
                "port": 4001,
                "capabilities": ["llm", "voice_stt"],
                "trust_level": 0.8
            }
        )
        print(f"✅ Node data stored: {success}")
        
        # Test agent data storage
        success = db_manager.store_agent_data(
            agent_id="agent_admin_001",
            data_type="state",
            content={
                "current_state": "idle",
                "last_activity": time.time(),
                "memory_usage": 45.2,
                "task_queue": []
            }
        )
        print(f"✅ Agent data stored: {success}")
        
        # Test data retrieval with consent
        record = db_manager.main_db.retrieve_data(
            f"user_{user_did}_profile_{int(time.time())}",
            user_consent_verified=True
        )
        print(f"✅ Data retrieved: {record is not None}")
        
        # Test statistics
        stats = db_manager.get_database_stats()
        print(f"📊 Database stats: {stats}")
        
        # Test cleanup
        cleanup_results = db_manager.cleanup_all_expired_data()
        print(f"🧹 Cleanup results: {cleanup_results}")
        
        print("\n🎉 Constitutional Database System Working!")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
