from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator

from app.models.market_order import MarketOrderType
from app.defs.items import MAP as ItemsMap


class CreateMarketOrderSchema(BaseModel):
    owner_id: int
    platform_id: int
    order_type: MarketOrderType
    price: int = Field(gt=0)
    quantity: int = Field(gt=0)
    item_name: str = Field(max_length=128, min_length=1)

    @field_validator('item_name')
    @classmethod
    def validate_item_name(cls, value: str) -> str:
        if value not in ItemsMap:
            raise ValueError(f"Товар '{value}' не зарегистрирован в игре")
        return value