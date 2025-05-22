from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func, or_
from typing import List, Optional
from datetime import datetime
import logging

from app.database import get_db
from app.models.guild import Guild, GuildEmblem
from app.models.guild_logs import (
    BaseGuildLog, KickLog, InviteLog, InviteDeclineLog, JoinLog, RankChangeLog,
    StashLog, TreasuryLog, MotdLog, UpgradeLog, InfluenceLog, MissionLog,
    create_log_entry, LOG_TYPE_MAP
)
from app.models.guild_member import GuildMember, guild_memberships
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

@router.get("/guilds")
async def get_guilds(force_refresh: bool = False, db: Session = Depends(get_db)):
    """Get all tracked guild data, refreshing from GW2 API if stale"""
    logger.info("Processing request for guild data")
    guilds = []
    guild_data_map = {}  # Store guild data for membership processing
    
    # First pass: Create/update all guilds and their basic data
    for guild_id in GUILD_IDS:
        logger.info(f"Processing guild: {guild_id}")
        # Get guild from database
        guild = db.query(Guild).filter(Guild.id == guild_id).first()
        
        try:
            # Check if we need to refresh the data
            if not guild:
                logger.info(f"No existing data found for guild {guild_id}")
            elif force_refresh or gw2_client.is_data_stale(guild.last_updated):
                logger.info(f"Data refresh needed for guild {guild_id}. Force refresh: {force_refresh}")
            else:
                logger.info(f"Using cached data for guild {guild_id}")
                guilds.append(guild.to_dict())
                continue

            # Start a nested transaction for this guild's updates
            with db.begin_nested():
                # Fetch fresh data from GW2 API
                logger.info(f"Fetching fresh data for guild {guild_id}")
                guild_data = await gw2_client.get_guild_data(
                    guild_id, 
                    # Only pass last_log_id if not doing a force refresh
                    last_log_id=None if force_refresh else (guild.last_log_id if guild else None)
                )
                
                # If we couldn't get guild data, skip this guild
                if not guild_data:
                    logger.warning(f"No data received for guild {guild_id}, skipping")
                    if guild:
                        guilds.append(guild.to_dict())
                    continue
                
                # Store guild data for later membership processing
                guild_data_map[guild_id] = guild_data
                
                if not guild:
                    # Create new guild if it doesn't exist
                    logger.info(f"Creating new guild record for {guild_id}")
                    guild = Guild(
                        id=guild_data["id"],
                        name=guild_data["name"],
                        tag=guild_data["tag"],
                        level=guild_data.get("level", 0),
                        motd=guild_data["motd"],
                        influence=guild_data["influence"],
                        aetherium=guild_data["aetherium"],
                        resonance=guild_data["resonance"],
                        favor=guild_data["favor"],
                        last_log_id=guild_data["last_log_id"]
                    )
                    db.add(guild)
                    db.flush()  # Ensure guild is created before adding related data
                
                # Update guild data
                guild.name = guild_data["name"]
                guild.tag = guild_data["tag"]
                guild.level = guild_data.get("level", 0)
                guild.motd = guild_data["motd"]
                guild.influence = guild_data["influence"]
                guild.aetherium = guild_data["aetherium"]
                guild.resonance = guild_data["resonance"]
                guild.favor = guild_data["favor"]
                guild.last_log_id = guild_data["last_log_id"]
                guild.last_updated = datetime.utcnow()
                db.flush()

                # Process emblem
                if guild_data.get("emblem"):
                    logger.info(f"Processing emblem for guild {guild_id}")
                    emblem_data = guild_data["emblem"]
                    if not guild.emblem:
                        guild.emblem = GuildEmblem()
                    guild.emblem.background_id = emblem_data["background"]["id"]
                    guild.emblem.background_colors = emblem_data["background"]["colors"]
                    guild.emblem.foreground_id = emblem_data["foreground"]["id"]
                    guild.emblem.foreground_colors = emblem_data["foreground"]["colors"]
                    guild.emblem.flags = emblem_data.get("flags", [])
                    db.flush()
                
                # Process new log entries
                if guild_data.get("logs"):
                    logger.info(f"Processing {len(guild_data['logs'])} new log entries for guild {guild_id}")
                    new_logs_count = 0
                    for log_entry in guild_data["logs"]:
                        # Get the appropriate log model class for this type
                        log_type = log_entry["type"]
                        if log_type not in LOG_TYPE_MAP:
                            logger.warning(f"Unknown log type: {log_type}")
                            continue
                            
                        log_model = LOG_TYPE_MAP[log_type]
                        
                        # Check if log entry already exists
                        existing_log = db.query(log_model).filter(
                            log_model.guild_id == guild_id,
                            log_model.id == log_entry["id"]
                        ).first()
                        
                        if not existing_log:
                            new_log = create_log_entry(guild_id, log_entry)
                            db.add(new_log)
                            new_logs_count += 1
                    
                    logger.info(f"Added {new_logs_count} new logs for guild {guild_id}")
                    db.flush()

                # Process ranks first (since members reference ranks)
                if guild_data.get("ranks"):
                    logger.info(f"Processing {len(guild_data['ranks'])} ranks")
                    # Get existing ranks
                    existing_ranks = {
                        rank.id: rank for rank in 
                        db.query(GuildRank).filter(GuildRank.guild_id == guild_id).all()
                    }
                    
                    # Track which ranks still exist
                    processed_ranks = set()
                    
                    # Update existing ranks or create new ones
                    for rank_data in guild_data["ranks"]:
                        rank_id = rank_data["id"]
                        processed_ranks.add(rank_id)
                        
                        if rank_id in existing_ranks:
                            # Update existing rank
                            rank = existing_ranks[rank_id]
                            rank.order = rank_data["order"]
                            rank.permissions = rank_data["permissions"]
                            rank.icon = rank_data.get("icon")
                        else:
                            # Add new rank
                            rank = GuildRank.from_api_response(guild_id, rank_data)
                            db.add(rank)
                    
                    # Remove ranks that no longer exist in the API response
                    for rank_id, rank in existing_ranks.items():
                        if rank_id not in processed_ranks:
                            db.delete(rank)
                    
                    db.flush()

            # If we get here, the nested transaction was successful
            db.commit()
            logger.info(f"Successfully processed basic data for guild {guild_id}")
            
        except Exception as e:
            logger.error(f"Error processing guild {guild_id}: {str(e)}", exc_info=True)
            db.rollback()
            if guild:
                # Return cached data if available
                logger.info(f"Falling back to cached data for guild {guild_id}")
                guilds.append(guild.to_dict())
    
    # Second pass: Process all memberships after all guilds exist
    if guild_data_map:
        try:
            logger.info("Processing all guild memberships")
            with db.begin_nested():
                for guild_id, guild_data in guild_data_map.items():
                    if guild_data.get("members"):
                        logger.info(f"Processing {len(guild_data['members'])} members for guild {guild_id}")
                        # Process members in batches to avoid memory issues
                        batch_size = 50
                        members_data = guild_data["members"]
                        
                        for i in range(0, len(members_data), batch_size):
                            batch = members_data[i:i + batch_size]
                            for member_data in batch:
                                GuildMember.add_guild_membership(db, member_data["name"], guild_id, member_data)
                            db.flush()
            
            db.commit()
            logger.info("Successfully processed all guild memberships")
            
            # Now get the final guild data for the response
            guilds = []
            for guild_id in guild_data_map.keys():
                guild = db.query(Guild).filter(Guild.id == guild_id).first()
                if guild:
                    guilds.append(guild.to_dict())
                else:
                    logger.error(f"Guild {guild_id} not found in database after processing")
        except Exception as e:
            logger.error(f"Error processing guild memberships: {str(e)}", exc_info=True)
            db.rollback()
            # Fall back to cached data for all guilds
            guilds = [
                db.query(Guild).filter(Guild.id == guild_id).first().to_dict()
                for guild_id in guild_data_map.keys()
            ]
    
    logger.info(f"Returning data for {len(guilds)} guilds")
    return guilds

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