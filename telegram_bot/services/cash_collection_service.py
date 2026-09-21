from telegram_bot.storage.cash_collection_cache import CashCollectionCache
from telegram_bot.models.cash_collection_task import ScheduledCashCollectionTask, CashCollectionTask

import datetime
from uuid import uuid4



class CashCollectionService(CashCollectionCache):

    def __init__(self, sheduled_cash_collection_database):
        self.sheduled_database = sheduled_cash_collection_database
        
    async def create_sheduler(self, 
                              city_id: int,
                              city: str,
                              description: str,
                              creator_id: int,
                              creator_name: str,
                              performer_id: int,
                              performer_name: str,
                              every_n_days: int
                            ):
        
        id_ = uuid4().hex[:16]  # генерим уникальный id
        created_at = datetime.datetime.now()
        sheduled_task = ScheduledCashCollectionTask(
                    id=id_,
                    city_id=city_id,
                    city=city,
                    description=description,
                    creator_id=creator_id,
                    creator_name=creator_name,
                    performer_id=performer_id,
                    performer_name=performer_name,
                    created_at=created_at,
                    every_n_days=every_n_days,
                    next_run_at = datetime.datetime.now().replace(second=0, microsecond=0)
                )

        self.sheduled_tasks[id_ ] = sheduled_task # add to csh
        # запись в базу данных
        await self.sheduled_database.upsert(sheduled_task)
        return sheduled_task
