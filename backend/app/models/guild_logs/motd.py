from sqlalchemy import Column, Text
from datetime import datetime

from .base import BaseGuildLog

class MotdLog(BaseGuildLog):
    """Log entry for when the guild's message of the day is changed"""
    __tablename__ = "guild_logs_motd"

    motd = Column(Text, nullable=False)  # The new message of the day

    def to_dict(self):
        """Convert the MOTD log entry to a dictionary."""
        base = super().to_dict()
        base.update({
            "motd": self.motd
        })
        return base

    @classmethod
    def from_api_response(cls, guild_id: str, log_entry: dict):
        """Create a MOTD log instance from an API response entry."""
        if log_entry["type"] != "motd":
            raise ValueError(f"Expected motd log type, got {log_entry['type']}")
            
        return cls(
            id=log_entry["id"],
            guild_id=guild_id,
            time=datetime.fromisoformat(log_entry["time"].replace('Z', '+00:00')),
            type=log_entry["type"],
            user=log_entry["user"],  # The person who changed the MOTD
            motd=log_entry["motd"]  # The new message
        ) 