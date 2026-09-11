from enum import Enum
from itertools import count

from fastapi import APIRouter, Depends, Query

from app.bootstrap.container import get_context_container
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.journal import JournalEventOut, MarkJournalReadRequest, JournalUnreadOut
from app.entities.user import UserEntity
from .deps import get_http_user


def create_api_router(prefix: str, tags: list[str | Enum]) -> APIRouter:
    router = APIRouter(
        prefix=prefix, 
        tags=tags,
    )

    @router.post('/auth/login', response_model=LoginResponse)
    async def login(payload: LoginRequest):
        async with get_context_container() as container:
            async with container.transaction():
                access = await container.auth_service.login_by_creds(payload)
        return LoginResponse.model_validate(access)

    @router.get('/journal', response_model=list[JournalEventOut])
    async def list_journal(
        user: UserEntity = Depends(get_http_user),
        offset: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=100),
    ):
        async with get_context_container() as container:
            return await container.journal_service.list_by_user(user.id, offset, limit)

    @router.get('/journal/unread', response_model=JournalUnreadOut)
    async def unreaded_count(
        user: UserEntity = Depends(get_http_user)
    ):
        async with get_context_container() as container:
            unread = await container.journal_service.count_unread(user.id)
        return JournalUnreadOut(unread=unread) 

    @router.post('/journal/read', response_model=JournalUnreadOut)
    async def mark_journal_read(
        payload: MarkJournalReadRequest,
        user: UserEntity = Depends(get_http_user),
    ):
        async with get_context_container() as container:
            await container.journal_service.mark_readed_user_events(user.id, payload.ids)
            unread = await container.journal_service.count_unread(user.id)
        return JournalUnreadOut(unread=unread)

    return router
