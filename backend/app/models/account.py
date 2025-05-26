from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Account(Base):
    """
    Represents a Guild Wars 2 account with a stable internal ID (IUID).
    Account names can change, but the IUID remains constant.
    """
    __tablename__ = "accounts"

    # Primary key - Internal Unique ID (IUID)
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Current account name (e.g. "Lawton Campbell.9413")
    current_account_name = Column(String, unique=True, index=True, nullable=False)
    
    # How this account was added to the system
    account_source = Column(String, default="guild_sync")  # "guild_sync", "moderation", "api_key"
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    name_history = relationship("AccountNameHistory", back_populates="account", cascade="all, delete-orphan")
    memberships = relationship("GuildMembership", back_populates="account", cascade="all, delete-orphan")
    user = relationship("User", back_populates="account", uselist=False, cascade="all, delete-orphan")
    mod_actions = relationship("ModAction", back_populates="account", order_by="ModAction.created_at.desc()")
    standing = relationship("GuildStanding", back_populates="account", uselist=False, cascade="all, delete-orphan")
    
    @property
    def is_banned(self) -> bool:
        """Check if account has any active ban."""
        if not self.mod_actions:
            return False
        
        for action in self.mod_actions:
            if action.is_blocking:
                return True
        return False
    
    @property
    def active_punishments(self):
        """Get all active punishments."""
        if not self.mod_actions:
            return []
        
        return [
            action for action in self.mod_actions
            if action.is_active and not action.is_expired
        ]
    
    @property
    def ban_info(self):
        """Get current ban information if banned."""
        for action in self.mod_actions:
            if action.is_blocking:
                return {
                    "is_banned": True,
                    "ban_type": action.action_type,
                    "reason": action.reason,
                    "expires_at": action.expires_at,
                    "created_at": action.created_at,
                    "created_by": action.created_by.username if action.created_by else None
                }
        return {"is_banned": False}
    
    @property
    def current_points(self) -> int:
        """Get current point total."""
        if not self.standing:
            return 0
        return self.standing.current_points
    
    @property
    def is_disabled(self) -> bool:
        """Check if account is disabled due to points."""
        if not self.standing:
            return False
        return self.standing.is_disabled
    
    def to_dict(self):
        """Convert the account to a dictionary."""
        return {
            "id": self.id,
            "current_account_name": self.current_account_name,
            "account_source": self.account_source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_banned": self.is_banned,
            "is_disabled": self.is_disabled,
            "current_points": self.current_points,
            "name_history": [history.to_dict() for history in self.name_history],
            "guilds": [{
                "id": membership.guild_id,
                "rank": membership.rank,
                "joined": membership.joined.isoformat() if membership.joined else None,
                "wvw_member": membership.wvw_member
            } for membership in self.memberships]
        }
    
    @classmethod
    def get_or_create(cls, db_session, account_name: str, source: str = "guild_sync"):
        """Get an existing account by name or create a new one."""
        account = db_session.query(cls).filter(cls.current_account_name == account_name).first()
        if not account:
            account = cls(current_account_name=account_name, account_source=source)
            db_session.add(account)
            db_session.flush()
            
            # Add initial name history entry
            from .account_name_history import AccountNameHistory
            history_entry = AccountNameHistory(
                account_id=account.id,
                account_name=account_name,
                valid_from=account.created_at
            )
            db_session.add(history_entry)
            
            # Create initial standing
            from .guild_standing import GuildStanding
            standing = GuildStanding(account_id=account.id)
            db_session.add(standing)
            
            db_session.flush()
            
        return account
    
    def __repr__(self):
        return f"<Account(id={self.id}, current_account_name='{self.current_account_name}')>" 