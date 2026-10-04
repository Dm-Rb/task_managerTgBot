from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from web_app.routes.templates import templates

router = APIRouter()


@router.post("/webhook/sms")
async def sms_webhook(request: Request):
    # 2. Разбор тела в зависимости от Content-Type
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        data = await request.json()
    elif "form" in content_type:
        data = dict(await request.form())
    else:
        raw = await request.body()
        
        data = {}
    print(data)