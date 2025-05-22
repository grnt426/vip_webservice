from sqlalchemy import Column, Integer, String, JSON
from datetime import datetime
import json

from .base import BaseGuildLog

class InfluenceLog(BaseGuildLog):
    """Log entry for guild influence changes"""
    __tablename__ = "guild_logs_influence"

    # Influence details
    activity = Column(String, nullable=False)  # daily_login or gifted
    participants = Column(Integer, nullable=False)  # Number of participants
    total_participants = Column(String, nullable=False, default='[]')  # Array of user IDs stored as JSON string

    def to_dict(self):
        """Convert the influence log entry to a dictionary."""
        base = super().to_dict()
        base.update({
            "activity": self.activity,
            "participants": self.participants,
            "total_participants": json.loads(self.total_participants)  # Deserialize back to list
        })
        return base

    @classmethod
    def from_api_response(cls, guild_id: str, log_entry: dict):
        """Create an influence log instance from an API response entry."""
        if log_entry["type"] != "influence":
            raise ValueError(f"Expected influence log type, got {log_entry['type']}")
        
        # Get total_participants list and ensure it's a JSON string
        total_participants = log_entry.get("total_participants", [])
        if isinstance(total_participants, list):
            total_participants = json.dumps(total_participants)
            
        # participants is the length of total_participants
        participants = int(log_entry.get("total_participants", 0))
            
        return cls(
            id=log_entry["id"],
            guild_id=guild_id,
            time=datetime.fromisoformat(log_entry["time"].replace('Z', '+00:00')),
            type=log_entry["type"],
            user=log_entry.get("user"),  # Optional
            activity=log_entry["activity"],
            participants=participants,  # Number of participants
            total_participants=total_participants  # JSON string of participant list
        ) 