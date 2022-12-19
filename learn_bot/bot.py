from config import logging
from datetime import time
from learn_bot.bot_jobs import send_updates
from learn_bot.anketa import anketa_start, anketa_name,\
    anketa_rating, anketa_skip, anketa_comment, anketa_fallback
from learn_bot.handlers import\
    greet_user, guess_number_handler, send_flag_picture,\
    user_coordinates, talk_to_me, check_user_photo,\
    subscribe_user_handler, unsubscribe_user_handler, set_alarm,\
    flag_picture_rating
import pytz
from telegram.ext import Updater, CommandHandler, \
                         MessageHandler, Filters, ConversationHandler,\
                         CallbackQueryHandler
from telegram.ext import messagequeue as mq
from telegram.bot import Bot
from telegram.utils.request import Request
from config import API_TOKEN


class MQBot(Bot):
    def __init__(self, *args, is_queued_def=True, msg_queue=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = msg_queue or mq.MessageQueue()

    def __del__(self):
        try:
            self._msg_queue.stop()
        except Exception:
            pass

    @mq.queuedmessage
    def send_message(self, *args, **kwargs):
        return super().send_message(*args, **kwargs)


def main():
    request = Request(con_pool_size=8)

    my_bot = MQBot(API_TOKEN, request=request)
    echo_bot = Updater(bot=my_bot, use_context=True)

    jq = echo_bot.job_queue
    target_time = time(10,  17, tzinfo=pytz.timezone('Europe/Moscow'))
    # jq.run_repeating(send_updates, interval=15, first=1)
    jq.run_daily(send_updates, time=target_time, days=(0, 2, 4))

    dp = echo_bot.dispatcher

    anketa = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex("^(Заполнить анкету)$"), anketa_start)
        ],
        states={
            "name": [MessageHandler(Filters.text, anketa_name)],
            "rating": [MessageHandler(
                Filters.regex("^(1|2|3|4|5)$"),
                anketa_rating)],
            "comment": [
                CommandHandler('skip', anketa_skip),
                MessageHandler(Filters.text, anketa_comment)
            ]
        },
        fallbacks=[
            MessageHandler(
                Filters.text | Filters.photo | Filters.video |
                Filters.document | Filters.location,
                anketa_fallback)
        ]
    )

    dp.add_handler(anketa)
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(CommandHandler("guess", guess_number_handler))
    dp.add_handler(CommandHandler("flag", send_flag_picture))
    dp.add_handler(CommandHandler("subscribe", subscribe_user_handler))
    dp.add_handler(CommandHandler("unsubscribe", unsubscribe_user_handler))
    dp.add_handler(CommandHandler("alarm", set_alarm))
    dp.add_handler(
        CallbackQueryHandler(flag_picture_rating, pattern="^(rating|)")
    )
    dp.add_handler(MessageHandler(Filters.regex(
        "^(Прислать флаг)$"), send_flag_picture)
    )
    dp.add_handler(MessageHandler(Filters.photo, check_user_photo))
    dp.add_handler(MessageHandler(Filters.location, user_coordinates))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    logging.info('Бот стартовал')

    echo_bot.start_polling()
    echo_bot.idle()


if __name__ == '__main__':
    main()
