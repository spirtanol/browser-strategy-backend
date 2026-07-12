import asyncio
import signal
from typing import Callable, AsyncContextManager
import logging

from app.bootstrap.container import get_context_container, CommandHandlerService
from app.core.engine import Engine
from app.core.disposer import dispose
from app.schemas.commands import GameCommand
from app.utils.async_helpers import fire_and_forget
from app.core.logging_config import init_logging


init_logging()
logger = logging.getLogger("app.core")

async def life_state_loop(check_func: Callable, interval: int):
    try:
        while True:
            await asyncio.sleep(interval)
            await check_func()
    except asyncio.CancelledError:
        pass

async def _run():
    async with get_context_container() as container:
        config = container.config

        engine = Engine(
            dt_multiplier=config.dt_multiplier, 
            tick_duration=config.tick_duration, 
            fleet_service=container.core_fleet_service,
            user_service=container.core_user_service,
            platform_service=container.core_platform_service,
            site_service=container.core_site_service,
            transaction_manager=container.transaction,
            save_interval=config.save_interval,
            market_service=container.market_service
        )

        def alive_handler(message):
            ename, id = message['data'].split(':')
            id = int(id)
            match ename:
                case 'ship':
                    container.life_state_registry.add_ship(id)
                case 'user':
                    container.life_state_registry.add_user(id)

        def command_handler(message):
            async def _handler():
                try:
                    command = GameCommand.model_validate_json(message['data'])
                    async with container.transaction():
                        await container.command_handler_service.handle(command, engine)
                except Exception as e:
                    logger.exception(f'Ошибка при обработке команды {e}')
            fire_and_forget(_handler())

        redis_client = container.get_redis()
        subscriber = redis_client.pubsub()
        await subscriber.subscribe(
            commands=command_handler,
            alive=alive_handler
        )

        async def message_loop():
            try:
                while True:
                    await subscriber.get_message(ignore_subscribe_messages=True, timeout=1.0)
            except asyncio.CancelledError:
                pass

        loop = asyncio.get_running_loop()

        game_loop = asyncio.create_task(engine.run())
        msg_task = asyncio.create_task(message_loop())
        life_task = asyncio.create_task(life_state_loop(container.life_state_registry.check_active, config.alive_objects_duration))

        def handle_stop_signal():
            logger.info("Получен сигнал SIGTERM от Docker, останавливаемся...")
            engine.stop()

        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, handle_stop_signal)

        try:
            await game_loop
        except asyncio.CancelledError:
            pass
        finally:
            life_task.cancel()
            msg_task.cancel()

            await asyncio.gather(msg_task, life_task, return_exceptions=True)
            await subscriber.unsubscribe()
            await subscriber.aclose()
            await dispose()

if __name__ == "__main__":
    asyncio.run(_run())