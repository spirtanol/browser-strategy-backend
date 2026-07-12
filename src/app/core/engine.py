from __future__ import annotations
import asyncio
import time
from typing import TYPE_CHECKING, AsyncContextManager, Optional
import logging

from app.services.fleet.core import CoreFleetService
from app.services.user.core import CoreUserService
from app.services.platform.core import CorePlatformService
from app.services.site.core import CoreSiteService
from app.entities.world import World, Awaitable
from app.services.market import MarketService

if TYPE_CHECKING:
    from app.entities.fleet import FleetEntity
    from app.entities.platform import PlatformEntity
    from app.entities.user import UserEntity


logger = logging.getLogger("app.core.engine")

class Engine(World):
    def __init__(
        self, 
        dt_multiplier: float, 
        tick_duration: int, 
        fleet_service: CoreFleetService,
        user_service: CoreUserService,
        platform_service: CorePlatformService,
        site_service: CoreSiteService,
        transaction_manager: callable[[], AsyncContextManager[None]],
        save_interval: float,
        market_service: MarketService
    ):
        self.fleet_service = fleet_service
        self.user_service = user_service
        self.platform_service = platform_service
        self.site_service = site_service
        self.is_running = False
        self.dt_multiplier = dt_multiplier
        self.tick_duration = float(tick_duration)
        self.transaction_manager = transaction_manager
        self.running = False
        self.save_interval = save_interval
        self._async_actions = []
        self.market_service = market_service

    async def _save(self):
        async with self.transaction_manager():
            await self.user_service.save()
            await self.fleet_service.save()
            await self.platform_service.save()
            await self.site_service.save()

    async def run(self):
        if self.is_running:
            return
            
        self.is_running = True
        self.running = True

        async with self.transaction_manager():
            if await self.fleet_service.is_empty():
                logger.debug('Мир пуст')
                return

        async with self.transaction_manager():
            await self.user_service.load()
            await self.fleet_service.load()
            await self.platform_service.load()
            await self.site_service.load()

        last_tick_time = time.perf_counter()
        last_save_time = last_tick_time

        try:
            while self.running:
                current_time = time.perf_counter()
                dt = (current_time - last_tick_time) * self.dt_multiplier

                fleets = self.fleet_service.get_all()
                for fleet in fleets:
                    fleet.update(dt, self)
                
                if len(self._async_actions) > 0:
                    async with self.transaction_manager():
                        await asyncio.gather(*(asyncio.create_task(act()) for act in self._async_actions))
                    self._async_actions.clear()
                
                users = self.user_service.get_all()
                for user in users:
                    user.update(dt)

                platforms = self.platform_service.get_all()
                for platform in platforms:
                    platform.update(dt)

                sites = self.site_service.get_all()
                for site in sites:
                    site.update(dt)
                    
                # Можно сбрасывать данные не каждый тик
                await self.fleet_service.flush()
                await self.user_service.flush()
                await self.platform_service.flush()
                await self.site_service.flush()

                last_tick_time = current_time

                # Сохранение данных в базу
                if current_time - last_save_time >= self.save_interval:
                    await self._save()
                    last_save_time = current_time

                elapsed = time.perf_counter() - current_time
                sleep_time = max(0, self.tick_duration - elapsed)
                
                await asyncio.sleep(sleep_time)

        except (KeyboardInterrupt, asyncio.CancelledError):
            logger.info('Остановка симуляции')
        except Exception as e:
            logger.exception('Краш игрового цикла')
        finally:
            self.is_running = False
            logger.info("Сохраняем прогресс...")
            async def final_save():
                await self._save()
                    
            await asyncio.shield(final_save())
            logger.info("Прогресс сохранен. Выход.")

    def stop(self):
        self.running = False

    def find_fleet(self, id: int) -> Optional[FleetEntity]:
        return self.fleet_service.find(id)

    def find_platform(self, id: int) -> Optional[PlatformEntity]:
        return self.platform_service.find(id)

    def find_user(self, id: int) -> Optional[UserEntity]:
        return self.user_service.find(id)

    def find_site(self, id: int) -> Optional[SiteEntity]:
        return self.site_service.find(id)

    def add_async_action(self, action: callable[[], Awaitable[any]]):
        self._async_actions.append(action)
    
    def get_market_service(self) -> MarketService:
        return self.market_service