from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class AccountNameHistory(Base):
    """
    Tracks the history of account name changes for a Guild Wars 2 account.
    Each entry represents a period when an account had a specific name.
    """
    __tablename__ = "account_name_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign key to the account
    account_id = Column(Integer, ForeignKey('accounts.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # The account name during this period
    account_name = Column(String, nullable=False, index=True)
    
    # Time period this name was valid
    valid_from = Column(DateTime, nullable=False, default=datetime.utcnow)
    valid_to = Column(DateTime, nullable=True)  # NULL means currently active
    
    # When this record was created
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship back to account
    account = relationship("Account", back_populates="name_history")
    
    def to_dict(self):
        """Convert the history entry to a dictionary."""
        return {
            "id": self.id,
            "account_id": self.account_id,
            "account_name": self.account_name,
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_to": self.valid_to.isoformat() if self.valid_to else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<AccountNameHistory(account_id={self.account_id}, name='{self.account_name}', valid_from={self.valid_from}, valid_to={self.valid_to})>" 