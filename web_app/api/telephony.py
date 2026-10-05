from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from core.app_context import AppContext

router = APIRouter()


def _check_auth(request: Request) -> JSONResponse | None:
    """Общая проверка авторизации для API-роутов. Возвращает ответ 401, если не авторизован."""
    if request.session.get("authenticated") is not True:
        return JSONResponse(status_code=401, content={"detail": "Не авторизован"})
    return None


def _call_to_dict(call) -> dict:
    return {
        "id": call.id,
        "from_": call.from_,
        "to_": call.to_,
        "short_text": call.short_text,
        "text": call.text,
        "completed_at": call.completed_at.isoformat() if call.completed_at else None,
    }


@router.get("/api/calls")
async def get_call_list(request: Request, page: int = 1, limit: int = 10):
    """Возвращает страницу записей о звонках, отсортированных от новых к старым."""

    auth_error = _check_auth(request)
    if auth_error:
        return auth_error

    if page < 1:
        raise HTTPException(status_code=422, detail="page должен быть >= 1")
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=422, detail="limit должен быть от 1 до 100")

    context: AppContext = request.app.state.context

    offset = (page - 1) * limit

    items = await context.telephony_database.get_page(offset=offset, limit=limit)
    total = await context.telephony_database.count()

    return {
        "items": [_call_to_dict(call) for call in items],
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.delete("/api/calls/{call_id}")
async def delete_call(request: Request, call_id: int):
    """Удаляет запись о звонке по id."""

    auth_error = _check_auth(request)
    if auth_error:
        return auth_error

    context: AppContext = request.app.state.context

    await context.telephony_database.delete_by_id(call_id)

    return {"status": "ok"}