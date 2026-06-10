from .handlers.move_to import MoveToCommandParams, move_to_command
from .handlers.cancel import CancelCommandParams, cancel_command
from .handlers.feed import FeedCommandParams, feed_command
from .handlers.move_to_object import move_to_object_command, MoveToObjectCommandParams
from .resolvers.ship import ship_command_resolver
from .resolvers.move_to_object_resolver import move_to_object_resolver


COMMAND_CONFIG = {
    'move_to': {
        'dto': MoveToCommandParams,
        'resolver': ship_command_resolver,
        'handler': move_to_command
    },
    'cancel': {
        'dto': CancelCommandParams,
        'resolver': ship_command_resolver,
        'handler': cancel_command
    },
    'feed' : {
        'dto': FeedCommandParams,
        'resolver': ship_command_resolver,
        'handler': feed_command
    },
    'move_to_object': {
        'dto': MoveToObjectCommandParams,
        'resolver': move_to_object_resolver,
        'handler': move_to_object_command
    }
}