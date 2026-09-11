from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from core.app_context import AppContext
from fastapi import status


router = APIRouter(
    prefix="/api",
    tags=["users"],
)



@router.get("/get_users")
async def get_users(request: Request):
    if not request.session["authenticated"] == True:
        return RedirectResponse(url="/login",status_code=303)
    context: AppContext = request.app.state.context
    users: list =  context.user_service.get_all_users(dump=True)
    return users


@router.delete("/delete_user/{user_tg_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(request: Request, user_tg_id: int):
    context: AppContext = request.app.state.context
    await context.user_service.remove_user(user_tg_id)    
    # статус 204 (No Content), возвращать тело ответа не нужно
    return None