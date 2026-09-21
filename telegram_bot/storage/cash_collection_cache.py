from telegram_bot.models.cash_collection_task import ScheduledCashCollectionTask, CashCollectionTask


class CashCollectionCache:
    sheduled_tasks: dict[str, ScheduledCashCollectionTask] = {}
    tasks: dict[str, CashCollectionTask] = {}    