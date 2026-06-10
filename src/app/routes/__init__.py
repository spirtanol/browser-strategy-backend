from .api import create_api_router
from .ws import create_ws_router


api_router = create_api_router('/api', tags=['ship'])
ws_router = create_ws_router('/ws', tags=['ship'])