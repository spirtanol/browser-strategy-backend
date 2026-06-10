from datetime import datetime, UTC, timedelta

from typing import Callable

from app.repositories.user import UserRepository, UserModel, UserEntity
from app.schemas.auth import TokenSchema, LoginCredentials, AccessSchema, UserSchema
from app.core.security import verify_password
from .token import TokenService, TokenInvalidError
from app.core.exceptions import AuthError


class AuthBadCredentials(AuthError):
    pass

class AuthService:
    def __init__(
        self, 
        user_repo: UserRepository,
        token_service: TokenService
    ):
        self._user_repo = user_repo
        self._token_service = token_service

    async def login_user(self, user: UserModel) -> AccessSchema:
        user.token_version += 1
        date = datetime.now(UTC)

        access_token, refresh_token = self._token_service.create_tokens(user.id, user.token_version)

        await self._user_repo.save_model(user)

        return AccessSchema(
            user=UserSchema.model_validate(user),
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def login_by_creds(self, creds: LoginCredentials) -> AccessSchema:
        user = await self._user_repo.find_model_by_email(creds.email)

        if user is None:
            raise AuthBadCredentials()

        if not verify_password(creds.password, user.password_hash):
            raise AuthBadCredentials()

        return await self.login_user(user)

    async def _check_token(self, token: str, token_type: str) -> tuple[UserEntity, TokenSchema]:
        try:
            payload = await self._token_service.check_token(token, token_type)
        except TokenInvalidError:
            raise AuthBadCredentials()

        user = await self._user_repo.find(payload.user_id)
        if not user:
            raise AuthBadCredentials()

        return user, payload

    async def check_access_token(self, token: str) -> tuple[UserEntity, TokenSchema]:
        return await self._check_token(token, 'access')

    async def logout(self, token: TokenSchema) -> None:
        await self._token_service.invalidate_token(token)

    async def logout_hard(self, user: UserModel) -> None:
        await self._token_service.invalidate_all_tokens(user.id, user.token_version)

    async def refresh_tokens(self, token: str) -> AccessSchema:
        user, token_schema = await self._check_token(token, 'refresh')
        await self.logout(token_schema)
        return await self.login_user(user)

    