import asyncio
import signal
from typing import Callable, AsyncContextManager

from app.bootstrap.container import get_context_container, CommandHandlerService, Mode
from app.core.engine import Engine
from app.core.disposer import dispose
from app.schemas.commands import GameCommand


async def command_subscribe(
    subscriber, 
    command_service: CommandHandlerService, 
    is_running: Callable[[], bool], 
    transaction_manager: Callable[[], AsyncContextManager[None]]
):
    while is_running():
        try:
            msg = await subscriber.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if msg:
                command = GameCommand.model_validate_json(msg['data'])
                async with transaction_manager():
                    await command_service.handle(command)
        except Exception as e:
            print(f'Ошибка при обработке команды {e}')

async def _run():
    async with get_context_container(Mode.CORE) as container:
        config = container.config

        redis_client = container.get_redis()
        subscriber = redis_client.pubsub()
        await subscriber.subscribe('commands')

        engine = Engine(
            config.dt_multiplier, 
            config.tick_duration, 
            container.ship_service,
            container.begin
        )

        loop = asyncio.get_running_loop()

        game_loop = asyncio.create_task(engine.run())
        asyncio.create_task(command_subscribe(subscriber, container.command_handler_service, lambda: engine.is_running, container.begin))
        

        def handle_stop_signal():
            print("Получен сигнал SIGTERM от Docker, останавливаемся...")
            engine.stop()

        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, handle_stop_signal)

        try:
            await game_loop
        except asyncio.CancelledError:
            pass
        finally:
            await subscriber.unsubscribe('command')
            await subscriber.aclose()
            await dispose()

if __name__ == "__main__":
    asyncio.run(_run())