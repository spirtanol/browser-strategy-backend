import asyncio
import logging
from enum import Enum
from typing import Optional

from pydantic import ValidationError
from fastapi import (
    APIRouter, 
    WebSocket, 
    WebSocketDisconnect, 
    Depends
)

from app.bootstrap.container import get_context_container
from app.schemas.commands import (
    GameCommandRequest,
    GameCommand,
    SelectShipCommand,
    SelectFleetCommand,
)
from .deps import get_ws_user, UserEntity
from app.schemas.fleet import FleetStateOut
from app.schemas.user import UserStateOut


logger = logging.getLogger("app.core.engine")

def create_ws_router(prefix: str, tags: list[str | Enum]):
    router = APIRouter(
        prefix=prefix, 
        tags=tags,
    )

    @router.websocket('/')
    async def connect(
        websocket: WebSocket,
        user: UserEntity = Depends(get_ws_user)
    ):
            async with get_context_container() as container:
                await websocket.accept()

                try:
                    pending = []
                    
                    fleets_last_state: dict[int, FleetStateOut] = {}
                    user_last_state: Optional[UserStateOut] = None
                    selected_fleet_id: Optional[int] = None

                    async def fleet_state_loop(fleet_id: int):
                        fleet = await container.client_fleet_service.find(fleet_id)
                        if fleet is None:
                            return

                        fleets_last_state[fleet.id] = fleet
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
                        nonlocal user_last_state
                        async for user_state in container.client_user_service.subscribe_to_updates(user_id, logger):
                            user_last_state = UserStateOut.model_validate_json(user_state)
                            await websocket.send_text(user_state)

                    async def client_command_loop():
                        nonlocal selected_fleet_id
                        try:
                            fleet_state_task = None
                            ship_state_task = None

                            while True:
                                data = await websocket.receive_json()
                                try:
                                    request = GameCommandRequest.model_validate(data)
                                    if request.action == 'select_fleet':
                                        select_command = SelectFleetCommand.model_validate(data)
                                        fleet_id = select_command.fleet_id

                                        if user_last_state is None:
                                            continue

                                        if fleet_id not in (fleet.id for fleet in user_last_state.fleets):
                                            continue

                                        if fleet_state_task:
                                            fleet_state_task.cancel()
                                            fleet_state_task = None

                                        if ship_state_task:
                                            ship_state_task.cancel()
                                            ship_state_task = None

                                        selected_fleet_id = fleet_id
                                        fleet_state_task = asyncio.create_task(fleet_state_loop(fleet_id))
                                    elif request.action == 'select_ship':
                                        select_command = SelectShipCommand.model_validate(data)
                                        ship_id = select_command.ship_id
                                        
                                        if selected_fleet_id is None:
                                            continue

                                        fleet_last_state = fleets_last_state.get(selected_fleet_id, None)
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
                            asyncio.create_task(client_command_loop()),
                        ],
                        return_when=asyncio.FIRST_COMPLETED,
                    )
                finally:
                    for task in pending:
                        task.cancel()
        
    return router
