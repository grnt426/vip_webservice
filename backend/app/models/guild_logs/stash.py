from sqlalchemy import Column, String, Integer, BigInteger
from datetime import datetime

from .base import BaseGuildLog

class StashLog(BaseGuildLog):
    """Log entry for when items or coins are deposited/withdrawn from the guild stash"""
    __tablename__ = "guild_logs_stash"

    operation = Column(String, nullable=False)  # deposit, withdraw, or move
    item_id = Column(Integer)  # Optional - not present for coin operations
    count = Column(Integer)  # Number of items
    coins = Column(BigInteger)  # Amount of coins (in copper)
    item_name = Column(String)  # Optional - cached item name

    def to_dict(self):
        """Convert the stash log entry to a dictionary."""
        base = super().to_dict()
        base.update({
            "operation": self.operation,
            "item_id": self.item_id,
            "count": self.count,
            "coins": self.coins,
            "item_name": self.item_name
        })
        return base

    @classmethod
    def from_api_response(cls, guild_id: str, log_entry: dict):
        """Create a stash log instance from an API response entry."""
        if log_entry["type"] != "stash":
            raise ValueError(f"Expected stash log type, got {log_entry['type']}")
            
        return cls(
            id=log_entry["id"],
            guild_id=guild_id,
            time=datetime.fromisoformat(log_entry["time"].replace('Z', '+00:00')),
            type=log_entry["type"],
            user=log_entry["user"],  # The person who performed the operation
            operation=log_entry["operation"],
            item_id=log_entry.get("item_id"),
            count=log_entry.get("count", 0),
            coins=log_entry.get("coins", 0),
            item_name=log_entry.get("item_name")
        ) 