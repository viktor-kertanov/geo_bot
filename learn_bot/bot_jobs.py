from datetime import datetime

from telegram.error import BadRequest

from db_handlers.mongo_db import get_subsribed_users, mongo_db


def send_updates(context):
    now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    for user in get_subsribed_users(mongo_db):
        try:
            context.bot.send_message(
                chat_id=user["chat_id"],
                text=f"Привет {user['first_name']} {user['emoji']}!\
                    \nТекущее время ⏰:\n{now}",
            )
        except (BadRequest, KeyError):
            print(f"Chat ID # {user['chat_id']} not found.")


def send_updates_aux(context):
    context.bot.send_message(
        chat_id=1670826777,
        text=f"привет! {context.job.trigger.interval_length: .0f} cекунд",
    )
    context.job.trigger.interval_length += 10
    if context.job.trigger.interval_length > 40:
        context.bot.send_message(chat_id=1670826777, text="Задание выполнено")
        context.job.schedule_removal()


def vk_alram(context):
    context.bot.send_message(
        chat_id=context.job.context,
        text=f'Сработал будильник ⏰. {datetime.now().strftime("%H:%M:%S")}',
    )
