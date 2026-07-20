import asyncio

from app.bootstrap.container import get_context_container, Container
from app.services.market import MarketService, CreateMarketOrderSchema
from app.entities.ship import ShipEntity
from app.entities.platform import PlatformEntity
from app.entities.site import SiteEntity
from app.entities.fleet import FleetEntity
from app.defs import modules as ModuleDefs, items as ItemDefs
from app.entities.ship_modules import factory as ModuleFactory
from app.schemas.user import CreateUserSchema, CreateNpcSchema
from app.core.disposer import dispose
from app.defs.enums import MarketOrderType
from app.defs.deposites import BaseRestrictions, SiteContent
from app.defs.ship_hull import BASE_HULL


async def seed_world(container: Container):
    async with container.transaction():
        # Создаем npc
        create_npc_dto = CreateNpcSchema(name='NPC')

        npc_user = await container.user_service.create_npc(create_npc_dto)

        # Создаем платформу
        platform = PlatformEntity()
        platform.name = 'The Platform'
        platform.owner_id = npc_user.id
        platform.x = 2.0
        platform.y = 1.0
        await container.platform_service.save(platform)

        # Создаем рыбное место
        fish_site = SiteEntity(restriction=BaseRestrictions.get(SiteContent.Fish))
        fish_site.x = 2.0
        fish_site.y = -1.0
        await container.site_service.save(fish_site)

        # Создаем пользователя
        create_user_dto = CreateUserSchema(
            name='player 1',
            email='player@test.com',
            password='12qwaszx',
            is_npc=False
        )

        user = await container.user_service.create(create_user_dto)
        user.money = 1000
        await container.user_service.save(user)

        # Создаем флотилию
        fleet = FleetEntity()
        fleet.owner_id = user.id
        fleet.name = 'Fleet 1'
        fleet.pos.xy(0.1, 0.0)
        await container.fleet_service.save(fleet)

        # Создаем корабль
        for i in range(2):
            fishing_ship = ShipEntity()
            fishing_ship.name = f'Blue Shrimp {i + 1}'
            fleet.add_ship(fishing_ship)

            # Создаем модули корабля
            fishing_ship.hull.hull_config = BASE_HULL
            fishing_ship.hull.size = 1
            
            fishing_ship.add_module(ModuleFactory.create(ModuleDefs.BaseGenerator.name, fishing_ship.get_counter(), active=True))
            fishing_ship.add_module(ModuleFactory.create(ModuleDefs.BaseEngine.name, fishing_ship.get_counter(), active=True))
            fishing_ship.add_module(ModuleFactory.create(ModuleDefs.FishNet.name, fishing_ship.get_counter(), active=True))
            
            fishing_ship.crew = 10
            await container.ship_service.save(fishing_ship)

        cargo_ship = ShipEntity()
        cargo_ship.name = 'Cargo Ship'
        fleet.add_ship(cargo_ship)

        cargo_ship.hull.hull_config = BASE_HULL
        cargo_ship.hull.size = 2

        cargo_ship.add_module(ModuleFactory.create(ModuleDefs.BaseGenerator.name, cargo_ship.get_counter(), active=True))
        cargo_ship.add_module(ModuleFactory.create(ModuleDefs.BaseEngine.name, cargo_ship.get_counter(), active=True))

        cargo_ship.crew = 10
        
        cargo_ship.storage.push(ItemDefs.MEAL, 1000)
        cargo_ship.storage.push(ItemDefs.MDO, 10000)

        await container.ship_service.save(cargo_ship)

        await container.market_service.create(CreateMarketOrderSchema(
            owner_id=npc_user.id,
            platform_id=platform.id,
            order_type=MarketOrderType.Sell,
            price=10,
            quantity=1000,
            item_name=ItemDefs.MEAL.name
        ))
        await container.market_service.create(CreateMarketOrderSchema(
            owner_id=npc_user.id,
            platform_id=platform.id,
            order_type=MarketOrderType.Sell,
            price=20,
            quantity=1000,
            item_name=ItemDefs.MDO.name
        ))
        await container.market_service.create(CreateMarketOrderSchema(
            owner_id=npc_user.id,
            platform_id=platform.id,
            order_type=MarketOrderType.Buy,
            price=5,
            quantity=10000,
            item_name=ItemDefs.Fish.name
        ))

if __name__ == "__main__":
    async def _run():
        try:
            async with get_context_container() as container:
                await seed_world(container)
        finally:
            await dispose()
    asyncio.run(_run())
