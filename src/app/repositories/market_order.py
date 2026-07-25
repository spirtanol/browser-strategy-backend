from typing import Callable, Optional, TypedDict

import sqlalchemy as sa

from app.models.market_order import MarketOrder, MarketOrderSnapshot, MarketOrderType
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

    @staticmethod
    def _snapshot_field(order: MarketOrder, name: str, *, use_history: bool):
        if not use_history:
            return getattr(order, name)
        hist = sa.inspect(order).attrs[name].history
        if hist.deleted:
            return hist.deleted[0]
        return getattr(order, name)

    async def ensure_snapshot(self, order: MarketOrder, *, is_new: bool = False) -> None:
        """First-write-wins: снимок только если для order.id ещё нет строки."""
        session = self._session_factory()
        existing = await session.get(MarketOrderSnapshot, order.id)
        if existing is not None:
            return

        use_history = not is_new
        session.add(MarketOrderSnapshot(
            id=order.id,
            owner_id=self._snapshot_field(order, 'owner_id', use_history=use_history),
            platform_id=self._snapshot_field(order, 'platform_id', use_history=use_history),
            order_type=self._snapshot_field(order, 'order_type', use_history=use_history),
            price=self._snapshot_field(order, 'price', use_history=use_history),
            quantity=self._snapshot_field(order, 'quantity', use_history=use_history),
            item_name=self._snapshot_field(order, 'item_name', use_history=use_history),
            is_new=is_new,
        ))
        await session.flush()

    async def apply_snapshots(self) -> None:
        """is_new → delete order; иначе upsert snapshot → market_orders."""
        session = self._session_factory()
        snapshots = list((await session.scalars(sa.Select(MarketOrderSnapshot))).all())
        if not snapshots:
            return

        for snap in snapshots:
            if snap.is_new:
                await session.execute(
                    sa.delete(MarketOrder).where(MarketOrder.id == snap.id)
                )
                continue

            order = await session.get(MarketOrder, snap.id)
            if order is None:
                session.add(MarketOrder(
                    id=snap.id,
                    owner_id=snap.owner_id,
                    platform_id=snap.platform_id,
                    order_type=snap.order_type,
                    price=snap.price,
                    quantity=snap.quantity,
                    item_name=snap.item_name,
                ))
            else:
                order.owner_id = snap.owner_id
                order.platform_id = snap.platform_id
                order.order_type = snap.order_type
                order.price = snap.price
                order.quantity = snap.quantity
                order.item_name = snap.item_name

        await session.flush()

    async def clear_snapshots(self) -> None:
        session = self._session_factory()
        await session.execute(sa.delete(MarketOrderSnapshot))
        await session.flush()

    async def delete_snapshot(self, order_id: int) -> None:
        session = self._session_factory()
        snap = await session.get(MarketOrderSnapshot, order_id)
        if snap is not None:
            await session.delete(snap)
            await session.flush()
