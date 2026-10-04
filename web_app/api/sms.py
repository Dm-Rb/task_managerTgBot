from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from core.app_context import AppContext
from pydantic import BaseModel, Field
from datetime import datetime


router = APIRouter()


def _check_auth(request: Request) -> JSONResponse | None:
    """Общая проверка авторизации для API-роутов. Возвращает ответ 401, если не авторизован."""
    if request.session.get("authenticated") is not True:
        return JSONResponse(status_code=401, content={"detail": "Не авторизован"})
    return None


def _sms_to_dict(sms) -> dict:
    return {
        "id": sms.id,
        "from_": sms.from_,
        "text": sms.text,
        "sentStamp": sms.sentStamp,
        "completed_at": sms.completed_at.isoformat() if sms.completed_at else None,
    }


class IncomingSms(BaseModel):
    from_: str = Field(alias="from")
    text: str
    sentStamp: str
    model_config = {"populate_by_name": True}


@router.post("/webhook/sms")
async def receive_sms(request: Request, payload: IncomingSms):
    """Принимает входящее СМС от шлюза и сохраняет его в БД."""

    context: AppContext = request.app.state.context

    await context.sms_database.create(
        from_=payload.from_,
        text=payload.text,
        sent_stamp=payload.sentStamp,
        completed_at=datetime.now(),
    )

    return {"status": "ok"}


@router.get("/api/sms")
async def get_sms_list(request: Request, page: int = 1, limit: int = 10):
    """Возвращает страницу сообщений, отсортированных от новых к старым."""

    auth_error = _check_auth(request)
    if auth_error:
        return auth_error

    if page < 1:
        raise HTTPException(status_code=422, detail="page должен быть >= 1")
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=422, detail="limit должен быть от 1 до 100")

    context: AppContext = request.app.state.context

    offset = (page - 1) * limit
    items = await context.sms_database.get_page(offset=offset, limit=limit)
    total = await context.sms_database.count()

    return {
        "items": [_sms_to_dict(sms) for sms in items],
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.delete("/api/sms/{sms_id}")
async def delete_sms(request: Request, sms_id: int):
    """Удаляет сообщение по id."""

    auth_error = _check_auth(request)
    if auth_error:
        return auth_error

    context: AppContext = request.app.state.context

    await context.sms_database.delete_by_id(sms_id)

    return {"status": "ok"}
