from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict

from .user import UserSchema


class AuthToken(BaseModel):
    token: str
    expired_at: datetime

class TokenSchema(BaseModel):
    user_id: int
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
    access_token: AuthToken
    refresh_token: AuthToken
    user: UserSchema

class LoginResponse(AccessSchema):
    model_config = ConfigDict(from_attributes=True)