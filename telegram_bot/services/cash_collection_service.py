from telegram_bot.storage.cash_collection_cache import CashCollectionCache
from telegram_bot.models.cash_collection_task import ScheduledCashCollectionTask, CashCollectionTask

import datetime
from uuid import uuid4



class CashCollectionService(CashCollectionCache):

    def __init__(self, sheduled_cash_collection_database):
        self.sheduled_database = sheduled_cash_collection_database
        
    async def warmup(self):
        db_tasks = await self.sheduled_database.get_all()

        self.sheduled_tasks = {
            db_task.id: ScheduledCashCollectionTask(
                id=db_task.id,
                city_id=db_task.city_id,
                city=db_task.city,
                description=db_task.description,
                creator_id=db_task.creator_id,
                creator_name=db_task.creator_name,
                performer_id=db_task.performer_id,
                performer_name=db_task.performer_name,
                created_at=db_task.created_at,
                every_n_days=db_task.every_n_days,
                next_run_at=db_task.next_run_at,
            )
            for db_task in db_tasks
        }
        return
    
        
    async def create_shedule_task(self, 
                              city_id: int,
                              city: str,
                              description: str,
                              creator_id: int,
                              creator_name: str,
                              performer_id: int,
                              performer_name: str,
                              every_n_days: int
                            )->ScheduledCashCollectionTask:
        
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
                    created_at=created_at.replace(second=0, microsecond=0),
                    every_n_days=every_n_days,
                    next_run_at = created_at.replace(second=0, microsecond=0)
                )

        self.sheduled_tasks[id_ ] = sheduled_task # add to csh
        # запись в базу данных
        await self.sheduled_database.upsert(sheduled_task)
        return sheduled_task
    
    async def get_shedule_tasks(self)->list[ScheduledCashCollectionTask]:        
        return list(self.sheduled_tasks.values())
    
    async def remove_shedule_task_by_id(self, shedule_task_id)->list[ScheduledCashCollectionTask]:        
        del self.sheduled_tasks[shedule_task_id]
        await self.sheduled_database.delete(shedule_task_id)
        return
    
    
