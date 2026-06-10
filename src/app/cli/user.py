import asyncio

import typer

from . import helper
from app.bootstrap.container import get_context_container
from app.schemas.user import CreateUserSchema


cli = typer.Typer()

@cli.command('user:create')
def create_user(
    name: str = typer.Argument(..., help='Имя пользователя'),
    email: str = typer.Argument(help='email пользователя')
):
    password = typer.prompt('Пароль', default=None, hide_input=True)

    @helper.cleanup
    async def inner():
        async with get_context_container() as container:
            async with container.transaction():
                schema = CreateUserSchema(
                    name=name,
                    email=email,
                    password=password
                )

                user = await container.user_service.create(schema)

            print(f'Добавлен новый пользователь: {user.id} {user.email}')
    asyncio.run(inner())