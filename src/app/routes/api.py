from fastapi import APIRouter, status

from app.bootstrap.container import get_context_container
from app.core.exceptions import ShipNotFound
from app.schemas.ship import ShipInfoResponse
from app.schemas.commands import GameCommandRequest
from app.core.exceptions import ShipNotFound
from app.defs.items import NetworkResource


def create_api_router(prefix: str, tags: list[str]) -> APIRouter:
    router = APIRouter(
        prefix=prefix, 
        tags=tags,
    )

    @router.get('/ship/{id}', response_model=ShipInfoResponse)
    async def get_ship_status(id: int):
        async with get_context_container() as container:
            ship = await container.client_ship_service.find(id)
            if ship is None:
                raise ShipNotFound(id)
            
            return ShipInfoResponse(
                id=ship.id,
                name=ship.name,
                crew=ship.crew,
                hunger=ship.hunger,
                storage=ship.storage.get_contents(),
                weight=ship.weight,
                floatage=ship.floatage,
                hp=ship.hp,
                power=(ship.get_consumers(NetworkResource.Power).value, ship.get_suppliers(NetworkResource.Power).value)
            )

    @router.post('/command', status_code=status.HTTP_204_NO_CONTENT)
    async def command(payload: GameCommandRequest):
        async with get_context_container() as container:
            ship_id = payload.params.get('ship_id', 0)
            ship = await container.client_ship_service.find(ship_id)
            if not ship:
                raise ShipNotFound(ship_id)

            await container.command_dispatcher_service.dispatch(
                command=payload
            )

    return router
