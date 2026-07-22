from typing import Callable, Optional, TypedDict

import sqlalchemy as sa

from app.models.market_order import MarketOrder, MarketOrderType
from app.core.db import AsyncSession


class MarketDepth(TypedDict):
    buy_orders: list[MarketOrder]
    sell_orders: list[MarketOrder]

class MarketOrderRepository:
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        self._session_factory = session_factory

    async def find(self, id: int) -> Optional[MarketOrder]:
        session = self._session_factory()
        return await session.get(MarketOrder, id)

    async def get_by_ids(self, ids: list[int]) -> list[MarketOrder]:
        session = self._session_factory()
        results = await session.scalars(sa.Select(MarketOrder).where(MarketOrder.id.in_(ids)))
        return list(results.all())
    
    async def get_by_platform_item_type_price(
        self, 
        platform_id: int, 
        item_name: str, 
        order_type: MarketOrderType, price: int, 
        for_update = False
    ) -> list[MarketOrder]:
        session = self._session_factory()
        
        stmt = (sa.Select(MarketOrder)
            .where(
                MarketOrder.platform_id == platform_id, 
                MarketOrder.item_name == item_name, 
                MarketOrder.order_type == order_type,
                MarketOrder.price >= price if order_type == MarketOrderType.Buy else MarketOrder.price <= price
            )
            .order_by(
                MarketOrder.price.desc() if order_type == MarketOrderType.Buy else MarketOrder.price.asc()
            )
        )
        if for_update:
            stmt = stmt.with_for_update()

        results = await session.scalars(stmt)
        return list(results.all())

    async def get_by_platforms(self, platform_ids: list[int]) -> MarketDepth:
        session = self._session_factory()

        stmt_buy = (sa.Select(MarketOrder)
            .where(MarketOrder.platform_id.in_(platform_ids), MarketOrder.order_type == MarketOrderType.Buy)
            .order_by(MarketOrder.price.desc()))
        stmt_sell = (sa.Select(MarketOrder)
            .where(MarketOrder.platform_id.in_(platform_ids), MarketOrder.order_type == MarketOrderType.Sell)
            .order_by(MarketOrder.price.asc()))

        buy_results = await session.scalars(stmt_buy)
        buy_orders = buy_results.all()
        sell_results = await session.scalars(stmt_sell)
        sell_orders = sell_results.all()

        return {
            "buy_orders": list(buy_orders),
            "sell_orders": list(sell_orders)
        }

    async def save(self, order: MarketOrder):
        session = self._session_factory()

        session.add(order)
        await session.flush()

    async def delete(self, order: MarketOrder):
        session = self._session_factory()
        await session.delete(order)