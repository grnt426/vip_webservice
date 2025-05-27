from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class LotteryEntryResponse(BaseModel):
    id: int
    guild_id: str
    account_id: int
    week_number: int
    year: int
    lots: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LotteryWinnerResponse(BaseModel):
    id: int
    guild_id: str
    account_id: int
    week_number: int
    year: int
    prize_amount: int
    paid_out: bool
    created_at: datetime
    paid_at: Optional[datetime]

    class Config:
        from_attributes = True

class LotteryStats(BaseModel):
    current_pot: int
    current_entries_count: int
    past_winners: List[LotteryWinnerResponse]

    class Config:
        from_attributes = True 