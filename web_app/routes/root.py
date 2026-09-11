from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse


router = APIRouter()


@router.get("/")
async def index(request: Request):
    print(request.session.get("authenticated"))
    if request.session.get("authenticated") is not True:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    return RedirectResponse(
        url="/panel/task_tittles",
        status_code=303,
    )