from enum import Enum
from itertools import count

from fastapi import APIRouter, Depends, Query, HTTPException, status

from app.bootstrap.container import get_context_container
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.journal import JournalEventOut, MarkJournalReadRequest, JournalUnreadOut
from app.schemas.player import PlayerSchema
from app.entities.player import PlayerEntity
from .deps import get_http_player


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
                player = await container.player_service.find_by_account_id(access.account_id)
                if player is None:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Authentication failed"
                    )
                return LoginResponse(
                    access_token=access.access_token,
                    refresh_token=access.refresh_token,
                    user=PlayerSchema(
                        id=player.id,
                        name=player.name,
                        email=access.email,
                    ),
                )

    @router.get('/journal', response_model=list[JournalEventOut])
    async def list_journal(
        player: PlayerEntity = Depends(get_http_player),
        offset: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=100),
    ):
        async with get_context_container() as container:
            return await container.journal_service.list_by_user(player.id, offset, limit)

    @router.get('/journal/unread', response_model=JournalUnreadOut)
    async def unreaded_count(
        player: PlayerEntity = Depends(get_http_player)
    ):
        async with get_context_container() as container:
            unread = await container.journal_service.count_unread(player.id)
        return JournalUnreadOut(unread=unread) 

    @router.post('/journal/read', response_model=JournalUnreadOut)
    async def mark_journal_read(
        payload: MarkJournalReadRequest,
        player: PlayerEntity = Depends(get_http_player),
    ):
        async with get_context_container() as container:
            await container.journal_service.mark_readed_user_events(player.id, payload.ids)
            unread = await container.journal_service.count_unread(player.id)
        return JournalUnreadOut(unread=unread)

    return router
