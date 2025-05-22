from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database import Base

class Guild(Base):
    __tablename__ = "guilds"

    # Primary guild data
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    tag = Column(String, nullable=False)
    level = Column(Integer, nullable=False)
    motd = Column(String)  # Message of the day
    
    # Guild resources
    influence = Column(Integer, default=0)
    aetherium = Column(Integer, default=0)
    resonance = Column(Integer, default=0)
    favor = Column(Integer, default=0)

    # Emblem relationship
    emblem = relationship("GuildEmblem", uselist=False, back_populates="guild", cascade="all, delete-orphan")

    def to_dict(self):
        """Convert the guild model to a dictionary matching the GW2 API response format."""
        return {
            "id": self.id,
            "name": self.name,
            "tag": self.tag,
            "level": self.level,
            "motd": self.motd,
            "influence": self.influence,
            "aetherium": self.aetherium,
            "resonance": self.resonance,
            "favor": self.favor,
            "emblem": self.emblem.to_dict() if self.emblem else None
        }

class GuildEmblem(Base):
    __tablename__ = "guild_emblems"

    # Primary key and foreign key to guild
    guild_id = Column(String, ForeignKey("guilds.id"), primary_key=True)
    guild = relationship("Guild", back_populates="emblem")

    # Background details
    background_id = Column(Integer, nullable=False)
    background_colors = Column(JSON, nullable=False, default=list)  # Store colors as JSON array

    # Foreground details
    foreground_id = Column(Integer, nullable=False)
    foreground_colors = Column(JSON, nullable=False, default=list)  # Store colors as JSON array

    # Flags stored as JSON array
    flags = Column(JSON, nullable=False, default=list)

    def to_dict(self):
        """Convert the emblem model to a dictionary matching the GW2 API response format."""
        return {
            "background": {
                "id": self.background_id,
                "colors": self.background_colors
            },
            "foreground": {
                "id": self.foreground_id,
                "colors": self.foreground_colors
            },
            "flags": self.flags
        } 