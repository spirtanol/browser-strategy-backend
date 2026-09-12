from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict

from .player import PlayerSchema


class AuthToken(BaseModel):
    token: str
    expired_at: datetime

class TokenSchema(BaseModel):
    account_id: int
    token_type: str
    iat: datetime
    exp: datetime
    version: int

class LoginCredentials(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(LoginCredentials):
    pass

class AccessSchema(BaseModel):
    account_id: int
    email: str
    access_token: AuthToken
    refresh_token: AuthToken

class LoginResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_token: AuthToken
    refresh_token: AuthToken
    user: PlayerSchema
