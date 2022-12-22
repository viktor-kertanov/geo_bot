import logging
from config import my_log_format, API_TOKEN
from telegram.ext import Updater, CommandHandler
from telegram_geobot.handlers import start_handler, flag_handler

logging.basicConfig(
    level=logging.INFO, format=my_log_format, filename='telegram_geobot/bot.log'
)

def main():
    geo_bot = Updater(API_TOKEN, use_context=True)

    dp = geo_bot.dispatcher
    
    dp.add_handler(CommandHandler("start", start_handler))
    dp.add_handler(CommandHandler("flags", flag_handler))

    geo_bot.start_polling()
    geo_bot.idle()

if __name__ == '__main__':
    main()
