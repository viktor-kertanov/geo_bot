import logging
from config import my_log_format, API_TOKEN
from telegram.ext import Updater


logging.basicConfig(
    level=logging.INFO, format=my_log_format, filename='telegram_geobot/bot.log'
)

def main():
    geo_bot = Updater(API_TOKEN, use_context=True)

    geo_bot.start_polling()
    geo_bot.idle()

if __name__ == '__main__':
    main()
