from sqlalchemy import Column, String, Integer
from datetime import datetime

from .base import BaseGuildLog

class MissionLog(BaseGuildLog):
    """Log entry for guild mission activities"""
    __tablename__ = "guild_logs_mission"

    # Mission details
    state = Column(String, nullable=False)  # start, success, or fail
    influence = Column(Integer, nullable=True)  # Amount of influence awarded (only on success)

    def to_dict(self):
        """Convert the mission log entry to a dictionary."""
        base = super().to_dict()
        base.update({
            "state": self.state,
            "influence": self.influence
        })
        return base

    @classmethod
    def from_api_response(cls, guild_id: str, log_entry: dict):
        """Create a mission log instance from an API response entry."""
        if log_entry["type"] != "mission":
            raise ValueError(f"Expected mission log type, got {log_entry['type']}")
            
        return cls(
            id=log_entry["id"],
            guild_id=guild_id,
            time=datetime.fromisoformat(log_entry["time"].replace('Z', '+00:00')),
            type=log_entry["type"],
            user=log_entry.get("user"),  # Optional - only present when state is 'start'
            state=log_entry["state"],
            influence=log_entry.get("influence")  # Optional - only present on success
        ) 