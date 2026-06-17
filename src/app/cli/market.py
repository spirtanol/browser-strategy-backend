import asyncio
import traceback
from typing import Annotated

import typer, click

from . import helper
from app.bootstrap.container import get_context_container
from app.schemas.market import CreateMarketOrderSchema, MarketOrderType


cli = typer.Typer()


@cli.command('market:create_npc_order')
def create_order(
    owner_id: Annotated[int, typer.Argument(help="ID NPC-пользователя (владельца ордера)")],
    platform_id: Annotated[int, typer.Argument(help="ID платформы")],
    order_type: Annotated[MarketOrderType, typer.Argument(help="Тип ордера: 1 - Buy, 2 - Sell")],
    item_name: Annotated[str, typer.Argument(help="Название товара из системного MAP")],
    price: Annotated[int, typer.Argument(help="Цена за единицу товара (> 0)")],
    quantity: Annotated[int, typer.Argument(help="Количество товара (> 0)")],
):
    try:
        dto = CreateMarketOrderSchema(
            owner_id=owner_id,
            platform_id=platform_id,
            order_type=order_type,
            item_name=item_name,
            price=price,
            quantity=quantity
        )
    except ValidationError as e:
        click.secho("\n[Ошибка валидации DTO]:", fg="red", bold=True)
        for error in e.errors():
            click.echo(f"  { ' -> '.join(str(l) for l in error['loc']) }: {error['msg']}")
        return

    @helper.cleanup
    async def inner():
        async with get_context_container() as container:
            async with container.transaction():
                user = await container.user_service.find(dto.owner_id)

                if not user.is_npc:
                    print('Нельзя создать ордер для не npc пользователя')
                    return

                order = await container.market_service.create(dto)
            print(f'Новый ордер {order.id} {order.item_name} {order.price} {order.quantity}')
    asyncio.run(inner())

@cli.command('market:remove_npc_order')
def remove_order(order_id: Annotated[int, typer.Argument(help='ID ордера')]):
    @helper.cleanup
    async def inner():
        async with get_context_container() as container:
            async with container.transaction():
                order = await container.market_service.find(order_id)
                
                if order is None:
                    print(f'Ордер {order_id} не существует')
                    return

                owner = await container.user_service.find(order.owner_id)

                if not owner.is_npc:
                    print(f'Владелец ордера {order_id} не npc')
                    return

                await container.market_service.remove(order)
        print(f'Ордер {order_id} удален')
    asyncio.run(inner())