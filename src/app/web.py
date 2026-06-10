from contextlib import asynccontextmanager
import asyncio
import sys

from fastapi import FastAPI, status, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware

from app.core.disposer import dispose
from app.core.exceptions import NotFoundEntityError, AuthError
from app.routes import api_router, ws_router
from app.utils.fapi import dump_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    dump_routes(app)
    yield
    await dispose()

app = FastAPI(
    docs_url='/docs',
    lifespan=lifespan,
    title="My game API",
    version="0.0.1",
    description="Короткое описание API"
)

@app.exception_handler(NotFoundEntityError)
async def not_found_handler(request: Request, exc: NotFoundEntityError):
    http_except = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return await http_exception_handler(request, http_except)

@app.exception_handler(AuthError)
async def auth_error_handler(request: Request, exc: AuthError):
    http_except = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    return await http_exception_handler(request, http_except)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
    allow_credentials=True
)

app.include_router(api_router)
app.include_router(ws_router)