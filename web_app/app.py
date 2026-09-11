from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from core.app_context import AppContext
from web_app.api.auth import router as router_api_login
from web_app.api.task_tittles import router as api_task_tittles_router
from web_app.api.users import router as api_users_router
from web_app.api.points import router as api_points_router



from web_app.routes.auth import router as auth_router
from web_app.routes.root import router as root_router
from web_app.routes.task_tittles import router as task_tittles_router
from web_app.routes.users import router as users_router
from web_app.routes.points import router as points_router






def create_app(context: AppContext):
    app = FastAPI()
    app.state.context = context

    app.add_middleware(
        SessionMiddleware,
        secret_key="fgdfgfgdf",
        session_cookie="session",
        max_age=60 * 60 * 24 * 7,
        same_site="lax",
        https_only=False,
    )

    app.include_router(root_router)
    app.include_router(auth_router)
    app.include_router(router_api_login)
    app.include_router(task_tittles_router)
    app.include_router(api_task_tittles_router)
    app.include_router(users_router)
    app.include_router(api_users_router)
    app.include_router(points_router)
    app.include_router(api_points_router)
    

    app.mount(
        "/static",
        StaticFiles(directory="web_app/static"),
        name="static",
    )

    return app
