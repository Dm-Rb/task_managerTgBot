from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from core.config import settings


router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
)


class LoginRequest(BaseModel):
    login: str
    password: str


@router.post("/login")
async def login(data: LoginRequest, request: Request):
    if data.login != settings.LOGIN_WEB or data.password != settings.ADMIN_PSW:
        raise HTTPException(
            status_code=401,
            detail="Invalid login or password",
        )
    # Запоминаем, что этот браузер авторизован
    request.session["authenticated"] = True
    return RedirectResponse(url="/panel/task_tittles",status_code=303)

@router.post("/logout")
async def logout(request: Request):
    # Полностью очищаем сессию (удаляем authenticated и всё остальное)
    request.session.clear()
    request.session["authenticated"] = False
    return {"status": "ok"}