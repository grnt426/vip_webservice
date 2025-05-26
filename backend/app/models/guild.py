from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base
from .guild_membership import guild_memberships, GuildMembership
from app.utils.name_utils import split_account_name, get_short_guild_name
from .guild_logs import (
    KickLog, InviteLog, InviteDeclineLog, JoinLog, RankChangeLog,
    StashLog, TreasuryLog, MotdLog, UpgradeLog, InfluenceLog, MissionLog
)

class Guild(Base):
    __tablename__ = "guilds"

    # Primary guild data
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    tag = Column(String, nullable=False)
    level = Column(Integer, nullable=True, default=0)  # Guild level is not always provided by the API
    motd = Column(String)  # Message of the day
    
    # Guild resources
    influence = Column(Integer, default=0)
    aetherium = Column(Integer, default=0)
    resonance = Column(Integer, default=0)
    favor = Column(Integer, default=0)

    # Metadata
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_log_id = Column(Integer, default=0)  # Track the last log entry we've seen

    # Relationships
    emblem = relationship("GuildEmblem", uselist=False, back_populates="guild", cascade="all, delete-orphan")
    
    # Log relationships
    kick_logs = relationship(KickLog, back_populates="guild", cascade="all, delete-orphan")
    invite_logs = relationship(InviteLog, back_populates="guild", cascade="all, delete-orphan")
    invite_decline_logs = relationship(InviteDeclineLog, back_populates="guild", cascade="all, delete-orphan")
    join_logs = relationship(JoinLog, back_populates="guild", cascade="all, delete-orphan")
    rank_change_logs = relationship(RankChangeLog, back_populates="guild", cascade="all, delete-orphan")
    stash_logs = relationship(StashLog, back_populates="guild", cascade="all, delete-orphan")
    treasury_logs = relationship(TreasuryLog, back_populates="guild", cascade="all, delete-orphan")
    motd_logs = relationship(MotdLog, back_populates="guild", cascade="all, delete-orphan")
    upgrade_logs = relationship(UpgradeLog, back_populates="guild", cascade="all, delete-orphan")
    influence_logs = relationship(InfluenceLog, back_populates="guild", cascade="all, delete-orphan")
    mission_logs = relationship(MissionLog, back_populates="guild", cascade="all, delete-orphan")
    
    # Direct access to membership data
    guild_memberships = relationship(
        "GuildMembership",
        back_populates="guild",
        primaryjoin="Guild.id == GuildMembership.guild_id",
        cascade="all, delete-orphan"
    )
    ranks = relationship("GuildRank", back_populates="guild", cascade="all, delete-orphan")

    def to_dict(self):
        """Convert the guild model to a dictionary matching the GW2 API response format."""
        # Get member data including their rank and join date for this guild
        member_data = []
        for membership in self.guild_memberships:
            # Access the account through the membership
            account = membership.account
            display_name, full_name = split_account_name(account.current_account_name)
            member_data.append({
                "name": display_name,
                "full_name": full_name,
                "account_id": account.id,  # Include the internal ID
                "rank": membership.rank,
                "joined": membership.joined.isoformat() if membership.joined else None,
                "wvw_member": membership.wvw_member
            })

        return {
            "id": self.id,
            "name": self.name,
            "short_name": get_short_guild_name(self.name),
            "tag": self.tag,
            "level": self.level,
            "motd": self.motd,
            "influence": self.influence,
            "aetherium": self.aetherium,
            "resonance": self.resonance,
            "favor": self.favor,
            "emblem": self.emblem.to_dict() if self.emblem else None,
            "members": member_data,
            "ranks": [rank.to_dict() for rank in self.ranks] if self.ranks else [],
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "last_log_id": self.last_log_id
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