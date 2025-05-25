from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import bcrypt
import hashlib

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # In-game name, used for login, must be unique
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    # SHA-256 hash of the API key, must be unique
    api_key_hash = Column(String, unique=True, nullable=False)
    
    # Link to the GuildMember, ensuring one User per GuildMember
    guild_member_name = Column(String, ForeignKey('guild_members.name', ondelete='CASCADE'), unique=True, nullable=False)
    
    roles = Column(JSON, nullable=False, default=list)  # e.g., ['admin', 'officer']
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False) # Site-level superuser

    # Relationship to GuildMember
    guild_member = relationship("GuildMember", back_populates="user_account")

    def set_password(self, password: str):
        """Hashes the password using bcrypt and stores it."""
        salt = bcrypt.gensalt()
        self.hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Checks if the provided password matches the stored hash."""
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))

    def set_api_key(self, api_key: str):
        """Hashes the API key using SHA-256 and stores it."""
        self.api_key_hash = hashlib.sha256(api_key.encode('utf-8')).hexdigest()

    def to_dict(self):
        """Converts the User model to a dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "roles": self.roles,
            "guild_member_name": self.guild_member_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser
        }

    def __repr__(self):
        return f"<User(username='{self.username}', guild_member_name='{self.guild_member_name}')>" 