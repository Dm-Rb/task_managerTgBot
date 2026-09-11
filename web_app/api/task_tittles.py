from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from core.app_context import AppContext
from fastapi import status


router = APIRouter(
    prefix="/api",
    tags=["task_tittles"],
)



@router.get("/task_tittles")
async def get_task_tittles(request: Request):
    if not request.session["authenticated"] == True:
        return RedirectResponse(url="/login",status_code=303)
    context: AppContext = request.app.state.context
    task_tittles: list = await context.template_service.get_all_task_tittles(dump=True)
    return task_tittles


@router.post("/create_tittle")
async def create_tittle(request: Request):
    if not request.session["authenticated"] == True:
        return RedirectResponse(url="/login",status_code=303)
    request_json = await request.json()
    context: AppContext = request.app.state.context
    task_tittle: int or None = await context.template_service.create_new_task_tittle(request_json['tittle'], request_json['is_sheduler'])
    if task_tittle:
        return {"status": "success", "id": task_tittle.id}
    else:
        return {"status": "error"}

 
@router.post("/update_task_tittle")
async def update_task_tittle(request: Request):
    if not request.session["authenticated"] == True:
        return RedirectResponse(url="/login",status_code=303)
    context: AppContext = request.app.state.context
    request_json = await request.json()

    task_tittle = await context.template_service.update_task_tittle(
        request_json['id'], 
        request_json['tittle'],
        request_json['is_sheduler']
        )
    print(task_tittle)
    return "ok"

@router.delete("/delete_tittle/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tittle(request: Request, item_id: int):
    context: AppContext = request.app.state.context
    await context.template_service.remove_task_tittle_by_id(item_id)
    # статус 204 (No Content), возвращать тело ответа не нужно
    return None