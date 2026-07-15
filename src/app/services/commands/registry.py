from .handlers.move_to import MoveToCommandParams, move_to_command
from .handlers.cancel import CancelCommandParams, cancel_command
from .handlers.move_to_object import move_to_object_command, MoveToObjectCommandParams
from .handlers.dock_to_platform import dock_to_platform_command, DockToPlatformCommandParams
from .handlers.trade import TradeCommandParams, trade_command
from .handlers.fishing import FishingCommandParams, fishing_command
from .resolvers.fleet_resolver import fleet_command_resolver
from .resolvers.move_to_object_resolver import move_to_object_resolver
from .resolvers.dock_to_platform_resolver import dock_to_platform_resolver
from .resolvers.trade_resolver import trade_resolver
from .resolvers.fishing_resolver import fishing_resolver


COMMAND_CONFIG = {
    'move_to': {
        'dto': MoveToCommandParams,
        'resolver': fleet_command_resolver,
        'handler': move_to_command
    },
    'cancel': {
        'dto': CancelCommandParams,
        'resolver': fleet_command_resolver,
        'handler': cancel_command
    },
    'move_to_object': {
        'dto': MoveToObjectCommandParams,
        'resolver': move_to_object_resolver,
        'handler': move_to_object_command
    },
    'dock': {
        'dto': DockToPlatformCommandParams,
        'resolver': dock_to_platform_resolver,
        'handler': dock_to_platform_command
    },
    'trade': {
        'dto': TradeCommandParams,
        'resolver': trade_resolver,
        'handler': trade_command
    },
    'fishing': {
        'dto': FishingCommandParams,
        'resolver': fishing_resolver,
        'handler': fishing_command
    }
}