import asyncio

import typer

from . import helper
from app.bootstrap.container import get_context_container
from app.schemas.player import CreatePlayerSchema
from app.schemas.account import CreateAccountSchema


cli = typer.Typer()

@cli.command('player:create')
def create_player(
    name: str = typer.Argument(..., help='Имя игрока'),
    email: str = typer.Argument(help='email аккаунта')
):
    password = typer.prompt('Пароль', default=None, hide_input=True)

    @helper.cleanup
    async def inner():
        async with get_context_container() as container:
            async with container.transaction():
                account = await container.account_service.create(CreateAccountSchema(
                    email=email,
                    password=password,
                ))
                player = await container.player_service.create(CreatePlayerSchema(
                    name=name,
                    account_id=account.id,
                ))

            print(f'Добавлен новый игрок: {player.id} {player.name}')
    asyncio.run(inner())
