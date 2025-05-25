from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
import sys
from contextlib import asynccontextmanager
from sqlalchemy import inspect
import asyncio

from app.database import engine, Base, get_db, SessionLocal
from app.api import router as api_router
from app.api.guilds import get_guilds, _execute_guild_update_logic, GUILD_IDS, guild_update_locks, guild_update_in_progress
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

async def warm_individual_guild(guild_id: str):
    """Warms a single guild, ensuring the update is attempted by acquiring the lock."""
    lock = guild_update_locks[guild_id]
    
    logger.info(f"Warmup: Attempting to acquire lock for guild {guild_id} for initial data population.")
    # Using 'async with lock' ensures the lock is acquired (blocking) and released properly.
    # This will make the task wait if the lock is somehow already held, ensuring the update is attempted.
    async with lock:
        logger.info(f"Warmup: Acquired lock for guild {guild_id}. Starting data update (force_refresh_logs=True).")
        
        # Mark as in progress for the duration of this locked operation.
        guild_update_in_progress[guild_id] = True
        
        db_session: SessionLocal = SessionLocal()
        try:
            # force_refresh_logs=True is crucial for the initial population as requested.
            await _execute_guild_update_logic(guild_id, db_session, force_refresh_logs=True)
            logger.info(f"Warmup: Successfully updated data for guild {guild_id}.")
        except Exception as e:
            # Log detailed error to help diagnose issues with data population.
            logger.error(f"Warmup: Error updating guild {guild_id} during initial population: {str(e)}", exc_info=True)
            # Depending on policy, one might want to re-raise to halt startup if a guild fails.
            # For now, it logs the error and continues with other guilds, aligning with current gather behavior.
        finally:
            if db_session: # Ensure session is closed regardless of outcome
                db_session.close()
            # Reset the progress flag after the operation.
            guild_update_in_progress[guild_id] = False
            # Lock is automatically released by 'async with' context exit.
            logger.info(f"Warmup: Lock for guild {guild_id} released after initial population attempt.")

async def warm_database():
    """Pre-fetch guild data on startup by updating each guild sequentially by lock, but tasks gathered."""
    logger.info("Warming up database with initial guild data...")
    
    # Create tasks for each guild to warm them up, potentially concurrently
    # but respecting individual guild locks via warm_individual_guild
    tasks = [warm_individual_guild(guild_id) for guild_id in GUILD_IDS]
    await asyncio.gather(*tasks, return_exceptions=True) # return_exceptions to see all errors if any
    
    logger.info("Database warmup process completed.")

@asynccontextmanager
async def lifespan(app: FastAPI):
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

