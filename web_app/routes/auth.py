from fastapi import APIRouter
from fastapi.responses import FileResponse


router = APIRouter(
    tags=["auth"],
)


@router.get("/login")
async def login_page():
    return FileResponse(
        "web_app/templates/login.html"
    )