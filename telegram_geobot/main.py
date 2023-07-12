from telegram_geobot.config import settings as pydantic_settings
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram_geobot.handlers import (start_handler, game_handler, game_callback)
from telegram_geobot.logs.log_config import logger

def main():
    geo_bot = Updater(
        pydantic_settings.telegram_api_token,
        use_context=True,
        arbitrary_callback_data=True
    )

    dp = geo_bot.dispatcher
    
    dp.add_handler(CommandHandler("start", start_handler))
    dp.add_handler(CallbackQueryHandler(game_callback))
    dp.add_handler(CommandHandler(["flag", "position"], game_handler))
    
    geo_bot.start_polling()
    geo_bot.idle()

if __name__ == '__main__':
    main()
