import logging
from config import my_log_format, API_TOKEN
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram_geobot.handlers import (start_handler, game_handler, game_callback, settings)

logging.basicConfig(
    level=logging.INFO, format=my_log_format, filename='telegram_geobot/bot.log'
)

def main():
    geo_bot = Updater(API_TOKEN, use_context=True, arbitrary_callback_data=True)

    dp = geo_bot.dispatcher
    
    dp.add_handler(CommandHandler("start", start_handler))
    dp.add_handler(CallbackQueryHandler(game_callback))
    dp.add_handler(CommandHandler(["flag", "position"], game_handler))
    dp.add_handler(CommandHandler("settings", settings))
    geo_bot.start_polling()
    geo_bot.idle()

if __name__ == '__main__':
    main()
