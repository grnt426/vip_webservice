from sqlalchemy import Column, String
from datetime import datetime

from .base import BaseGuildLog

class InviteLog(BaseGuildLog):
    """Log entry for when a member is invited to the guild"""
    __tablename__ = "guild_logs_invite"

    # Who sent the invite
    invited_by = Column(String, nullable=False)

    def to_dict(self):
        """Convert the invite log entry to a dictionary."""
        base = super().to_dict()
        base.update({
            "invited_by": self.invited_by
        })
        return base

    @classmethod
    def from_api_response(cls, guild_id: str, log_entry: dict):
        """Create an invite log instance from an API response entry."""
        if log_entry["type"] != "invited":
            raise ValueError(f"Expected invited log type, got {log_entry['type']}")
            
        return cls(
            id=log_entry["id"],
            guild_id=guild_id,
            time=datetime.fromisoformat(log_entry["time"].replace('Z', '+00:00')),
            type=log_entry["type"],
            user=log_entry["user"],  # The person who was invited
            invited_by=log_entry["invited_by"]  # The person who sent the invite
        ) 