from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from web_app.routes.templates import templates

router = APIRouter()


@router.get("/panel/points")
async def ponts(request: Request):
    if request.session.get("authenticated") is not True:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="points.html",
        context={
            "active_section": "task_tittles"
        }
    )