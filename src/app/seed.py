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
        ship = ShipEntity()
        ship.name = 'Blue Shrimp'
        fleet.add_ship(ship)

        # Создаем модули корабля
        ship.hull.hull_config = BASE_HULL
        ship.hull.size = 1
        
        ship.add_module(ModuleFactory.create(ModuleDefs.BaseGenerator.name, ship.get_counter(), active=True))
        ship.add_module(ModuleFactory.create(ModuleDefs.BaseEngine.name, ship.get_counter(), active=True))
        ship.add_module(ModuleFactory.create(ModuleDefs.FishNet.name, ship.get_counter(), active=True))
        
        ship.crew = 10
        ship.storage.push(ItemDefs.MEAL, 100)
        ship.storage.push(ItemDefs.FUEL_BARREL, 10)

        await container.ship_service.save(ship)

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
            item_name=ItemDefs.FUEL_BARREL.name
        ))
        await container.market_service.create(CreateMarketOrderSchema(
            owner_id=npc_user.id,
            platform_id=platform.id,
            order_type=MarketOrderType.Buy,
            price=5,
            quantity=1000,
            item_name=ItemDefs.EMPTY_BARREL.name
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
