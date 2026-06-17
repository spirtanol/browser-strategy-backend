from typing import Optional

from app.repositories.market_order import (
    MarketOrderRepository, 
    MarketOrder, 
    MarketOrderType, 
    MarketDepth
)
from app.schemas.market import CreateMarketOrderSchema


class MarketService:
    def __init__(self, market_order_repo: MarketOrderRepository):
        self._market_order_repo = market_order_repo

    async def find(self, id: int) -> Optional[MarketOrder]:
        return await self._market_order_repo.find(id)

    async def get_for_operation(self, platform_id: int, item_name: str, order_type: MarketOrderType, price: int) -> list[MarketOrder]:
        return await self._market_order_repo.get_by_platform_item_type_price(
            platform_id,
            item_name,
            order_type,
            price,
            True
        )

    async def get_by_ids(self, ids: list[int]) -> list[MarketOrder]:
        return await self._market_order_repo.get_by_ids(ids)

    async def get_platform_orders(self, platform_id: int) -> MarketDepth:
        return await self._market_order_repo.get_by_platforms([platform_id])

    async def create(self, dto: CreateMarketOrderSchema) -> MarketOrder:
        order = MarketOrder(
            owner_id=dto.owner_id,
            platform_id=dto.platform_id,
            quantity=dto.quantity,
            price=dto.price,
            item_name=dto.item_name,
            order_type=dto.order_type
        )

        await self._market_order_repo.save(order)

        return order

    async def remove(self, order: MarketOrder):
        await self._market_order_repo.delete(order)

    async def save(self, order: MarketOrder):
        await self._market_order_repo.save(order)