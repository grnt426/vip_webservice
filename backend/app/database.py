from sqlalchemy import create_engine
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

    # Create SQLite engine
    # check_same_thread is needed for SQLite specifically
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )

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