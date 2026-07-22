from datetime import datetime
from typing import Any

from passlib.context import CryptContext
from jose import jwt, JWTError
from pydantic import ValidationError

from app.schemas.auth import TokenSchema, AuthToken


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenDecodeError(Exception):
    pass

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password[:72])

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_token(alg: str, secret_key: str, dto: TokenSchema) -> AuthToken:
    to_encode: dict[str, Any] = {
        "sub": str(dto.user_id), 
        "iat": int(dto.iat.timestamp()), 
        "exp": int(dto.exp.timestamp()),
        "type": dto.token_type,
        "v": dto.version
    }
    return AuthToken(
        token=jwt.encode(to_encode, secret_key, algorithm=alg),
        expired_at=dto.exp
    )

def decode_token(alg: str, secret_key: str, token: str) -> TokenSchema:
    try:
        data = jwt.decode(token, secret_key, algorithms=[alg])
        return TokenSchema(
            user_id=data['sub'],
            iat=datetime.fromtimestamp(float(data['iat'])),
            exp=datetime.fromtimestamp(float(data['exp'])),
            token_type=data['type'],
            version=data['v']
        )
    except (JWTError, ValidationError) as exp:
        raise TokenDecodeError(str(exp))