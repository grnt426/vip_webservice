from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, timedelta
import random
from typing import List, Optional
from sqlalchemy.exc import OperationalError
import time
import logging

from app.database import get_db
from app.models.guild_lottery import LotteryEntry, LotteryWinner
from app.models.guild_membership import GuildMembership
from app.models.account import Account
from app.models.user import User
from app.schemas.lottery_schemas import LotteryEntryResponse, LotteryWinnerResponse, LotteryStats
from app.api.deps import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

OFFICER_RANKS = [
    "Community Owner",
    "Guild Leader",
    "Vice Leader",
    "Sr Officer",
    "Officer",
    "Probi Officer"
]  # Ranks that cannot participate

GOLD_TO_COPPER = 10000  # 1 gold = 10000 copper
MAX_RETRIES = 3  # Maximum number of retries for database operations
RETRY_DELAY = 0.5  # Delay between retries in seconds

def get_current_week():
    """Get the current ISO week number and year"""
    now = datetime.utcnow()
    return now.isocalendar()[1], now.isocalendar()[0]

def is_officer(db: Session, account_id: int) -> bool:
    """Check if an account has an officer rank in any guild"""
    memberships = db.query(GuildMembership).filter(
        GuildMembership.account_id == account_id,
    ).all()
    
    return any(membership.rank in OFFICER_RANKS for membership in memberships)

def is_officer_user(user: User, db: Session) -> bool:
    """Check if a user has officer privileges"""
    if not user.account:
        return False
    return is_officer(db, user.account.id)

async def process_lottery_entry(
    guild_id: str,
    account_id: int,
    copper_amount: int,
    db: Session
) -> Optional[LotteryEntry]:
    """Process a lottery entry from a stash deposit with retry logic"""
    
    # Check if account is an officer
    if is_officer(db, account_id):
        return None  # Silently skip officer entries
    
    # Get current week
    week_number, year = get_current_week()
    
    # Calculate number of lots (1 gold = 1 lot)
    gold_amount = copper_amount / GOLD_TO_COPPER
    new_lots = int(gold_amount)  # Truncate to whole number
    
    if new_lots < 1:
        return None  # Skip entries less than 1 gold

    retries = 0
    last_error = None
    
    while retries < MAX_RETRIES:
        try:
            # Get or create entry for this week
            entry = db.query(LotteryEntry).filter(
                LotteryEntry.account_id == account_id,
                LotteryEntry.week_number == week_number,
                LotteryEntry.year == year
            ).with_for_update().first()  # Lock the row
            
            if entry:
                # Check if adding new lots would exceed maximum
                if entry.lots + new_lots > 10:
                    return None  # Skip if would exceed maximum
                entry.lots += new_lots
                entry.updated_at = datetime.utcnow()
            else:
                if new_lots > 10:
                    new_lots = 10  # Cap at maximum
                entry = LotteryEntry(
                    guild_id=guild_id,  # Record which guild the entry came from
                    account_id=account_id,
                    week_number=week_number,
                    year=year,
                    lots=new_lots
                )
                db.add(entry)
            
            db.commit()
            return entry
            
        except OperationalError as e:
            last_error = e
            if "database is locked" in str(e):
                retries += 1
                if retries < MAX_RETRIES:
                    time.sleep(RETRY_DELAY * (2 ** retries))  # Exponential backoff
                    continue
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise

    if last_error:
        logger.error(f"Failed to process lottery entry after {MAX_RETRIES} retries: {last_error}")
        raise last_error

    return None

@router.get("/entries", response_model=List[LotteryEntryResponse])
async def get_current_entries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all entries for the current week"""
    week_number, year = get_current_week()
    
    entries = db.query(LotteryEntry).filter(
        LotteryEntry.week_number == week_number,
        LotteryEntry.year == year
    ).all()
    
    return entries

@router.post("/draw")
async def draw_winner(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Draw a winner for the current week's lottery"""
    if not is_officer_user(current_user, db):
        raise HTTPException(status_code=403, detail="Only officers can draw winners")

    week_number, year = get_current_week()
    
    retries = 0
    last_error = None
    
    while retries < MAX_RETRIES:
        try:
            # Get all entries for the week with row locks
            entries = db.query(LotteryEntry).filter(
                LotteryEntry.week_number == week_number,
                LotteryEntry.year == year
            ).with_for_update().all()
            
            if not entries:
                raise HTTPException(status_code=404, detail="No entries found for current week")
            
            # Create weighted list based on number of lots
            weighted_entries = []
            for entry in entries:
                weighted_entries.extend([entry] * entry.lots)
            
            # Draw winner
            winning_entry = random.choice(weighted_entries)
            
            # Calculate prize (90% of total pot)
            total_lots = sum(entry.lots for entry in entries)
            total_gold = total_lots  # 1 lot = 1 gold
            prize_gold = int(total_gold * 0.9)  # 90% of pot
            prize_copper = prize_gold * GOLD_TO_COPPER
            
            # Record winner
            winner = LotteryWinner(
                guild_id=winning_entry.guild_id,  # Record which guild the winning entry came from
                account_id=winning_entry.account_id,
                week_number=week_number,
                year=year,
                prize_amount=prize_copper
            )
            db.add(winner)
            db.commit()
            
            return winner
            
        except OperationalError as e:
            last_error = e
            if "database is locked" in str(e):
                retries += 1
                if retries < MAX_RETRIES:
                    time.sleep(RETRY_DELAY * (2 ** retries))  # Exponential backoff
                    continue
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise

    if last_error:
        logger.error(f"Failed to draw winner after {MAX_RETRIES} retries: {last_error}")
        raise last_error

@router.get("/stats", response_model=LotteryStats)
async def get_lottery_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get statistics about the lottery"""
    week_number, year = get_current_week()
    
    # Current week's pot (across all guilds)
    current_entries = db.query(LotteryEntry).filter(
        LotteryEntry.week_number == week_number,
        LotteryEntry.year == year
    ).all()
    
    total_lots = sum(entry.lots for entry in current_entries)
    current_pot = total_lots * GOLD_TO_COPPER  # in copper
    
    # Past winners
    past_winners = db.query(LotteryWinner).order_by(
        LotteryWinner.created_at.desc()
    ).limit(10).all()
    
    return {
        "current_pot": current_pot,
        "current_entries_count": len(current_entries),
        "past_winners": past_winners
    }

@router.post("/winners/{winner_id}/paid")
async def mark_winner_paid(
    winner_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a winner as paid out"""
    if not is_officer_user(current_user, db):
        raise HTTPException(status_code=403, detail="Only officers can mark winners as paid")

    retries = 0
    last_error = None
    
    while retries < MAX_RETRIES:
        try:
            winner = db.query(LotteryWinner).filter(
                LotteryWinner.id == winner_id
            ).with_for_update().first()
            
            if not winner:
                raise HTTPException(status_code=404, detail="Winner not found")
            
            winner.paid_out = True
            winner.paid_at = datetime.utcnow()
            db.commit()
            return winner
            
        except OperationalError as e:
            last_error = e
            if "database is locked" in str(e):
                retries += 1
                if retries < MAX_RETRIES:
                    time.sleep(RETRY_DELAY * (2 ** retries))  # Exponential backoff
                    continue
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise

    if last_error:
        logger.error(f"Failed to mark winner as paid after {MAX_RETRIES} retries: {last_error}")
        raise last_error 