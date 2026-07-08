from fastapi import Query, status, HTTPException
import logging

from app.bootstrap.container import get_context_container
from app.entities.user import UserEntity
from app.core.exceptions import UserNotFound, AuthError


logger = logging.getLogger("app.core.engine")

async def get_ws_user(
    token: str = Query(...)
) -> UserEntity:
    async with get_context_container() as container:
        async with container.transaction():
            try:
                user, _ = await container.auth_service.check_access_token(token)
                return user
            except AuthError:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Authentication failed"
                )
            except Exception as e:
                logger.exception('Не удалось получить пользователя из токена')
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error"
                )