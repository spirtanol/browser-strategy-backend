from app.repositories.account import AccountRepository
from app.models.account import AccountModel
from app.schemas.auth import TokenSchema, LoginCredentials, AccessSchema
from app.core.security import verify_password
from .token import TokenService, TokenInvalidError
from app.core.exceptions import AuthError


class AuthBadCredentials(AuthError):
    pass


class AuthService:
    def __init__(
        self,
        account_repo: AccountRepository,
        token_service: TokenService
    ):
        self._account_repo = account_repo
        self._token_service = token_service

    async def login_user(self, account: AccountModel) -> AccessSchema:
        account.token_version += 1

        access_token, refresh_token = self._token_service.create_tokens(account.id, account.token_version)

        await self._account_repo.save(account)

        return AccessSchema(
            account_id=account.id,
            email=account.email,
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def login_by_creds(self, creds: LoginCredentials) -> AccessSchema:
        account = await self._account_repo.find_by_email(creds.email)

        if account is None:
            raise AuthBadCredentials()

        if not verify_password(creds.password, account.password_hash):
            raise AuthBadCredentials()

        return await self.login_user(account)

    async def _check_token(self, token: str, token_type: str) -> TokenSchema:
        try:
            return await self._token_service.check_token(token, token_type)
        except TokenInvalidError:
            raise AuthBadCredentials()

    async def check_access_token(self, token: str) -> TokenSchema:
        return await self._check_token(token, 'access')

    async def logout(self, token: TokenSchema) -> None:
        await self._token_service.invalidate_token(token)

    async def logout_hard(self, account: AccountModel) -> None:
        await self._token_service.invalidate_all_tokens(account.id, account.token_version)

    async def refresh_tokens(self, token: str) -> AccessSchema:
        token_schema = await self._check_token(token, 'refresh')
        account = await self._account_repo.find(token_schema.account_id)
        if account is None:
            raise AuthBadCredentials()
        await self.logout(token_schema)
        return await self.login_user(account)
