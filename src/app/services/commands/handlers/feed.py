from .base import ShipTargeted
from app.entities.world import World


class FeedCommandParams(ShipTargeted):
    amount: int

def feed_command(world: World, params: FeedCommandParams):
    ship = world.find_ship(params.ship_id)
    
    if ship is None:
        return
        
    if params.amount > 0:
        from app.defs.items import MEAL
        ship.storage.push(MEAL, params.amount)