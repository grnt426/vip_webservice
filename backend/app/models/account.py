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
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    name_history = relationship("AccountNameHistory", back_populates="account", cascade="all, delete-orphan")
    memberships = relationship("GuildMembership", back_populates="account", cascade="all, delete-orphan")
    user = relationship("User", back_populates="account", uselist=False, cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert the account to a dictionary."""
        return {
            "id": self.id,
            "current_account_name": self.current_account_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "name_history": [history.to_dict() for history in self.name_history],
            "guilds": [{
                "id": membership.guild_id,
                "rank": membership.rank,
                "joined": membership.joined.isoformat() if membership.joined else None,
                "wvw_member": membership.wvw_member
            } for membership in self.memberships]
        }
    
    @classmethod
    def get_or_create(cls, db_session, account_name: str):
        """Get an existing account by name or create a new one."""
        account = db_session.query(cls).filter(cls.current_account_name == account_name).first()
        if not account:
            account = cls(current_account_name=account_name)
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
            db_session.flush()
            
        return account
    
    def __repr__(self):
        return f"<Account(id={self.id}, current_account_name='{self.current_account_name}')>" 