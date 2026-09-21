from aiogram import Router

from .remove_shedule_tasks import router as remove_shedule_tasks_router

# Собираем роутер подпакета
router = Router()

router.include_router(remove_shedule_tasks_router)
