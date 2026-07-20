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
from app.core.exceptions import ShipNotFoundError, AuthError, FleetNotFoundError
from app.schemas.ship import ShipDetailInfoOut
from app.schemas.commands import GameCommandRequest, GameCommand, SelectShipCommand
from .deps import get_ws_user, UserEntity
from app.schemas.fleet import FleetStateOut


logger = logging.getLogger("app.core.engine")

def create_ws_router(prefix: str, tags: list[str]):
    router = APIRouter(
        prefix=prefix, 
        tags=tags,
    )

    @router.websocket('/{fleet_id}')
    async def connect(
        websocket: WebSocket,
        fleet_id: int = Path(),
        user: UserEntity = Depends(get_ws_user)
    ):
            async with get_context_container() as container:
                async with container.transaction():
                    fleet = await container.client_fleet_service.find(fleet_id)
                    if fleet is None:
                        raise FleetNotFoundError(fleet_id)
                    
                    if fleet.owner_id != user.id:
                        raise AuthError()

                await websocket.accept()

                try:
                    redis_client = container.get_redis()
                    
                    fleets_last_state: dict[int, FleetStateOut] = {
                        fleet.id: fleet
                    }
                    async def fleet_state_loop():
                        await websocket.send_text(fleet.model_dump_json())

                        async for fleet_state in container.client_fleet_service.subscribe_to_updates(fleet_id, logger):
                            dto = FleetStateOut.model_validate_json(fleet_state)
                            fleets_last_state[dto.id] = dto
                            await websocket.send_text(fleet_state)

                    async def ship_state_loop(ship_id: int):
                        async for ship_state in container.client_ship_service.subscribe_to_updates(ship_id, logger):
                            await websocket.send_text(ship_state)

                    user_id = user.id
                    async def user_state_loop():
                        async for user_state in container.client_user_service.subscribe_to_updates(user_id, logger):
                            await websocket.send_text(user_state)

                    async def client_command_loop():
                        try:
                            ship_state_task = None

                            while True:
                                data = await websocket.receive_json()
                                try:
                                    request = GameCommandRequest.model_validate(data)
                                    if request.action == 'select_ship':
                                        select_command = SelectShipCommand.model_validate(data)
                                        ship_id = select_command.ship_id
                                        
                                        fleet_last_state = fleets_last_state.get(fleet_id, None)
                                        if fleet_last_state is None:
                                            continue

                                        if ship_id not in (ship.id for ship in fleet_last_state.ships):
                                            continue

                                        if ship_state_task:
                                            ship_state_task.cancel()
                                            ship_state_task = None

                                        ship_state_task = asyncio.create_task(ship_state_loop(ship_id))
                                    else:
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
                            asyncio.create_task(fleet_state_loop()),
                            asyncio.create_task(client_command_loop()),
                        ],
                        return_when=asyncio.FIRST_COMPLETED,
                    )
                except FleetNotFoundError:
                    await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
                finally:
                    for task in pending:
                        task.cancel()
        
    return router