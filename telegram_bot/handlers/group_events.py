from aiogram import Router
from aiogram.types import ChatMemberUpdated
from telegram_bot.models.group import Group


router = Router(name="group_events")


@router.my_chat_member()
async def bot_status_in_group_updated(event: ChatMemberUpdated, group_service):
    """Отслеживаем все изменения статуса бота в группе"""

    old = event.old_chat_member  # предыдущий статус участника (до изменения)
    new = event.new_chat_member  # новый (текущий) статус участника (после изменения)
    chat = event.chat # информация о группе
    old_status = old.status
    new_status = new.status

    # 1. Бота добавили в группу
    if old_status in ("left", "kicked") and new_status in ("member", "administrator", "creator"):
        is_admin = new_status in ("administrator", "creator")

        await event.bot.send_message(
            chat.id,
            f"{'Бот был добавлен в группу.' if is_admin else 'Бот был добавлен в группу. Необходимо выдать права администратора'}"
        )
        group = Group(
            tg_id=chat.id,
            title=chat.title,
            is_admin=True if is_admin else False
        )

        await group_service.add_group(group)

    # 2. Изменили права администратора
    elif old_status == "member" and new_status in ("administrator", "creator"):
        await event.bot.send_message(
            chat.id,
            f"Боту были выдадены права администатора"
        )
        group = Group(
            tg_id=chat.id,
            title=chat.title,
            is_admin=True
        )

        await group_service.add_group(group)
        # groups = await group_service.get_all_groups()
        #
        # for group in groups:
        #     print(group.tg_id, group.title, group.is_admin)

    # 3. Бота кикнули или удалили
    elif new_status in ("left", "kicked") and old_status not in ("left", "kicked"):
        await group_service.remove_group(tg_id=chat.id)
