from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class AccountNameHistoryItem(BaseModel):
    account_name: str
    valid_from: datetime
    valid_to: Optional[datetime]

class AccountSearchResult(BaseModel):
    id: int
    current_account_name: str
    has_user: bool
    guild_count: int
    name_history: List[AccountNameHistoryItem]

class AccountMergeRequest(BaseModel):
    old_account_id: int
    new_account_id: int

class AccountMergeResponse(BaseModel):
    success: bool
    message: str

class GuildMembershipInfo(BaseModel):
    guild_id: str
    guild_name: str
    rank: str
    joined: Optional[datetime]
    wvw_member: bool

class AccountDetail(BaseModel):
    id: int
    current_account_name: str
    created_at: datetime
    updated_at: datetime
    has_user: bool
    user_username: Optional[str]
    guilds: List[GuildMembershipInfo]
    name_history: List[AccountNameHistoryItem] 