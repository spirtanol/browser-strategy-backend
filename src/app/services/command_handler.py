from .ship import ShipService
from app.schemas.commands import GameCommand


class CommandHandlerService:
    def __init__(self, ship_service: ShipService):
        self.ship_service = ship_service

    async def handle(self, command: GameCommand):
        if command.action == 'feed':
            amount = command.params.get('amount', 0)
            if amount > 0:
                from app.defs.items import MEAL
                ship = await self.ship_service.find(command.entity_id)
                ship.storage.push(MEAL, 10)
                await self.ship_service.flush([ship])
            