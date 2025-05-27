from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Use /app/data for the database file
DATA_DIR = "/app/data"
DB_FILE = os.path.join(DATA_DIR, "guild.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_FILE}"

logger.info(f"Database URL: {SQLALCHEMY_DATABASE_URL}")

try:
    # Ensure the data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    logger.info(f"Using data directory: {os.path.abspath(DATA_DIR)}")

    # Create SQLite engine with better configuration for concurrent access
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={
            "check_same_thread": False,
            "timeout": 30.0  # 30 second timeout for locks
        },
        pool_pre_ping=True,  # Verify connections before using them
        pool_size=5,  # Connection pool size
        max_overflow=10  # Maximum overflow connections
    )

    # Enable WAL mode for better concurrent access
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=30000")  # 30 second timeout
        cursor.execute("PRAGMA synchronous=NORMAL")  # Better performance
        cursor.close()

    # Create SessionLocal class
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create Base class
    Base = declarative_base()
except Exception as e:
    logger.error(f"Error initializing database: {e}")
    raise

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 