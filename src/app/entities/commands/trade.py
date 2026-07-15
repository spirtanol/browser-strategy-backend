from __future__ import annotations
from typing import TYPE_CHECKING, TypedDict, Optional, Any

from .base import BaseCommand
from .factory import register_command
from app.defs.enums import ObjectType, MarketOrderType
from .docking import DockingCommand
from app.defs.items import MAP as ItemMap

if TYPE_CHECKING:
    from ..platform import PlatformEntity


class TradeOperation(TypedDict):
    ship_id: int
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

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data['platform_id'] = self.platform_id
        data['operations'] = self.operations
        data['stage'] = self.stage
        return data

    def from_dict(self, data: dict[str, Any]):
        super().from_dict(data)
        self.platform_id = data.get('platform_id', 0)
        self.operations = data.get('operations', [])
        self.stage = data.get('stage', 0)

    def update(self, dt: float):
        if self.finished or self.is_process:
            return

        fleet = self.fleet

        if (self.stage == 0 
            and fleet.attached_to_id == self.platform_id 
            and fleet.attached_to_type == ObjectType.Platform):
            self.stage = 1

        match self.stage:
            case 0:
                docking = DockingCommand(self.platform_id)
                docking.is_dependent = True
                self.queue.add(docking, True)
                return
            case 1:
                async def trade_ops():
                    owner = self.world.find_user(fleet.owner_id)
                    market_service = self.world.get_market_service()

                    for op in self.operations:
                        item_type = ItemMap.get(op['item_name'], None)
                        if item_type is None:
                            continue
                        ship = self.fleet.ships.get(op['ship_id'], None)
                        if ship is None:
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
                            if left == -1:
                                left = have
                            else:
                                left = min(left, have)
                        else: # Корректируем покупку под имеющийся объем и плавучесть
                            purchase_volume = item_type.volume * left
                            free_space = ship.max_volume - ship.volume
                            if free_space < purchase_volume:
                                left = int(free_space / item_type.volume)
                            
                            purchase_width = item_type.weight * left
                            free_space = ship.floatage - ship.weight
                            if free_space < purchase_width:
                                left = int(free_space / item_type.weight)

                        for order in orders:
                            if left <= 0:
                                break

                            diff = left if order.quantity > left else order.quantity
                            left -= diff
                            money = diff * order.price
                            order_owner = self.world.find_user(order.owner_id)

                            if op['op_type'] == MarketOrderType.Buy:
                                owner.money -= money
                                ship.push(item_type, diff)
                            else:
                                owner.money += money
                                ship.pull(item_type, diff)
                                
                            if not order_owner.is_npc:
                                order.quantity -= diff
                                # todo: Передача товара на склад, зачисление денег для игрока
                                await market_service.save(order)
                            
                    self.finished = True
                self.world.add_async_action(trade_ops)
                self.is_process = True
