from __future__ import annotations
from typing import TYPE_CHECKING, TypedDict, Optional

from .base import BaseCommand
from .factory import register_command
from ..world import World
from app.defs.enums import ObjectType, MarketOrderType
from .docking import DockingCommand
from app.defs.items import MAP as ItemMap

if TYPE_CHECKING:
    from ..ship import ShipEntity
    from ..platform import PlatformEntity


class TradeOperation(TypedDict):
    item_name: str
    quantity: int
    price: int
    op_type: int

@register_command()
class TradeCommand(BaseCommand):
    name = 'trade'

    def __init__(self, platform_id: int = 0, operations: Optional[list[TradeOperation]] = None):
        super().__init__()
        self.platform_id = platform_id
        self.operations = operations if operations is not None else []
        self.stage = 0
        self.is_process = False
        if not self.operations:
            self.finished = True

    def to_dict(self) -> dict[str, any]:
        data = super().to_dict()
        data['platform_id'] = self.platform_id
        data['operations'] = self.operations
        data['stage'] = self.stage
        return data

    def from_dict(self, data: dict[str, any]):
        super().from_dict(data)
        self.platform_id = data.get('platform_id', 0)
        self.operations = data.get('operations', [])
        self.stage = data.get('stage', 0)

    def update(self, ship: ShipEntity, dt: float, world: World):
        if self.finished or self.is_process:
            return

        if (self.stage == 0 
            and ship.attached_to_id == self.platform_id 
            and ship.attached_to_type == ObjectType.Platform):
            self.stage = 1

        match self.stage:
            case 0:
                docking = DockingCommand(self.platform_id)
                docking.is_dependend = True
                ship.command_queue.add(docking, True)
                return
            case 1:
                async def trade_ops():
                    ship_owner = world.find_user(ship.owner_id)
                    market_service = world.get_market_service()

                    for op in self.operations:
                        item_type = ItemMap.get(op['item_name'], None)
                        if item_type is None:
                            continue

                        orders = await market_service.get_for_operation(
                            platform_id=self.platform_id, 
                            item_name=op['item_name'],
                            price=op['price'],
                            order_type=MarketOrderType.Buy if op['op_type'] == MarketOrderType.Sell else MarketOrderType.Sell
                        )
                        
                        left = op['quantity']
                        if op['op_type'] == MarketOrderType.Sell:
                            have = ship.get_amount(item_type)
                            left = min(left, have)

                        for order in orders:
                            if left <= 0:
                                break

                            diff = left if order.quantity > left else order.quantity
                            left -= diff
                            money = diff * order.price
                            order_owner = world.find_user(order.owner_id)

                            if op['op_type'] == MarketOrderType.Buy:
                                ship_owner.money -= money
                                ship.push(item_type, diff)
                            else:
                                ship_owner.money += money
                                ship.pull(item_type, diff)
                                
                            if not order_owner.is_npc:
                                order.quantity -= diff
                                pass
                                # todo: Передача товара на склад, зачисление денег для игрока
                                await market_service.save(order)
                            
                    self.finished = True
                world.add_async_action(trade_ops)
                self.is_process = True
                
