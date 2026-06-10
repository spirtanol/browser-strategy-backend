from datetime import datetime, UTC, timedelta

from typing import Callable

from app.core.db import Redis
from app.core.exceptions import TokenInvalidError
from app.schemas.auth import TokenSchema, AuthToken
from app.core.security import TokenDecodeError, decode_token, create_token


class TokenService:
    def __init__(
        self,
        redis_factory: Callable[[], Redis],
        access_ttl: int,
        refresh_ttl: int,
        secret_key: str,
        token_alg: str
    ):
        self._redis_factory = redis_factory
        self._access_ttl = access_ttl
        self._refresh_ttl = refresh_ttl
        self._token_secret_key = secret_key
        self._token_alg = token_alg

    async def check_token(self, token: str, token_type: str) -> TokenSchema:
        try:
            payload = decode_token(self._token_alg, self._token_secret_key, token)
        except TokenDecodeError:
            raise TokenInvalidError('Invalid signature or format')

        if token_type != payload.token_type:
            raise TokenInvalidError('Wrong token type')

        redis = self._redis_factory()

        blocked_version = await redis.get(f'token_block:{payload.user_id}')

        if ((blocked_version is not None and payload.version <= int(blocked_version))
            or await redis.exists(f'token_block:{payload.user_id}:{payload.version}')):
            raise TokenInvalidError('Token is blacklisted')
        
        return payload

    def create_tokens(self, user_id: int, version: int) -> tuple[AuthToken, AuthToken]:
        date = datetime.now(UTC)

        token_schema = TokenSchema(
            user_id=user_id,
            token_type='access',
            iat=date,
            exp=date + timedelta(minutes=self._access_ttl),
            version=version
        )
        access_token = create_token(alg=self._token_alg, secret_key=self._token_secret_key, dto=token_schema)
        
        token_schema.token_type = 'refresh'
        token_schema.exp = date + timedelta(minutes=self._refresh_ttl)
        refresh_token = create_token(alg=self._token_alg, secret_key=self._token_secret_key, dto=token_schema)
        
        return access_token, refresh_token

    async def invalidate_token(self, token: TokenSchema):
        redis = self._redis_factory()
        await redis.set(f'token_block:{token.user_id}:{token.version}', 1, exat=int(token.exp.timestamp()))

    async def invalidate_all_tokens(self, user_id: int, version: int):
        redis = self._redis_factory()
        await redis.set(f'token_block:{user_id}', version, ex=self._refresh_ttl * 60)
