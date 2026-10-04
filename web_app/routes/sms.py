from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from web_app.routes.templates import templates
from core.config import settings

router = APIRouter()


@router.get("/sms/settings")
async def sms_settings(request: Request):
    if request.session.get("authenticated") is not True:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="sms_settings.html",
        context={
            "active_section": "sms_settings",
            "webhook_url": f"{settings.PUBLIC_IP}:{settings.PORT}/webhook/sms",
            
        }
    )
    
@router.get("/sms/details")
async def sms_details(request: Request):
    if request.session.get("authenticated") is not True:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="sms_details.html",
        context={
            "active_section": "sms_details",          
        }
    )     