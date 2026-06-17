from .base import ResolverContext, ResolveResult
from app.entities.user import UserEntity
from ..handlers.trade import TradeCommandParams
from .dock_to_platform_resolver import dock_to_platform_resolver
from app.defs.items import MAP as ItemMap


async def trade_resolver(context: ResolverContext, user: UserEntity, dto: TradeCommandParams) -> ResolveResult:
    res = await dock_to_platform_resolver(context, user, dto)

    if not res.success:
        return res

    errors = []
    if len(dto.operations) > 0:
        for op in dto.operations:
            if op['item_name'] not in ItemMap:
                errors.append(f'Предмета {op['item_name']} не существует')
    else:
        errors = ['Не заданы операции для торговли']

    return ResolveResult(
        success=len(errors) == 0,
        message='\n'.join(errors) if len(errors) > 0 else None
    )