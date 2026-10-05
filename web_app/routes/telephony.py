from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from web_app.routes.templates import templates
from core.config import settings

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
            "webhook_token": settings.WEBHOOK_TOKEN,
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