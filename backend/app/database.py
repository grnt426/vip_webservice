from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Use a relative path that works both in development and in container
DUMPS_DIR = "dumps"
DB_FILE = os.path.join(DUMPS_DIR, "guild.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///./{DB_FILE}"

logger.info(f"Database URL: {SQLALCHEMY_DATABASE_URL}")

try:
    # Ensure the dumps directory exists
    os.makedirs(DUMPS_DIR, exist_ok=True)
    logger.info(f"Using dumps directory: {os.path.abspath(DUMPS_DIR)}")

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