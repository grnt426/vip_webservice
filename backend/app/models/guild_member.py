from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

# Association table for the many-to-many relationship between accounts and guilds
guild_memberships = Table(
    'guild_memberships',
    Base.metadata,
    Column('account_name', String, ForeignKey('guild_members.name', ondelete='CASCADE'), primary_key=True),
    Column('guild_id', String, ForeignKey('guilds.id', ondelete='CASCADE'), primary_key=True),
    Column('rank', String, nullable=False),  # Current rank name in this guild
    Column('joined', DateTime, nullable=True),  # Join date for this guild
    Column('wvw_member', Boolean, default=False)  # WvW representation status
)

class GuildMembership(Base):
    """Mapped class for the guild_memberships table to enable direct access to membership data"""
    __table__ = guild_memberships

    # Add relationships to both sides
    member = relationship("GuildMember", back_populates="memberships")
    guild = relationship("Guild", back_populates="guild_memberships")

class GuildMember(Base):
    """
    Represents a Guild Wars 2 account that can be a member of multiple guilds.
    The actual guild memberships are stored in the guild_memberships association table.
    """
    __tablename__ = "guild_members"

    # Primary key
    name = Column(String, primary_key=True)  # Account name (e.g. "Lawton Campbell.9413")

    # Relationships
    guilds = relationship(
        "Guild",
        secondary=guild_memberships,
        back_populates="members",
        overlaps="memberships",
        viewonly=True,  # Make this relationship read-only since we'll write through memberships
    )
    
    # Direct access to membership data
    memberships = relationship(
        "GuildMembership",
        back_populates="member",
        primaryjoin="GuildMember.name == GuildMembership.account_name",
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        """Convert the member to a dictionary with all guild memberships."""
        return {
            "name": self.name,
            "guilds": [{
                "id": membership.guild_id,
                "rank": membership.rank,
                "joined": membership.joined.isoformat() if membership.joined else None,
                "wvw_member": membership.wvw_member
            } for membership in self.memberships]
        }

    @classmethod
    def get_or_create(cls, db_session, account_name: str):
        """Get an existing member or create a new one."""
        member = db_session.query(cls).filter(cls.name == account_name).first()
        if not member:
            member = cls(name=account_name)
            db_session.add(member)
            db_session.flush()  # Ensure the member is created before returning
        return member

    @classmethod
    def add_guild_membership(cls, db_session, account_name: str, guild_id: str, member_data: dict):
        """Add or update a guild membership for an account."""
        try:
            # Get or create the member
            member = cls.get_or_create(db_session, account_name)

            # Parse the join date
            joined_date = None
            if member_data.get("joined"):
                joined_date = datetime.fromisoformat(member_data["joined"].replace('Z', '+00:00'))

            # Find existing membership
            membership = db_session.query(GuildMembership).filter(
                GuildMembership.account_name == account_name,
                GuildMembership.guild_id == guild_id
            ).first()

            if membership:
                # Update existing membership
                membership.rank = member_data["rank"]
                membership.joined = joined_date
                membership.wvw_member = member_data.get("wvw_member", False)
            else:
                # Create new membership
                membership = GuildMembership(
                    account_name=account_name,
                    guild_id=guild_id,
                    rank=member_data["rank"],
                    joined=joined_date,
                    wvw_member=member_data.get("wvw_member", False)
                )
                db_session.add(membership)
            
            db_session.flush()
            return member
        except Exception as e:
            db_session.rollback()
            raise e 