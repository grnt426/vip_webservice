from sqlalchemy import Column, Integer, String, JSON
from app.database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    type = Column(String, nullable=False)
    level = Column(Integer, nullable=False)
    rarity = Column(String, nullable=False)
    vendor_value = Column(Integer, nullable=False)
    details = Column(JSON, nullable=False, default=dict)
    game_types = Column(JSON, nullable=False, default=list)
    flags = Column(JSON, nullable=False, default=list)
    restrictions = Column(JSON, nullable=False, default=list)

    def to_dict(self):
        """Convert the item to a dictionary matching the GW2 API response format."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "level": self.level,
            "rarity": self.rarity,
            "vendor_value": self.vendor_value,
            "game_types": self.game_types,
            "flags": self.flags,
            "restrictions": self.restrictions,
            **self.details  # Merge in any type-specific details
        } 