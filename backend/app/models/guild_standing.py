from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class GuildStanding(Base):
    """
    Tracks the current standing (point total) for each account.
    Points accumulate from mod actions and decay over time.
    """
    __tablename__ = "guild_standings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    current_points = Column(Integer, default=0)
    last_decay_at = Column(DateTime, default=datetime.utcnow)  # Track when we last applied decay
    is_disabled = Column(Boolean, default=False)  # Auto-disable at >= 100 points
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    account = relationship("Account", back_populates="standing")
    
    def to_dict(self):
        """Convert the standing to a dictionary."""
        return {
            "id": self.id,
            "account_id": self.account_id,
            "current_points": self.current_points,
            "last_decay_at": self.last_decay_at.isoformat() if self.last_decay_at else None,
            "is_disabled": self.is_disabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f"<GuildStanding(account_id={self.account_id}, points={self.current_points}, disabled={self.is_disabled})>" 