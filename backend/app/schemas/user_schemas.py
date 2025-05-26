from pydantic import BaseModel, constr
from typing import List, Optional

class APIKeyValidateRequest(BaseModel):
    api_key: constr(min_length=72, max_length=72) # GW2 API keys are 72 characters

class APIKeyValidateResponse(BaseModel):
    username: str # This will be the GuildMember.name
    message: str

class UserCreateRequest(BaseModel):
    api_key: constr(min_length=72, max_length=72)
    password: str
    username: str # GuildMember.name, pre-validated

class UserResponse(BaseModel):
    id: int
    username: str
    roles: List[str]
    is_active: bool
    is_superuser: bool

    class Config:
        orm_mode = True 