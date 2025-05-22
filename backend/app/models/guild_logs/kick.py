from sqlalchemy import Column, String
from datetime import datetime

from .base import BaseGuildLog

class KickLog(BaseGuildLog):
    """Log entry for when a member is kicked from the guild"""
    __tablename__ = "guild_logs_kick"

    # Who performed the kick action
    kicked_by = Column(String, nullable=False)

    def to_dict(self):
        """Convert the kick log entry to a dictionary."""
        base = super().to_dict()
        base.update({
            "kicked_by": self.kicked_by
        })
        return base

    @classmethod
    def from_api_response(cls, guild_id: str, log_entry: dict):
        """Create a kick log instance from an API response entry."""
        if log_entry["type"] != "kick":
            raise ValueError(f"Expected kick log type, got {log_entry['type']}")
            
        return cls(
            id=log_entry["id"],
            guild_id=guild_id,
            time=datetime.fromisoformat(log_entry["time"].replace('Z', '+00:00')),
            type=log_entry["type"],
            user=log_entry["user"],  # The person who was kicked
            kicked_by=log_entry["kicked_by"]  # The person who did the kicking
        ) 