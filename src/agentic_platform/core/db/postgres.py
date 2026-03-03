import os
import boto3
from sqlalchemy import Engine, create_engine, event
import urllib.parse
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, Dict, Any
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
# Initialize logging if not already done
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

class EnvironmentType(Enum):
    """Environment types for database connections"""
    LOCAL = "local"
    DEVELOPMENT = "dev"
    STAGING = "staging" 
    PRODUCTION = "prod"
    
    @classmethod
    def from_string(cls, value: str) -> 'EnvironmentType':
        """Convert string to enum value with fallback to LOCAL"""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.LOCAL

class EngineType(Enum):
    """Defines the type of database engine connection"""
    WRITER = "writer"
    READER = "reader"

@dataclass
class DatabaseConfig:
    """Configuration for database connections"""
    environment: EnvironmentType
    database: str
    
    # Local development config
    local_host: Optional[str] = None
    writer_user: Optional[str] = None
    reader_user: Optional[str] = None
    writer_password: Optional[str] = None
    reader_password: Optional[str] = None
    
    # Production config (Aurora)
    writer_endpoint: Optional[str] = None
    reader_endpoint: Optional[str] = None
    
    # Connection pool settings
    pool_size: int = 10
    max_overflow: int = 15
    pool_recycle: int = 300
    token_refresh_seconds: int = 290  # For IAM auth (tokens expire in 15 min)

    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.database:
            raise ValueError("PG_DATABASE must be set")
            
        if self.environment == EnvironmentType.LOCAL:
            required = {
                "PG_CONNECTION_URL": self.local_host,
                "PG_USER": self.writer_user,
                "PG_READ_ONLY_USER": self.reader_user,
                "PG_PASSWORD": self.writer_password,
                "PG_READ_ONLY_PASSWORD": self.reader_password
            }
        else:
            required = {
                "PG_WRITER_ENDPOINT": self.writer_endpoint,
                "PG_READER_ENDPOINT": self.reader_endpoint,
                "PG_USER": self.writer_user,
                "PG_READ_ONLY_USER": self.reader_user
            }
            
        missing = [k for k, v in required.items() if not v]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

class PostgresDB:
    """Manages PostgreSQL database connections with IAM authentication for Aurora"""
    
    # Standard PostgreSQL connection settings
    _DEFAULT_CONNECT_ARGS = {
        "connect_timeout": 10,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5
    }
    
    def __init__(self, config: Optional[DatabaseConfig] = None, rds_client = None):
        """Initialize database connection engines with optional dependency injection"""
        self.config = config or self._load_config()
        self.rds_client = rds_client or boto3.client("rds")
        self.write_engine = self._create_engine(EngineType.WRITER)
        self.read_engine = self._create_engine(EngineType.READER)
    
    def _load_config(self) -> DatabaseConfig:
        """Load database configuration from environment variables"""
        env_str = os.environ.get("ENVIRONMENT", "local")
        environment = EnvironmentType.from_string(env_str)
        
        return DatabaseConfig(
            environment=environment,
            database=os.environ.get("PG_DATABASE", ""),
            local_host=os.environ.get("PG_CONNECTION_URL"),
            writer_user=os.environ.get("PG_USER"),
            reader_user=os.environ.get("PG_READ_ONLY_USER"),
            writer_password=os.environ.get("PG_PASSWORD"),
            reader_password=os.environ.get("PG_READ_ONLY_PASSWORD"),
            writer_endpoint=os.environ.get("PG_WRITER_ENDPOINT"),
            reader_endpoint=os.environ.get("PG_READER_ENDPOINT"),
            pool_size=int(os.environ.get("PG_POOL_SIZE", "10")),
            max_overflow=int(os.environ.get("PG_MAX_OVERFLOW", "15")),
            pool_recycle=int(os.environ.get("PG_POOL_RECYCLE", "300")),
        )
    
    def _create_engine(self, engine_type: EngineType) -> Engine:
        """Create SQLAlchemy engine based on environment and engine type"""
        is_writer = engine_type == EngineType.WRITER
        
        # Determine connection parameters based on environment and engine type
        if self.config.environment == EnvironmentType.LOCAL:
            logger.info("Using local env database connection")
            return self._create_local_engine(is_writer)
        else:
            logger.info("Using aurora IAM database connection")
            return self._create_aurora_engine(is_writer)

    def _create_local_engine(self, is_writer: bool) -> Engine:
        """Create engine for local development using password authentication"""
        user = self.config.writer_user if is_writer else self.config.reader_user
        password = self.config.writer_password if is_writer else self.config.reader_password
        
        connection_string = f"postgresql://{user}:{urllib.parse.quote(password)}@{self.config.local_host}/{self.config.database}"
        
        return create_engine(
            connection_string,
            pool_size=self.config.pool_size,
            max_overflow=self.config.max_overflow,
            pool_pre_ping=True,
            pool_recycle=self.config.pool_recycle,
            connect_args=self._DEFAULT_CONNECT_ARGS
        )
    
    def _create_aurora_engine(self, is_writer: bool) -> Engine:
        """Create engine for Aurora using IAM authentication with do_connect event"""
        user = self.config.writer_user if is_writer else self.config.reader_user
        host = self.config.writer_endpoint if is_writer else self.config.reader_endpoint
        
        try:
            # Create engine with minimal connection string - parameters set by event
            engine = create_engine(
                "postgresql:///",  # Empty connection string
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_pre_ping=True,
                pool_recycle=self.config.token_refresh_seconds,
                connect_args=self._DEFAULT_CONNECT_ARGS
            )
            
            # Event listener to provide fresh connection parameters including token
            @event.listens_for(engine, "do_connect")
            def provide_token(dialect, conn_rec, cargs, cparams):
                # Generate fresh token for each connection
                token = self._get_iam_token(user, host)
                
                # Set all connection parameters
                cparams['host'] = host
                cparams['port'] = 5432
                cparams['user'] = user
                cparams['password'] = token
                cparams['database'] = self.config.database
                cparams['sslmode'] = 'require'
            
            return engine
            
        except Exception as e:
            raise RuntimeError(f"Failed to create Aurora database engine: {str(e)}") from e
    
    def _get_iam_token(self, username: str, hostname: str) -> str:
        """Generate an IAM authentication token for Aurora PostgreSQL"""
        try:
            return self.rds_client.generate_db_auth_token(
                DBHostname=hostname,
                Port=5432,
                DBUsername=username
            )
        except Exception as e:
            raise RuntimeError(f"Failed to generate IAM token: {str(e)}") from e

    def get_write_engine(self) -> Engine:
        """Get the database engine for write operations"""
        return self.write_engine
    
    def get_read_engine(self) -> Engine:
        """Get the database engine for read operations"""
        return self.read_engine
        
    def healthcheck(self) -> Dict[str, Any]:
        """Perform a health check on both database connections"""
        result = {"status": "ok", "writer": {}, "reader": {}}
        
        try:
            # Check writer connection
            with self.write_engine.connect() as conn:
                version = conn.execute("SELECT version()").scalar()
                result["writer"] = {"connected": True, "version": version}
        except Exception as e:
            result["writer"] = {"connected": False, "error": str(e)}
            result["status"] = "error"
            
        try:
            # Check reader connection
            with self.read_engine.connect() as conn:
                version = conn.execute("SELECT version()").scalar()
                result["reader"] = {"connected": True, "version": version}
        except Exception as e:
            result["reader"] = {"connected": False, "error": str(e)}
            result["status"] = "error"
            
        return result

# Create singleton instance
db = PostgresDB()
write_postgres_db = db.get_write_engine()
read_postgres_db = db.get_read_engine()
