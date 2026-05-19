from aiogram import Router, F
from aiogram.types import Message

from telegram_bot.models.group import GroupTopic


router = Router()


@router.message(F.is_topic_message == True)
async def forum_topic_handler(
    message: Message,
    group_service
):

    chat = message.chat

    if not chat.is_forum:
        return

    topic_id = message.message_thread_id

    if not topic_id:
        return

    # ==========================================
    # GET GROUP
    # ==========================================

    group = group_service.get_group_by_id(chat.id)

    if not group:
        return

    # ==========================================
    # UPDATE FORUM FLAG
    # ==========================================

    # если группа ещё не помечена как форум
    if not group.is_forum:

        group.is_forum = True

        # обновляем кеш + БД
        await group_service.add_group(group)

    # ==========================================
    # CHECK EXISTS
    # ==========================================

    topic_exists = any(
        t.topic_id == topic_id
        for t in group.topics
    )

    # уже зарегистрирован
    if topic_exists:
        return

    # ==========================================
    # TOPIC TITLE
    # ==========================================

    topic_title = None

    # Telegram присылает имя только
    # при создании топика
    if message.forum_topic_created:
        topic_title = message.forum_topic_created.name

    # fallback
    if not topic_title:
        topic_title = f"Topic {topic_id}"

    # ==========================================
    # SAVE TOPIC
    # ==========================================

    topic = GroupTopic(
        topic_id=topic_id,
        title=topic_title
    )

    await group_service.add_topic(
        group_id=chat.id,
        topic=topic
    )

    # ==========================================
    # SEND MESSAGE TO TOPIC
    # ==========================================

    await message.bot.send_message(
        chat_id=chat.id,
        message_thread_id=topic_id,
        text=(
            f"✅ Тема зарегистрирована\n\n"
            f"ID: <code>{topic_id}</code>\n"
            f"Название: <b>{topic_title}</b>"
        ),
        parse_mode="HTML"
    )

@router.message(F.forum_topic_closed)
async def forum_topic_deleted_handler(
    message: Message,
    group_service
):
    """
    Удаление топика форума
    """
    chat = message.chat

    if not chat.is_forum:
        return

    topic_id = message.message_thread_id

    if not topic_id:
        return

    # ==========================================
    # GET GROUP
    # ==========================================

    group = group_service.get_group_by_id(chat.id)

    if not group:
        return

    # ==========================================
    # REMOVE FROM CACHE
    # ==========================================

    group.topics = [
        topic
        for topic in group.topics
        if topic.topic_id != topic_id
    ]

    # ==========================================
    # REMOVE FROM DATABASE
    # ==========================================

    await group_service.remove_topic(
        group_id=chat.id,
        topic_id=topic_id
    )

    print(
        f"Топик удалён: "
        f"group_id={chat.id}, "
        f"topic_id={topic_id}"
    )