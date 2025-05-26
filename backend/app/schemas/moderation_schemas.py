from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List, Dict
from app.config.moderation import MOD_ACTION_TYPES

class ModActionCreateRequest(BaseModel):
    account_name: str = Field(..., description="Account name to take action against")
    action_type: str = Field(..., description="Type of moderation action")
    reason: str = Field(..., min_length=3, description="Reason for the action")
    duration_hours: Optional[int] = Field(None, ge=1, description="Duration in hours for temporary actions")
    severity: Optional[int] = Field(None, ge=1, le=5, description="Override default severity (1-5)")
    details: Optional[str] = Field(None, description="Additional details or context")
    
    @validator('action_type')
    def validate_action_type(cls, v):
        if v not in MOD_ACTION_TYPES:
            raise ValueError(f"Invalid action type. Must be one of: {', '.join(MOD_ACTION_TYPES.keys())}")
        return v

class ModActionLiftRequest(BaseModel):
    mod_action_id: int = Field(..., description="ID of the mod action to lift")

class ModActionResponse(BaseModel):
    id: int
    account_id: Optional[int]
    account_name: str
    action_type: str
    severity: int
    reason: str
    details: Optional[str]
    created_at: datetime
    expires_at: Optional[datetime]
    lifted_at: Optional[datetime]
    created_by_user_id: int
    created_by_username: Optional[str]
    lifted_by_user_id: Optional[int]
    lifted_by_username: Optional[str]
    is_active: bool
    is_expired: bool

class AccountStandingResponse(BaseModel):
    allowed: bool
    is_banned: bool
    active_blocks: List[Dict]
    warnings: List[Dict]
    account_id: Optional[int]

class ModActionHistoryResponse(BaseModel):
    actions: List[ModActionResponse]
    total: int

class ModActionTypeInfo(BaseModel):
    name: str
    severity: int
    blocks_access: bool
    default_duration: Optional[int]
    description: str
    color: str

class ModActionTypesResponse(BaseModel):
    action_types: Dict[str, ModActionTypeInfo] 