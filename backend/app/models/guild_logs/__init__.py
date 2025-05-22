from .base import BaseGuildLog
from .kick import KickLog
from .invite import InviteLog
from .invite_decline import InviteDeclineLog
from .join import JoinLog
from .rank_change import RankChangeLog
from .stash import StashLog
from .treasury import TreasuryLog
from .motd import MotdLog
from .upgrade import UpgradeLog
from .influence import InfluenceLog
from .mission import MissionLog

# Map of log types to their corresponding model classes
LOG_TYPE_MAP = {
    "kick": KickLog,
    "invited": InviteLog,
    "invite_declined": InviteDeclineLog,
    "joined": JoinLog,
    "rank_change": RankChangeLog,
    "stash": StashLog,
    "treasury": TreasuryLog,
    "motd": MotdLog,
    "upgrade": UpgradeLog,
    "influence": InfluenceLog,
    "mission": MissionLog
}

def create_log_entry(guild_id: str, log_entry: dict) -> BaseGuildLog:
    """Factory function to create the appropriate log entry based on type"""
    log_type = log_entry["type"]
    if log_type not in LOG_TYPE_MAP:
        raise ValueError(f"Unknown log type: {log_type}")
        
    return LOG_TYPE_MAP[log_type].from_api_response(guild_id, log_entry) 