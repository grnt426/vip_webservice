from sqlalchemy import Column, String, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class GuildRank(Base):
    __tablename__ = "guild_ranks"

    # Composite primary key
    id = Column(String, primary_key=True)  # The rank name (e.g. "Leader")
    guild_id = Column(String, ForeignKey("guilds.id"), primary_key=True)

    # Rank data
    order = Column(Integer, nullable=False)  # Sort order (lower = higher rank)
    permissions = Column(JSON, nullable=False, default=list)  # List of permission strings
    icon = Column(String)  # URL to rank icon

    # Relationships
    guild = relationship("Guild", back_populates="ranks")

    def to_dict(self):
        """Convert the rank to a dictionary matching the GW2 API response format."""
        return {
            "id": self.id,
            "order": self.order,
            "permissions": self.permissions,
            "icon": self.icon
        }

    @classmethod
    def from_api_response(cls, guild_id: str, rank_data: dict):
        """Create a GuildRank instance from an API response entry."""
        return cls(
            id=rank_data["id"],
            guild_id=guild_id,
            order=rank_data["order"],
            permissions=rank_data["permissions"],
            icon=rank_data.get("icon")
        ) 