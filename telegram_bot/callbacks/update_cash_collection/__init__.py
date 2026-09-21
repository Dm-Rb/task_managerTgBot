from aiogram import Router

from .remove_shedule_tasks import router as remove_shedule_tasks_router
from .submenu import router as submenu_router

router = Router()

router.include_router(remove_shedule_tasks_router)
router.include_router(submenu_router)


