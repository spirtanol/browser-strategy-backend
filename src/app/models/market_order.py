import enum

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Integer, Index, String

from .base import BaseModel
from app.defs.enums import MarketOrderType


class MarketOrder(BaseModel):
    __tablename__ = 'market_orders'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete='RESTRICT', onupdate='NO ACTION'), nullable=False, index=True)
    platform_id: Mapped[int] = mapped_column(ForeignKey("platforms.id", ondelete='RESTRICT', onupdate='NO ACTION'), nullable=False, index=True)
    order_type: Mapped[MarketOrderType] = mapped_column(Integer, nullable=False, index=True)
    price: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    item_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)

    __table_args__ = (
        Index('ix_market_orders_platform_type_price', 'platform_id', 'order_type', 'price'),
        Index('ix_market_orders_platform_item_type_price', 'platform_id', 'item_name', 'order_type', 'price'),
    )