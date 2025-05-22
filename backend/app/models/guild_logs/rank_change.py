from sqlalchemy import Column, String
from datetime import datetime

from .base import BaseGuildLog

class RankChangeLog(BaseGuildLog):
    """Log entry for when a member's rank is changed"""
    __tablename__ = "guild_logs_rank_change"

    # Who changed the rank
    changed_by = Column(String, nullable=False)
    old_rank = Column(String, nullable=False)
    new_rank = Column(String, nullable=False)

    def to_dict(self):
        """Convert the rank change log entry to a dictionary."""
        base = super().to_dict()
        base.update({
            "changed_by": self.changed_by,
            "old_rank": self.old_rank,
            "new_rank": self.new_rank
        })
        return base

    @classmethod
    def from_api_response(cls, guild_id: str, log_entry: dict):
        """Create a rank change log instance from an API response entry."""
        if log_entry["type"] != "rank_change":
            raise ValueError(f"Expected rank_change log type, got {log_entry['type']}")
            
        return cls(
            id=log_entry["id"],
            guild_id=guild_id,
            time=datetime.fromisoformat(log_entry["time"].replace('Z', '+00:00')),
            type=log_entry["type"],
            user=log_entry["user"],  # The person whose rank was changed
            changed_by=log_entry["changed_by"],  # The person who changed the rank
            old_rank=log_entry["old_rank"],
            new_rank=log_entry["new_rank"]
        ) 