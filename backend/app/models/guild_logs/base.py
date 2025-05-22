from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declared_attr
from datetime import datetime
import re

from app.database import Base

class BaseGuildLog(Base):
    """Base class for all guild log types"""
    __abstract__ = True

    # Primary key and foreign key to guild
    id = Column(Integer, primary_key=True)  # The GW2 API log entry ID
    
    @declared_attr
    def guild_id(cls):
        return Column(String, ForeignKey("guilds.id"), primary_key=True)
    
    @declared_attr
    def guild(cls):
        # Map log types to their corresponding relationship names in the Guild model
        relationship_map = {
            'joined': 'join_logs',  # Changed back to 'joined' to match API
            'invited': 'invite_logs',
            'invite_declined': 'invite_decline_logs',
            'kick': 'kick_logs',
            'rank_change': 'rank_change_logs',
            'treasury': 'treasury_logs',
            'stash': 'stash_logs',
            'motd': 'motd_logs',
            'upgrade': 'upgrade_logs',
            'influence': 'influence_logs',
            'mission': 'mission_logs'
        }
        # Get the type from the class name (e.g., RankChangeLog -> rank_change)
        # Handle CamelCase to snake_case conversion
        log_type = re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__.replace('Log', '')).lower()
        # Special cases that don't follow the simple pattern
        special_cases = {
            'join': 'joined',  # Changed back to convert 'join' to 'joined'
            'invite': 'invited',
            'invite_decline': 'invite_declined'
        }
        log_type = special_cases.get(log_type, log_type)
        return relationship("Guild", back_populates=relationship_map[log_type])

    # Common fields for all log types
    time = Column(DateTime, nullable=False)
    type = Column(String, nullable=False)
    user = Column(String)  # Optional in some cases

    # Metadata
    fetched_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert the log entry to a dictionary."""
        return {
            "id": self.id,
            "time": self.time.isoformat() if self.time else None,
            "type": self.type,
            "user": self.user,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
        }

    @classmethod
    def from_api_response(cls, guild_id: str, log_entry: dict):
        """Create a log instance from an API response entry."""
        raise NotImplementedError("Subclasses must implement from_api_response") 