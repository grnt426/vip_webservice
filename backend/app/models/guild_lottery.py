from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class LotteryEntry(Base):
    """Represents a single lottery entry for a player"""
    __tablename__ = "guild_lottery_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(String, ForeignKey("guilds.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    week_number = Column(Integer, nullable=False)  # ISO week number
    year = Column(Integer, nullable=False)  # Year for the week number
    lots = Column(Integer, nullable=False, default=0)  # Number of lots purchased this week
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    guild = relationship("Guild", back_populates="lottery_entries")
    account = relationship("Account", back_populates="lottery_entries")

class LotteryWinner(Base):
    """Records the winners of each weekly lottery"""
    __tablename__ = "guild_lottery_winners"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(String, ForeignKey("guilds.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    week_number = Column(Integer, nullable=False)  # ISO week number
    year = Column(Integer, nullable=False)  # Year for the week number
    prize_amount = Column(Integer, nullable=False)  # Prize amount in copper
    paid_out = Column(Boolean, default=False)  # Whether the prize has been paid out
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)  # When the prize was paid out

    # Relationships
    guild = relationship("Guild", back_populates="lottery_winners")
    account = relationship("Account", back_populates="lottery_wins") 