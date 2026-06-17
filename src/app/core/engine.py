from __future__ import annotations
import asyncio
import time
from typing import TYPE_CHECKING, AsyncContextManager, Optional
import traceback

from app.services.ship.core import CoreShipService
from app.services.user.core import CoreUserService
from app.services.platform.core import CorePlatformService
from app.entities.world import World, Awaitable
from app.services.market import MarketService

if TYPE_CHECKING:
    from .ship import ShipEntity
    from .platform import PlatformEntity
    from .user import UserEntity

class Engine(World):
    def __init__(
        self, 
        dt_multiplier: float, 
        tick_duration: int, 
        ship_service: CoreShipService,
        user_service: CoreUserService,
        platform_service: CorePlatformService,
        transaction_manager: callable[[], AsyncContextManager[None]],
        save_interval: float,
        market_service: MarketService
    ):
        self.ship_service = ship_service
        self.user_service = user_service
        self.platform_service = platform_service
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
            await self.ship_service.save()
            await self.platform_service.save()

    async def run(self):
        if self.is_running:
            return
            
        self.is_running = True
        self.running = True

        async with self.transaction_manager():
            if await self.ship_service.is_empty():
                print('Мир пуст')
                return

        async with self.transaction_manager():
            await self.user_service.load()
            await self.ship_service.load()
            await self.platform_service.load()

        last_tick_time = time.perf_counter()
        last_save_time = last_tick_time

        try:
            while self.running:
                current_time = time.perf_counter()
                dt = (current_time - last_tick_time) * self.dt_multiplier

                ships = self.ship_service.get_all()
                for ship in ships:
                    ship.update(dt, self)
                
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
                    
                # Можно сбрасывать данные не каждый тик
                await self.ship_service.flush()
                await self.user_service.flush()
                await self.platform_service.flush()

                last_tick_time = current_time

                # Сохранение данных в базу
                if current_time - last_save_time >= self.save_interval:
                    await self._save()
                    last_save_time = current_time

                elapsed = time.perf_counter() - current_time
                sleep_time = max(0, self.tick_duration - elapsed)
                
                await asyncio.sleep(sleep_time)

        except (KeyboardInterrupt, asyncio.CancelledError):
            traceback.print_exc()
            print("\nСимуляция остановлена пользователем.")
        except Exception as e:
            traceback.print_exc()
            print('\nВсе пропало', str(e))
        finally:
            self.is_running = False
            print("Сохраняем прогресс...")
            async def final_save():
                await self._save()
                    
            await asyncio.shield(final_save())
            print("Прогресс сохранен. Выход.")

    def stop(self):
        self.running = False

    def find_ship(self, id: int) -> Optional[ShipEntity]:
        return self.ship_service.find(id)

    def find_platform(self, id: int) -> Optional[PlatformEntity]:
        return self.platform_service.find(id)

    def find_user(self, id: int) -> Optional[UserEntity]:
        return self.user_service.find(id)

    def add_async_action(self, action: callable[[], Awaitable[any]]):
        self._async_actions.append(action)
    
    def get_market_service(self) -> MarketService:
        return self.market_service