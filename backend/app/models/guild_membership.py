from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

# Association table for the many-to-many relationship between accounts and guilds
guild_memberships = Table(
    'guild_memberships',
    Base.metadata,
    Column('account_id', Integer, ForeignKey('accounts.id', ondelete='CASCADE'), primary_key=True),
    Column('guild_id', String, ForeignKey('guilds.id', ondelete='CASCADE'), primary_key=True),
    Column('rank', String, nullable=False),  # Current rank name in this guild
    Column('joined', DateTime, nullable=True),  # Join date for this guild
    Column('wvw_member', Boolean, default=False)  # WvW representation status
)

class GuildMembership(Base):
    """Mapped class for the guild_memberships table to enable direct access to membership data"""
    __table__ = guild_memberships

    # Add relationships to both sides
    account = relationship("Account", back_populates="memberships")
    guild = relationship("Guild", back_populates="guild_memberships")

    def __repr__(self):
        return f"<GuildMembership(account_id={self.account_id}, guild_id='{self.guild_id}', rank='{self.rank}')>"

    @classmethod
    def add_or_update(cls, db_session, account_id: int, guild_id: str, member_data: dict):
        """Add or update a guild membership for an account."""
        try:
            # Parse the join date
            joined_date = None
            if member_data.get("joined"):
                joined_date = datetime.fromisoformat(member_data["joined"].replace('Z', '+00:00'))

            # Find existing membership
            membership = db_session.query(cls).filter(
                cls.account_id == account_id,
                cls.guild_id == guild_id
            ).first()

            if membership:
                # Update existing membership
                membership.rank = member_data["rank"]
                membership.joined = joined_date
                membership.wvw_member = member_data.get("wvw_member", False)
            else:
                # Create new membership
                membership = cls(
                    account_id=account_id,
                    guild_id=guild_id,
                    rank=member_data["rank"],
                    joined=joined_date,
                    wvw_member=member_data.get("wvw_member", False)
                )
                db_session.add(membership)
            
            db_session.flush()
            return membership
        except Exception as e:
            db_session.rollback()
            raise e 