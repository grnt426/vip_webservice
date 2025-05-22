from sqlalchemy import Column, String
from datetime import datetime

from .base import BaseGuildLog

class InviteDeclineLog(BaseGuildLog):
    """Log entry for when a guild invite is declined"""
    __tablename__ = "guild_logs_invite_decline"

    # Who declined the invite
    declined_by = Column(String, nullable=False)

    def to_dict(self):
        """Convert the invite decline log entry to a dictionary."""
        base = super().to_dict()
        base.update({
            "declined_by": self.declined_by
        })
        return base

    @classmethod
    def from_api_response(cls, guild_id: str, log_entry: dict):
        """Create an invite decline log instance from an API response entry."""
        if log_entry["type"] != "invite_declined":
            raise ValueError(f"Expected invite_declined log type, got {log_entry['type']}")
            
        return cls(
            id=log_entry["id"],
            guild_id=guild_id,
            time=datetime.fromisoformat(log_entry["time"].replace('Z', '+00:00')),
            type=log_entry["type"],
            user=log_entry["user"],  # The person who was invited
            declined_by=log_entry["declined_by"]  # The person who declined the invite
        ) 