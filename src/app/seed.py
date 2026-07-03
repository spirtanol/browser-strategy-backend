import asyncio

from app.bootstrap.container import get_context_container
from app.services.user.action import UserService
from app.services.ship.action import ShipService
from app.services.platform.action import PlatformService
from app.services.site.action import SiteService
from app.services.market import MarketService, CreateMarketOrderSchema
from app.entities.ship import ShipEntity
from app.entities.platform import PlatformEntity
from app.entities.site import SiteEntity
from app.defs import modules as ModuleDefs, items as ItemDefs
from app.entities.ship_modules import factory as ModuleFactory
from app.schemas.user import CreateUserSchema, CreateNpcSchema
from app.core.disposer import dispose
from app.defs.enums import MarketOrderType
from app.defs.deposites import BaseRestrictions, SiteContent


async def seed_world(
    user_service: UserService, 
    ship_service: ShipService, 
    platform_service: PlatformService,
    market_servcie: MarketService,
    site_service: SiteService
):
    # Создаем npc
    create_npc_dto = CreateNpcSchema(name='NPC')

    npc_user = await user_service.create_npc(create_npc_dto)

    # Создаем платформу
    platform = PlatformEntity()
    platform.name = 'The Platform'
    platform.owner_id = npc_user.id
    platform.x = 2.0
    platform.y = 1.0
    await platform_service.save(platform)

    # Создаем рыбное место
    fish_site = SiteEntity(restriction=BaseRestrictions.get(SiteContent.Fish))
    fish_site.x = 2.0
    fish_site.y = -1.0
    await site_service.save(fish_site)

    # Создаем пользователя
    create_user_dto = CreateUserSchema(
        name='spirt',
        email='spirt@test.com',
        password='12qwaszx',
        is_npc=False
    )

    user = await user_service.create(create_user_dto)
    user.money = 1000
    await user_service.save(user)

    ship = ShipEntity()
    ship.owner_id = user.id
    ship.name = 'Blue Shrimp'

    # Создаем модули корабля
    ship.hull.hp = 1000
    ship.hull.weight = 3000
    ship.hull.floatage = 6000
    
    ship.add_module(ModuleFactory.create(ModuleDefs.BaseGenerator.name, ship.get_counter(), active=True))
    ship.add_module(ModuleFactory.create(ModuleDefs.BaseEngine.name, ship.get_counter(), active=True))
    ship.add_module(ModuleFactory.create(ModuleDefs.FishNet.name, ship.get_counter(), active=True))
    
    ship.crew = 10
    ship.storage.push(ItemDefs.MEAL, 100)
    ship.storage.push(ItemDefs.FUEL_BARREL, 10)

    await ship_service.save(ship)

    await market_servcie.create(CreateMarketOrderSchema(
        owner_id=npc_user.id,
        platform_id=platform.id,
        order_type=MarketOrderType.Sell,
        price=10,
        quantity=1000,
        item_name=ItemDefs.MEAL.name
    ))
    await market_servcie.create(CreateMarketOrderSchema(
        owner_id=npc_user.id,
        platform_id=platform.id,
        order_type=MarketOrderType.Sell,
        price=20,
        quantity=1000,
        item_name=ItemDefs.FUEL_BARREL.name
    ))
    await market_servcie.create(CreateMarketOrderSchema(
        owner_id=npc_user.id,
        platform_id=platform.id,
        order_type=MarketOrderType.Buy,
        price=5,
        quantity=1000,
        item_name=ItemDefs.EMPTY_BARREL.name
    ))
    await market_servcie.create(CreateMarketOrderSchema(
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
                async with container.transaction():
                    await seed_world(
                        container.user_service, 
                        container.ship_service, 
                        container.platform_service,
                        container.market_service,
                        container.site_service
                    )
        finally:
            await dispose()
    asyncio.run(_run())
