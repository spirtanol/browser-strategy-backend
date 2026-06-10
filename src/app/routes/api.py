from fastapi import APIRouter, status

from app.bootstrap.container import get_context_container
from app.schemas.auth import LoginRequest, LoginResponse

def create_api_router(prefix: str, tags: list[str]) -> APIRouter:
    router = APIRouter(
        prefix=prefix, 
        tags=tags,
    )

    @router.post('/auth/login', response_model=LoginResponse)
    async def login(payload: LoginRequest):
        async with get_context_container() as container:
            async with container.transaction():
                access = await container.auth_service.login_by_creds(payload)
        return LoginResponse.model_validate(access)

    return router
