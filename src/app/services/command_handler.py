from .ship import ShipService
from .lifestate.registry import LifeStateRegistry
from app.schemas.commands import GameCommand


class CommandHandlerService:
    def __init__(self, ship_service: ShipService, life_state_registry: LifeStateRegistry):
        self.ship_service = ship_service
        self._life_state_registry = life_state_registry

    async def handle(self, command: GameCommand):
        match command.action:
            case 'feed':
                ship = await self.ship_service.find(command.params.get('ship_id', 0))
                if ship:
                    amount = command.params.get('amount', 0)
                    if amount > 0:
                        from app.defs.items import MEAL
                        ship.storage.push(MEAL, 10)
            case 'alive_ship':
                ship = await self.ship_service.find(command.params.get('ship_id', 0))
                if ship:
                    self._life_state_registry.add_ship(ship.id)
            case _:
                pass