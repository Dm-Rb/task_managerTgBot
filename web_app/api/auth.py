from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from pydantic import BaseModel


router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
)


class LoginRequest(BaseModel):
    login: str
    password: str


@router.post("/login")
async def login(data: LoginRequest, request: Request):
    if data.login != "admin" or data.password != "12345":
        raise HTTPException(
            status_code=401,
            detail="Invalid login or password",
        )
    # Запоминаем, что этот браузер авторизован
    request.session["authenticated"] = True
    return RedirectResponse(url="/panel/task_tittles",status_code=303)
