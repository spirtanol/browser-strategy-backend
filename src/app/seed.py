import asyncio

from app.bootstrap.container import get_context_container
from app.services.ship import ShipService, ShipEntity
from app.defs.items import MEAL, FUEL_BARREL
from app.entities.modules.factory import module_factory, ModuleDefs
from app.core.disposer import dispose


async def seed_world(ship_service: ShipService):
    ship = ShipEntity()
    ship.name = 'Nostromo'

    # Создаем модули корабля
    for i in range(10):
        ship.add_module(module_factory(ModuleDefs.HULL.name))
    ship.add_module(module_factory(ModuleDefs.GENERATOR.name))
    
    ship.crew = 10
    ship.storage.push(MEAL, 100)
    ship.storage.push(FUEL_BARREL, 10)

    await ship_service.add(ship)


if __name__ == "__main__":
    async def _run():
        try:
            async with get_context_container() as container:
                if await container.ship_service.is_empty():
                    await seed_world(container.ship_service)
                    print('Корабль создан')
                else:
                    print('Корабль уже существует')
        finally:
            await dispose()
    asyncio.run(_run())
