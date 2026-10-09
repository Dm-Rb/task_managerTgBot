from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request
from fastapi.responses import RedirectResponse
from web_app.routes.templates import templates
from core.app_context import AppContext
from core.config import settings
import hmac
from urllib.parse import unquote


router = APIRouter()


@router.get("/telephony/settings")
async def call_settings_page(request: Request):
    if request.session.get("authenticated") is not True:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="call_settings.html",
        context={
            "active_section": "telephony-settings",
            "webhook_url": f"{settings.PUBLIC_IP}:{settings.PORT}/webhook/call",
            "webhook_token": settings.WEBHOOK_KEY,
        }
    )

@router.get("/telephony/details")
async def call_details_page(request: Request):
    if request.session.get("authenticated") is not True:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="call_details.html",
        context={
            "active_section": "telephony-details"
        }
    )
    
@router.post("/webhook/call")
async def webhook_call(
    request: Request,
    background_tasks: BackgroundTasks,
    x_key: str | None = Header(default=None),        # читает заголовок x-key
    x_filename: str | None = Header(default=None),   # читает заголовок x-filename
    ):

    if not x_key or not hmac.compare_digest(
        x_key.encode("utf-8"), settings.WEBHOOK_KEY.encode("utf-8")
    ):
        raise HTTPException(status_code=403, detail="Forbidden")

    filename = unquote(x_filename) if x_filename else None

    audio = await request.body()
    if not audio:
        raise HTTPException(status_code=400, detail="Пустое тело запроса")
    context: AppContext = request.app.state.context


    # Распознавание в фоне, ответ отправителю сразу
    background_tasks.add_task(context.telephony_service.transcribe_call, audio, filename)
    return {"status": "ok"}
