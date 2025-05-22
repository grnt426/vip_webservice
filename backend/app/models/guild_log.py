from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

class GuildLog(Base):
    __tablename__ = "guild_logs"

    # Primary key and foreign key to guild
    id = Column(Integer, primary_key=True)  # The GW2 API log entry ID
    guild_id = Column(String, ForeignKey("guilds.id"), primary_key=True)
    guild = relationship("Guild", back_populates="logs")

    # Common fields for all log types
    time = Column(DateTime, nullable=False)
    type = Column(String, nullable=False)
    user = Column(String)  # Optional in some cases

    # Additional fields stored as JSON to handle different log types
    details = Column(JSON, nullable=False, default=dict)

    # Metadata
    fetched_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert the log entry to a dictionary."""
        base = {
            "id": self.id,
            "time": self.time.isoformat() if self.time else None,
            "type": self.type,
            "user": self.user,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
        }
        # Merge in any additional fields from details
        if self.details:
            base.update(self.details)
        return base

    @classmethod
    def from_api_response(cls, guild_id: str, log_entry: dict):
        """Create a GuildLog instance from an API response entry."""
        # Extract common fields
        instance = cls(
            id=log_entry["id"],
            guild_id=guild_id,
            time=datetime.fromisoformat(log_entry["time"].replace('Z', '+00:00')),
            type=log_entry["type"],
            user=log_entry.get("user"),
        )

        # Store all additional fields in details
        details = dict(log_entry)
        for field in ["id", "time", "type", "user"]:
            details.pop(field, None)
        instance.details = details

        return instance 