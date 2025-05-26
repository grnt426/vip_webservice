from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func, or_
from typing import List, Optional, Dict, Callable
from datetime import datetime
import logging
import asyncio

from app.database import get_db, SessionLocal
from app.models.guild import Guild, GuildEmblem
from app.models.guild_logs import (
    BaseGuildLog, KickLog, InviteLog, InviteDeclineLog, JoinLog, RankChangeLog,
    StashLog, TreasuryLog, MotdLog, UpgradeLog, InfluenceLog, MissionLog,
    create_log_entry, LOG_TYPE_MAP
)
from app.models.account import Account
from app.models.guild_membership import GuildMembership, guild_memberships
from app.models.guild_rank import GuildRank
from app.gw2_client import GW2Client
from app.utils.name_utils import get_short_guild_name

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()
gw2_client = GW2Client()

# List of guild IDs to track
GUILD_IDS = [
    "C8260C3D-F677-E711-80D4-E4115BEBA648",  # Power
    "4C345327-7D78-E711-80D4-E4115BEBA648",  # Primal
    "BDEF3AB3-7F78-E711-80DA-101F7433AF15",  # Phoenix
    "11605C96-8578-E711-80DA-101F7433AF15",  # Pain
    "5C59E515-A66D-E811-81A8-83C7278578E0",  # Perfect
    "90EE62DE-B813-EF11-BA1F-12061042B485",  # Pips
]

# For managing concurrent updates to the same guild_id within this instance
guild_update_locks: Dict[str, asyncio.Lock] = {
    guild_id: asyncio.Lock() for guild_id in GUILD_IDS
}
# To track if an update is already scheduled/running to avoid redundant tasks
guild_update_in_progress: Dict[str, bool] = {
    guild_id: False for guild_id in GUILD_IDS
}

# Helper to get a new DB session for background tasks
def get_background_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def _execute_guild_update_logic(
    guild_id: str, 
    db: Session, # Accepts an active DB session
    force_refresh_logs: bool = False
):
    """Core logic to fetch and update data for a single guild."""
    logger.info(f"Executing update logic for guild {guild_id}. Force refresh logs: {force_refresh_logs}")
    try:
        guild = db.query(Guild).filter(Guild.id == guild_id).first()

        current_last_log_id = None
        if guild and not force_refresh_logs:
            current_last_log_id = guild.last_log_id
        
        guild_api_data = await gw2_client.get_guild_data(
            guild_id,
            last_log_id=current_last_log_id
        )

        if not guild_api_data:
            logger.warning(f"Core Logic: No data received for guild {guild_id} from API.")
            return

        with db.begin_nested():
            if not guild:
                guild = Guild(
                    id=guild_api_data["id"],
                    name=guild_api_data["name"],
                    tag=guild_api_data["tag"],
                    level=guild_api_data.get("level", 0),
                    motd=guild_api_data["motd"],
                    influence=guild_api_data["influence"],
                    aetherium=guild_api_data["aetherium"],
                    resonance=guild_api_data["resonance"],
                    favor=guild_api_data["favor"],
                    last_log_id=guild_api_data.get("last_log_id", 0)
                )
                db.add(guild)
                db.flush()
            
            guild.name = guild_api_data["name"]
            guild.tag = guild_api_data["tag"]
            guild.level = guild_api_data.get("level", 0)
            guild.motd = guild_api_data["motd"]
            guild.influence = guild_api_data["influence"]
            guild.aetherium = guild_api_data["aetherium"]
            guild.resonance = guild_api_data["resonance"]
            guild.favor = guild_api_data["favor"]
            guild.last_log_id = guild_api_data.get("last_log_id", guild.last_log_id)
            guild.last_updated = datetime.utcnow()
            db.flush()

            if guild_api_data.get("emblem"):
                emblem_data = guild_api_data["emblem"]
                if not guild.emblem:
                    guild.emblem = GuildEmblem(guild_id=guild.id)
                guild.emblem.background_id = emblem_data["background"]["id"]
                guild.emblem.background_colors = emblem_data["background"]["colors"]
                guild.emblem.foreground_id = emblem_data["foreground"]["id"]
                guild.emblem.foreground_colors = emblem_data["foreground"]["colors"]
                guild.emblem.flags = emblem_data.get("flags", [])
                db.flush()
            
            if guild_api_data.get("logs"):
                new_logs_count = 0
                for log_entry_data in guild_api_data["logs"]:
                    log_type = log_entry_data["type"]
                    if log_type not in LOG_TYPE_MAP:
                        logger.warning(f"Core Logic: Unknown log type: {log_type} for guild {guild_id}")
                        continue
                    log_model_cls = LOG_TYPE_MAP[log_type]
                    existing_log = db.query(log_model_cls).filter_by(guild_id=guild_id, id=log_entry_data["id"]).first()
                    if not existing_log:
                        new_log = create_log_entry(guild_id, log_entry_data)
                        db.add(new_log)
                        new_logs_count += 1
                if new_logs_count > 0:
                    logger.info(f"Core Logic: Added {new_logs_count} new logs for guild {guild_id}")
                db.flush()

            if guild_api_data.get("ranks"):
                existing_ranks = {rank.id: rank for rank in db.query(GuildRank).filter_by(guild_id=guild_id).all()}
                processed_rank_ids = set()
                for rank_data in guild_api_data["ranks"]:
                    rank_id = rank_data["id"]
                    processed_rank_ids.add(rank_id)
                    rank = existing_ranks.get(rank_id)
                    if rank:
                        rank.order = rank_data["order"]
                        rank.permissions = rank_data["permissions"]
                        rank.icon = rank_data.get("icon")
                    else:
                        rank = GuildRank.from_api_response(guild_id, rank_data)
                        db.add(rank)
                for rank_id_to_delete in set(existing_ranks.keys()) - processed_rank_ids:
                    db.delete(existing_ranks[rank_id_to_delete])
                db.flush()

            if guild_api_data.get("members"):
                for member_data in guild_api_data["members"]:
                    # Get or create the account
                    account = Account.get_or_create(db, member_data["name"])
                    # Add or update the guild membership
                    GuildMembership.add_or_update(db, account.id, guild_id, member_data)
                db.flush()
        
        db.commit()
        logger.info(f"Core Logic: Update completed successfully for guild {guild_id}")

    except Exception as e:
        logger.error(f"Core Logic Error for guild {guild_id}: {str(e)}", exc_info=True)
        db.rollback()
        raise # Re-raise the exception so the caller (background task or warm_database) can know

async def _update_guild_data_background(
    guild_id: str, 
    force_refresh_logs: bool = False
):
    """Background task wrapper to fetch and update guild data, managing lock and DB session."""
    lock = guild_update_locks[guild_id]
    if lock.locked():
        logger.info(f"Update for guild {guild_id} is already in progress (lock held), skipping new background task initiation.")
        return

    async with lock:
        logger.info(f"Background task acquired lock for guild {guild_id}. Force refresh logs: {force_refresh_logs}")
        guild_update_in_progress[guild_id] = True
        db_gen = get_background_db_session()
        db: Session = next(db_gen)
        try:
            await _execute_guild_update_logic(guild_id, db, force_refresh_logs)
            logger.info(f"Background task completed successfully for guild {guild_id} via _execute_guild_update_logic.")
        except Exception as e:
            # Logging is already done in _execute_guild_update_logic
            logger.error(f"Background task for guild {guild_id} encountered an error: {str(e)}")
        finally:
            db.close()
            guild_update_in_progress[guild_id] = False
            logger.info(f"Background task finished for guild {guild_id}, lock released.")

@router.get("/guilds")
async def get_guilds(
    background_tasks: BackgroundTasks,
    force_refresh: bool = False, 
    db: Session = Depends(get_db)
):
    """Get all tracked guild data, returning cached data immediately 
       and scheduling background updates if needed."""
    logger.info(f"Processing request for guild data. Force refresh: {force_refresh}")
    guilds_response = []
    
    for guild_id in GUILD_IDS:
        guild = db.query(Guild).options(joinedload(Guild.emblem)).filter(Guild.id == guild_id).first()
        
        if guild:
            guilds_response.append(guild.to_dict())
            logger.info(f"Guild {guild_id} found in cache. Last updated: {guild.last_updated}")
        else:
            logger.info(f"Guild {guild_id} not found in cache. Initial fetch will be in background.")
            # Optionally, add a placeholder or skip for now
            # guilds_response.append({"id": guild_id, "name": "Fetching...", "status": "pending"})

        needs_refresh = not guild or force_refresh or gw2_client.is_data_stale(guild.last_updated if guild else None)

        if needs_refresh:
            if not guild_update_locks[guild_id].locked():
                if not guild_update_in_progress[guild_id]: # Check if already scheduled by another request in this instance
                    logger.info(f"Scheduling background update for guild {guild_id}. Force refresh logs: {force_refresh}")
                    guild_update_in_progress[guild_id] = True # Mark as scheduled/in-progress
                    background_tasks.add_task(
                        _update_guild_data_background, 
                        guild_id=guild_id,
                        force_refresh_logs=force_refresh # Pass force_refresh to control log fetching behavior
                    )
                else:
                    logger.info(f"Background update for guild {guild_id} is already scheduled/in progress by another request.")
            else:
                logger.info(f"Background update for guild {guild_id} is actively being processed (lock held). Not scheduling another.")
        elif guild: # Only log if not needing refresh and guild exists
             logger.info(f"Cached data for guild {guild_id} is fresh. No background update scheduled.")

    logger.info(f"Returning {len(guilds_response)} guilds immediately.")
    return guilds_response

@router.get("/guilds/{guild_id}/logs")
async def get_guild_logs(
    guild_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=100),
    type: Optional[str] = None,
    user: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get guild logs with filtering and pagination"""
    # Start with base query for each log type
    queries = []
    if not type or type == "kick":
        queries.append(db.query(KickLog).filter(KickLog.guild_id == guild_id))
    if not type or type == "invited":
        queries.append(db.query(InviteLog).filter(InviteLog.guild_id == guild_id))
    if not type or type == "invite_declined":
        queries.append(db.query(InviteDeclineLog).filter(InviteDeclineLog.guild_id == guild_id))
    if not type or type == "join":
        queries.append(db.query(JoinLog).filter(JoinLog.guild_id == guild_id))
    if not type or type == "rank_change":
        queries.append(db.query(RankChangeLog).filter(RankChangeLog.guild_id == guild_id))
    if not type or type == "stash":
        queries.append(db.query(StashLog).filter(StashLog.guild_id == guild_id))
    if not type or type == "treasury":
        queries.append(db.query(TreasuryLog).filter(TreasuryLog.guild_id == guild_id))
    if not type or type == "motd":
        queries.append(db.query(MotdLog).filter(MotdLog.guild_id == guild_id))
    if not type or type == "upgrade":
        queries.append(db.query(UpgradeLog).filter(UpgradeLog.guild_id == guild_id))
    if not type or type == "influence":
        queries.append(db.query(InfluenceLog).filter(InfluenceLog.guild_id == guild_id))
    if not type or type == "mission":
        queries.append(db.query(MissionLog).filter(MissionLog.guild_id == guild_id))
    
    # Apply user filter if provided
    if user:
        queries = [q.filter(BaseGuildLog.user.ilike(f"%{user}%")) for q in queries]
    
    # Union all queries and order by time
    query = queries[0].union_all(*queries[1:]).order_by(desc(BaseGuildLog.time))
    
    # Get total count for pagination
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * limit
    logs = query.offset(offset).limit(limit).all()
    
    return {
        "logs": [log.to_dict() for log in logs],
        "total": total,
        "page": page,
        "limit": limit
    }

@router.get("/logs")
async def get_all_guild_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=100),
    type: Optional[str] = None,
    user: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get logs from all guilds with filtering and pagination"""
    # Get all logs of each type
    all_logs = []
    
    # Helper function to apply filters
    def apply_filters(query, model):
        if user:
            query = query.filter(model.user.ilike(f"%{user}%"))
        return query.join(Guild).order_by(desc(model.time))
    
    # Fetch logs based on type filter
    if not type or type == "kick":
        logs = apply_filters(db.query(KickLog), KickLog).all()
        logger.info(f"Found {len(logs)} kick logs")
        all_logs.extend(logs)
    if not type or type == "invited":
        logs = apply_filters(db.query(InviteLog), InviteLog).all()
        logger.info(f"Found {len(logs)} invite logs")
        all_logs.extend(logs)
    if not type or type == "invite_declined":
        logs = apply_filters(db.query(InviteDeclineLog), InviteDeclineLog).all()
        logger.info(f"Found {len(logs)} invite decline logs")
        all_logs.extend(logs)
    if not type or type == "join":
        logs = apply_filters(db.query(JoinLog), JoinLog).all()
        logger.info(f"Found {len(logs)} join logs")
        all_logs.extend(logs)
    if not type or type == "rank_change":
        logs = apply_filters(db.query(RankChangeLog), RankChangeLog).all()
        logger.info(f"Found {len(logs)} rank change logs")
        all_logs.extend(logs)
    if not type or type == "stash":
        logs = apply_filters(db.query(StashLog), StashLog).all()
        logger.info(f"Found {len(logs)} stash logs")
        all_logs.extend(logs)
    if not type or type == "treasury":
        logs = apply_filters(db.query(TreasuryLog), TreasuryLog).all()
        logger.info(f"Found {len(logs)} treasury logs")
        all_logs.extend(logs)
    if not type or type == "motd":
        logs = apply_filters(db.query(MotdLog), MotdLog).all()
        logger.info(f"Found {len(logs)} motd logs")
        all_logs.extend(logs)
    if not type or type == "upgrade":
        logs = apply_filters(db.query(UpgradeLog), UpgradeLog).all()
        logger.info(f"Found {len(logs)} upgrade logs")
        all_logs.extend(logs)
    if not type or type == "influence":
        logs = apply_filters(db.query(InfluenceLog), InfluenceLog).all()
        logger.info(f"Found {len(logs)} influence logs")
        all_logs.extend(logs)
    if not type or type == "mission":
        logs = apply_filters(db.query(MissionLog), MissionLog).all()
        logger.info(f"Found {len(logs)} mission logs")
        all_logs.extend(logs)
    
    # Sort all logs by time
    all_logs.sort(key=lambda x: x.time, reverse=True)
    logger.info(f"Total logs found: {len(all_logs)}")
    
    # Calculate total and apply pagination
    total = len(all_logs)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_logs = all_logs[start_idx:end_idx]
    
    # Format response with guild information
    return {
        "logs": [{
            **log.to_dict(),
            "guild_name": get_short_guild_name(log.guild.name),
        } for log in paginated_logs],
        "total": total,
        "page": page,
        "limit": limit
    } 