from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class ModAction(Base):
    """
    Tracks all moderation actions taken against accounts.
    This includes warnings, bans, temporary bans, kicks, mutes, etc.
    """
    __tablename__ = "mod_actions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Account information
    account_id = Column(Integer, ForeignKey('accounts.id', ondelete='SET NULL'), nullable=True, index=True)
    account_name = Column(String, nullable=False, index=True)  # Always store the name at time of action
    
    # Action details
    action_type = Column(String, nullable=False, index=True)  # "ban", "temp_ban", "warning", "kick", "mute", etc.
    severity = Column(Integer, default=1)  # 1-5 scale for escalation tracking
    
    # Points system
    points_added = Column(Integer, nullable=True)  # Points added by this action
    violation_type = Column(String, nullable=True)  # Type of violation (maps to point values)
    auto_disabled_account = Column(Boolean, default=False)  # If this action caused auto-disable
    
    reason = Column(String, nullable=False)
    details = Column(Text, nullable=True)  # Additional context
    
    # Temporal fields
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=True, index=True)  # For temporary actions
    lifted_at = Column(DateTime, nullable=True)  # If manually lifted early
    
    # Who did it
    created_by_user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=False)
    lifted_by_user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Relationships
    account = relationship("Account", back_populates="mod_actions")
    created_by = relationship("User", foreign_keys=[created_by_user_id], backref="mod_actions_created")
    lifted_by = relationship("User", foreign_keys=[lifted_by_user_id], backref="mod_actions_lifted")
    
    def to_dict(self):
        """Convert the mod action to a dictionary."""
        return {
            "id": self.id,
            "account_id": self.account_id,
            "account_name": self.account_name,
            "action_type": self.action_type,
            "severity": self.severity,
            "points_added": self.points_added,
            "violation_type": self.violation_type,
            "auto_disabled_account": self.auto_disabled_account,
            "reason": self.reason,
            "details": self.details,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "lifted_at": self.lifted_at.isoformat() if self.lifted_at else None,
            "created_by_user_id": self.created_by_user_id,
            "created_by_username": self.created_by.username if self.created_by else None,
            "lifted_by_user_id": self.lifted_by_user_id,
            "lifted_by_username": self.lifted_by.username if self.lifted_by else None,
            "is_active": self.is_active,
            "is_expired": self.is_expired
        }
    
    @property
    def is_expired(self) -> bool:
        """Check if this action has expired."""
        if not self.is_active:
            return True
        if self.expires_at and self.expires_at <= datetime.utcnow():
            return True
        return False
    
    @property
    def is_blocking(self) -> bool:
        """Check if this action blocks access (bans)."""
        return self.action_type in ["ban", "temp_ban"] and not self.is_expired
    
    def lift(self, lifted_by_user_id: int):
        """Lift this moderation action."""
        self.is_active = False
        self.lifted_at = datetime.utcnow()
        self.lifted_by_user_id = lifted_by_user_id
    
    def __repr__(self):
        return f"<ModAction(id={self.id}, account='{self.account_name}', type='{self.action_type}', points={self.points_added}, active={self.is_active})>" 