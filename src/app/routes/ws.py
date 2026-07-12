import asyncio
import logging

from pydantic import ValidationError
from fastapi import (
    APIRouter, 
    status, 
    WebSocket, 
    WebSocketDisconnect, 
    Path,
    Depends
)

from app.bootstrap.container import get_context_container
from app.core.exceptions import ShipNotFoundError, AuthError
from app.schemas.ship import ShipStateOut
from app.schemas.commands import GameCommandRequest, GameCommand
from .deps import get_ws_user, UserEntity
from app.schemas.user import UserStateOut


logger = logging.getLogger("app.core.engine")

def create_ws_router(prefix: str, tags: list[str]):
    router = APIRouter(
        prefix=prefix, 
        tags=tags,
    )

    @router.websocket('/{ship_id}')
    async def connect(
        websocket: WebSocket,
        ship_id: int = Path(),
        user: UserEntity = Depends(get_ws_user)
    ):
            async with get_context_container() as container:
                async with container.transaction():
                    ship = await container.client_ship_service.find(ship_id)
                    if ship is None:
                        raise ShipNotFoundError(ship_id)
                    
                    if ship.owner_id != user.id:
                        raise AuthError()

                await websocket.accept()

                try:
                    redis_client = container.get_redis()

                    async def ship_state_loop():
                        async for ship in container.client_ship_service.subscribe_to_updates(ship_id, logger):
                            ship_dto = ShipStateOut.from_entity(ship)
                            await websocket.send_text(ship_dto.model_dump_json())

                    user_id = user.id
                    async def user_state_loop():
                        async for user in container.client_user_service.subscribe_to_updates(user_id, logger):
                            user_dto = UserStateOut.from_entity(user)
                            await websocket.send_text(user_dto.model_dump_json())

                    async def client_command_loop():
                        try:
                            while True:
                                data = await websocket.receive_json()
                                try:
                                    request = GameCommandRequest.model_validate(data)
                                    command = GameCommand(
                                        action=request.action,
                                        params=request.params
                                    )
                                    async with container.transaction():
                                        await container.command_dispatcher_service.dispatch(command, user)
                                except ValidationError as e:
                                    logger.exception(f'Ошибка парса команды {str(e)}')
                                except Exception as e:
                                    logger.exception(f'Ошибка обработки команды {str(e)}')
                        except WebSocketDisconnect:
                            pass

                    done, pending = await asyncio.wait(
                        [
                            asyncio.create_task(user_state_loop()),
                            asyncio.create_task(ship_state_loop()),
                            asyncio.create_task(client_command_loop()),
                        ],
                        return_when=asyncio.FIRST_COMPLETED,
                    )
                except ShipNotFound:
                    await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
                finally:
                    for task in pending:
                        task.cancel()
        
    return router