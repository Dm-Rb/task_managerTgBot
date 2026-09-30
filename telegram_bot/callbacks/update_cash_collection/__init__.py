from aiogram import Router

from .remove_shedule_tasks import router as remove_shedule_tasks_router
from .remove_tasks import router as remove_tasks_router
from .complite_task import router as complite_task_router
from .report import router as report_router


from .submenu import router as submenu_router

router = Router()

router.include_router(remove_shedule_tasks_router)
router.include_router(remove_tasks_router)
router.include_router(complite_task_router)
router.include_router(report_router)


router.include_router(submenu_router)


