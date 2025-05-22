from sqlalchemy import Column, Integer, String
from datetime import datetime

from .base import BaseGuildLog

class TreasuryLog(BaseGuildLog):
    """Log entry for when items are deposited into the guild treasury"""
    __tablename__ = "guild_logs_treasury"

    item_id = Column(Integer, nullable=False)
    count = Column(Integer, nullable=False)
    item_name = Column(String)  # Optional - cached item name

    def to_dict(self):
        """Convert the treasury log entry to a dictionary."""
        base = super().to_dict()
        base.update({
            "item_id": self.item_id,
            "count": self.count,
            "item_name": self.item_name
        })
        return base

    @classmethod
    def from_api_response(cls, guild_id: str, log_entry: dict):
        """Create a treasury log instance from an API response entry."""
        if log_entry["type"] != "treasury":
            raise ValueError(f"Expected treasury log type, got {log_entry['type']}")
            
        return cls(
            id=log_entry["id"],
            guild_id=guild_id,
            time=datetime.fromisoformat(log_entry["time"].replace('Z', '+00:00')),
            type=log_entry["type"],
            user=log_entry["user"],  # The person who deposited the items
            item_id=log_entry["item_id"],
            count=log_entry["count"],
            item_name=log_entry.get("item_name")
        ) 