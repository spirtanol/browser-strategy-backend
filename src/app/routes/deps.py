from fastapi import Query, status, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import logging

from app.bootstrap.container import get_context_container
from app.entities.player import PlayerEntity
from app.core.exceptions import AuthError


logger = logging.getLogger("app.core.engine")

_bearer = HTTPBearer()


async def _player_from_token(token: str) -> PlayerEntity:
    async with get_context_container() as container:
        try:
            payload = await container.auth_service.check_access_token(token)
            player = await container.player_service.find_by_account_id(payload.account_id)
        except AuthError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Authentication failed"
            )
        except Exception:
            logger.exception('Не удалось получить игрока из токена')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

        if player is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Authentication failed"
            )
        return player


async def get_ws_player(
    token: str = Query(...)
) -> PlayerEntity:
    return await _player_from_token(token)


async def get_http_player(
    creds: HTTPAuthorizationCredentials = Depends(_bearer),
) -> PlayerEntity:
    return await _player_from_token(creds.credentials)
