from datetime import datetime

from .base import BaseGuildLog

class JoinLog(BaseGuildLog):
    """Log entry for when a member joins the guild"""
    __tablename__ = "guild_logs_join"

    def to_dict(self):
        """Convert the join log entry to a dictionary."""
        return super().to_dict()

    @classmethod
    def from_api_response(cls, guild_id: str, log_entry: dict):
        """Create a join log instance from an API response entry."""
        if log_entry["type"] != "joined":
            raise ValueError(f"Expected joined log type, got {log_entry['type']}")
            
        return cls(
            id=log_entry["id"],
            guild_id=guild_id,
            time=datetime.fromisoformat(log_entry["time"].replace('Z', '+00:00')),
            type=log_entry["type"],
            user=log_entry["user"]  # The person who joined
        ) 