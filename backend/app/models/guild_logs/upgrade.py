import traceback

from sqlalchemy import Column, String, Integer
from datetime import datetime
import logging

from .base import BaseGuildLog

logger = logging.getLogger(__name__)

class UpgradeLog(BaseGuildLog):
    """Log entry for when a guild upgrade is queued, cancelled, completed, or sped up"""
    __tablename__ = "guild_logs_upgrade"

    action = Column(String, nullable=False)  # queued, cancelled, completed, or sped_up
    upgrade_id = Column(Integer, nullable=True)  # The upgrade ID (for regular upgrades)
    item_id = Column(Integer, nullable=True)  # The item ID (for item-based upgrades like decorations)
    recipe_id = Column(Integer)  # Optional - only present for scribe crafted upgrades
    count = Column(Integer)  # Optional - only present for completed upgrades
    upgrade_name = Column(String)  # Optional - cached upgrade name

    def to_dict(self):
        """Convert the upgrade log entry to a dictionary."""
        base = super().to_dict()
        base.update({
            "action": self.action,
            "upgrade_id": self.upgrade_id,
            "item_id": self.item_id,
            "recipe_id": self.recipe_id,
            "count": self.count,
            "upgrade_name": self.upgrade_name
        })
        return base

    @classmethod
    def from_api_response(cls, guild_id: str, log_entry: dict):
        """Create an upgrade log instance from an API response entry."""
        if log_entry["type"] != "upgrade":
            raise ValueError(f"Expected upgrade log type, got {log_entry['type']}")
            
        logger.debug(f"Processing upgrade log entry: {log_entry}")
        
        try:
            return cls(
                id=log_entry["id"],
                guild_id=guild_id,
                time=datetime.fromisoformat(log_entry["time"].replace('Z', '+00:00')),
                type=log_entry["type"],
                user=log_entry.get("user"),  # Optional - not present for queued actions
                action=log_entry["action"],
                upgrade_id=log_entry.get("upgrade_id"),  # Optional - for regular upgrades
                item_id=log_entry.get("item_id"),  # Optional - for item-based upgrades
                recipe_id=log_entry.get("recipe_id"),  # Optional
                count=log_entry.get("count"),  # Optional - only present for completed upgrades
                upgrade_name=log_entry.get("upgrade_name")  # Optional - cached name
            )
        except KeyError as e:
            logger.error("Failed to parse upgrade log entry: %s", e)
            logger.error("Raw entry: %s", log_entry)
            traceback.print_exc()
            return None