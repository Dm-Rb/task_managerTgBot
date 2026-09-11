from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from web_app.routes.templates import templates


router = APIRouter()


@router.get("/panel/users")
async def task_tittles(request: Request):
    if request.session.get("authenticated") is not True:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="members.html",
        context={
            "active_section": "users"
        }
    )