from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
import sys
from contextlib import asynccontextmanager
from sqlalchemy import inspect

from app.database import engine, Base, get_db
from app.api import router as api_router
from app.api.guilds import get_guilds
from app.models.guild_logs import (
    KickLog, InviteLog, InviteDeclineLog, JoinLog, RankChangeLog,
    StashLog, TreasuryLog, MotdLog, UpgradeLog, InfluenceLog, MissionLog
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Only create tables if they don't exist
inspector = inspect(engine)
existing_tables = inspector.get_table_names()
if not existing_tables:
    logger.info("No tables found in database, creating schema...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema created successfully")
else:
    logger.info(f"Found existing tables: {', '.join(existing_tables)}")

# Verify tables exist
inspector = inspect(engine)
tables = inspector.get_table_names()
logger.info("Database tables found:")
for table in tables:
    logger.info(f"  - {table}")

# Expected log tables
expected_tables = [
    "guild_logs_kick",
    "guild_logs_invite",
    "guild_logs_invite_decline",
    "guild_logs_join",
    "guild_logs_rank_change",
    "guild_logs_stash",
    "guild_logs_treasury",
    "guild_logs_motd",
    "guild_logs_upgrade",
    "guild_logs_influence",
    "guild_logs_mission"
]

missing_tables = [table for table in expected_tables if table not in tables]
if missing_tables:
    logger.error("Missing tables:")
    for table in missing_tables:
        logger.error(f"  - {table}")
    raise Exception("Missing required database tables")

async def warm_database():
    """Pre-fetch guild data on startup"""
    logger.info("Warming up database with initial guild data...")
    try:
        # Get database session
        db = next(get_db())
        # Force refresh all guild data
        await get_guilds(force_refresh=True, db=db)
        logger.info("Successfully warmed up database with guild data")
    except Exception as e:
        logger.error(f"Error warming up database: {str(e)}", exc_info=True)
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm up database on startup
    await warm_database()
    yield

app = FastAPI(lifespan=lifespan)

# Mount static files
app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",  # Backend dev server
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative dev port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include API routes
app.include_router(api_router)

@app.get("/")
async def get():
    return FileResponse("static/index.html")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up FastAPI application")
    logger.info("Database tables created")
    logger.info("API routes configured")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down FastAPI application")

