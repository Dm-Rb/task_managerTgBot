from aiogram.fsm.state import StatesGroup, State


class CreateTaskStates(StatesGroup):  # FSM для логического бока create_task
    choosing_template = State()  # выбор шаблона из списка готовых шаблонов задач
    waiting_template_title = State()  # создание нового шаблона: ожидание заголовка шаблона задач
    waiting_template_description = State()  # создание нового шаблона: ожидание описания шаблона задач
    choosing_group = State()  # выбор группы для задачи
    choosing_performer = State()  # выбор исполнителя для задачи
    choosing_priority = State()  # выбор приоритета задачи
    choosing_task_type = State()  # типа задачи (разовая\цикличная)
    choosing_repeat = State()
    waiting_confirmation = State()


class CompleteTaskStates(StatesGroup):  # FSM для логического бока completing_task

    waiting_media = State()
    waiting_comment = State()