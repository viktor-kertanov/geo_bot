from config import logging
from learn_bot.anketa import anketa_start, anketa_name, anketa_rating, anketa_skip, anketa_comment, anketa_fallback
from learn_bot.handlers import\
    greet_user, guess_number_handler, send_flag_picture,\
    user_coordinates, talk_to_me, check_user_photo
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from config import API_TOKEN


def main():
    echo_bot = Updater(API_TOKEN, use_context=True)
    
    dp = echo_bot.dispatcher

    anketa = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex("^(Заполнить анкету)$"), anketa_start)
        ],
        states={
            "name": [MessageHandler(Filters.text, anketa_name)],
            "rating": [MessageHandler(Filters.regex("^(1|2|3|4|5)$"), anketa_rating)],
            "comment": [
                CommandHandler('skip', anketa_skip),
                MessageHandler(Filters.text, anketa_comment)
            ]
        },
        fallbacks=[
            MessageHandler(Filters.text|Filters.photo|Filters.video|Filters.document|Filters.location, anketa_fallback)
        ]
    )

    dp.add_handler(anketa)
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(CommandHandler("guess", guess_number_handler))
    dp.add_handler(CommandHandler("flag", send_flag_picture))
    dp.add_handler(MessageHandler(Filters.regex("^(Прислать флаг)$"), send_flag_picture))
    dp.add_handler(MessageHandler(Filters.photo, check_user_photo))
    dp.add_handler(MessageHandler(Filters.location, user_coordinates))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))
    logging.info('Бот стартовал')
    
    echo_bot.start_polling()
    echo_bot.idle()


if __name__ == '__main__':
    main()
