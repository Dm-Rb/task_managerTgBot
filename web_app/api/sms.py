from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from core.app_context import AppContext
from pydantic import BaseModel, Field
from datetime import datetime
import json
import re
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import logging


logger = logging.getLogger(__name__)
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
    sim: str | None = None

    model_config = {"populate_by_name": True}

@field_validator("sentStamp", mode="before")
@classmethod
def stamp_to_str(cls, v):
    # шлюз может прислать число вместо строки
    return str(v)


# Запасной разбор на случай, когда в тексте SMS есть неэкранированные " или \
_FALLBACK_RE = re.compile(
    r'"from"\s*:\s*"(?P<from_>.*?)"\s*,\s*'
    r'"text"\s*:\s*"(?P<text>.*)"\s*,\s*'
    r'"sentStamp"\s*:\s*"?(?P<sentStamp>\d+)"?',
    re.DOTALL,
)


def clean_text(s: str) -> str:
    """Убирает NUL и заменяет одиночные суррогаты, чтобы запись в SQLite не падала."""
    s = s.replace("\x00", "")
    return s.encode("utf-8", errors="replace").decode("utf-8")


def parse_sms_body(raw: bytes) -> IncomingSms:
    body = raw.decode("utf-8", errors="replace")

    # Основной путь: strict=False разрешает сырые \n и \t внутри строк
    try:
        return IncomingSms.model_validate(json.loads(body, strict=False))
    except ValueError:
        pass

    # Запасной путь: регулярка по фиксированному порядку полей
    m = _FALLBACK_RE.search(body)
    if m:
        return IncomingSms.model_validate(m.groupdict())

    raise ValueError("unparsable body")


@router.post("/webhook/sms")
async def receive_sms(request: Request):
    """Принимает входящее СМС от шлюза и сохраняет его в БД."""
    context: AppContext = request.app.state.context
    raw = await request.body()

    try:
        payload = parse_sms_body(raw)
    except ValueError:
        logger.error("Bad SMS payload: %r", raw)
        raise HTTPException(status_code=422, detail="Invalid payload")

    await context.sms_database.create(
        from_=clean_text(payload.from_),
        text=clean_text(payload.text),
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
