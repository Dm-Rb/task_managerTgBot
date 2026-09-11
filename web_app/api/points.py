from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from core.app_context import AppContext
from fastapi import status


router = APIRouter(
    prefix="/api",
    tags=["points"],
)



@router.get("/get_points")
async def get_points(request: Request):
    if not request.session["authenticated"] == True:
        return RedirectResponse(url="/login",status_code=303)
    context: AppContext = request.app.state.context
    result = context.template_service.get_all_points_for_api()
    return result


@router.post("/add_city")
async def add_city(request: Request):
    if not request.session["authenticated"] == True:
        return RedirectResponse(url="/login",status_code=303)
    r = await request.json()
    context: AppContext = request.app.state.context
    city = await context.template_service.new_city(r['city'])
    return city


@router.post("/add_adress")
async def add_adress(request: Request):
    if not request.session["authenticated"] == True:
        return RedirectResponse(url="/login",status_code=303)
    r = await request.json()
    context: AppContext = request.app.state.context
    adress = await context.template_service.new_adress(adress=r['adress'], 
                                                     city_id=r['city_id']
                                                     )
    return adress

@router.post("/add_point")
async def add_point(request: Request):
    if not request.session["authenticated"] == True:
        return RedirectResponse(url="/login",status_code=303)
    r = await request.json()
    context: AppContext = request.app.state.context
    point = await context.template_service.new_point(point=r['point'],
                                                     id_device=r['id_device'],
                                                     adress_id=r['adress_id'], 
                                                     city_id=r['city_id']
                                                     )
    return point

@router.post("/update_city")
async def update_city(request: Request):
    if not request.session["authenticated"] == True:
        return RedirectResponse(url="/login",status_code=303)
    r = await request.json()
    context: AppContext = request.app.state.context
    city = await context.template_service.update_city(r['id'], r['city'])
    return city

@router.post("/update_adress")
async def update_adress(request: Request):
    if not request.session["authenticated"] == True:
        return RedirectResponse(url="/login",status_code=303)
    r = await request.json()
    context: AppContext = request.app.state.context
    adress = await context.template_service.update_adress(id_=r['id'], adress=r['adress'], city_id=r['city_id'])
    return adress

@router.post("/update_point")
async def update_point(request: Request):
    if not request.session["authenticated"] == True:
        return RedirectResponse(url="/login",status_code=303)
    r = await request.json()
    context: AppContext = request.app.state.context
    point = await context.template_service.update_point(id_=r['id'], 
                                                        point=r['point'], 
                                                        id_device=r['id_device'],
                                                        city_id=r['city_id'], 
                                                        adress_id=r['adress_id']
                                                     )
    return point

@router.delete("/delete_city/{city_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_city(request: Request, city_id: int):
    context: AppContext = request.app.state.context
    await context.template_service.delete_city(city_id)
    # статус 204 (No Content), возвращать тело ответа не нужно
    return None

@router.delete("/delete_adress/{adress_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_adress(request: Request, adress_id: int):
    context: AppContext = request.app.state.context
    await context.template_service.delete_adress(adress_id)
    # статус 204 (No Content), возвращать тело ответа не нужно
    return None

@router.delete("/delete_point/{point_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_point(request: Request, point_id: int):
    context: AppContext = request.app.state.context
    await context.template_service.delete_point(point_id)
    # статус 204 (No Content), возвращать тело ответа не нужно
    return None