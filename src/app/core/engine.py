import asyncio
import time
from typing import Callable, AsyncContextManager

from app.services.ship import ShipService


class Engine:
    def __init__(
        self, dt_multiplier: float, 
        tick_duration: int, 
        ship_service: ShipService,
        transaction_manager: Callable[[], AsyncContextManager[None]]
    ):
        self.ship_service = ship_service
        self.is_running = False
        self.dt_multiplier = dt_multiplier
        self.tick_duration = float(tick_duration)
        self.transaction_manager = transaction_manager
        self.running = False

    async def run(self):
        if self.is_running:
            return
            
        self.is_running = True
        self.running = True

        async with self.transaction_manager():
            if await self.ship_service.is_empty():
                print('Мир пуст')
                return

        last_time = time.perf_counter()

        try:
            while self.running:
                current_time = time.perf_counter()
                dt = (current_time - last_time) * self.dt_multiplier

                async with self.transaction_manager():
                    ships = await self.ship_service.get_all()
                    for ship in ships:
                        ship.update(dt)
                    
                    # Можно сбрасывать данные не каждый тик
                    await self.ship_service.flush(ships)

                last_time = current_time

                elapsed = time.perf_counter() - current_time
                sleep_time = max(0, self.tick_duration - elapsed)
                
                await asyncio.sleep(sleep_time)

        except (KeyboardInterrupt, asyncio.CancelledError):
            print("\nСимуляция остановлена пользователем.")
        finally:
            self.is_running = False
            print("Сохраняем прогресс...")
            async def final_save():
                async with self.transaction_manager():
                    ships = await self.ship_service.get_all()
                    await self.ship_service.save(ships)
                    
            await asyncio.shield(final_save())
            print("Прогресс сохранен. Выход.")

    def stop(self):
        self.running = False
    