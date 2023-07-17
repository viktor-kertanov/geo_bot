from telegram_geobot.config import settings as pydantic_settings
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram_geobot.handlers import (start_handler, game_handler, game_callback, regions, region_button_callback, get_user_stats)
from telegram_geobot.logs.log_config import logger

def region_callback_verifier(cb_data: dict[str]):
    if cb_data['callback_name_id'] == 'region_settings_callback_id':
        return True
    return False

def game_callback_verifier(cb_data: dict[str]):
    if cb_data['callback_name_id'] == 'play_game_callback_id':
        return True
    return False

def main():
    geo_bot = Updater(
        pydantic_settings.telegram_api_token,
        use_context=True,
        arbitrary_callback_data=True
    )

    dp = geo_bot.dispatcher
    dp.add_handler(CommandHandler("start", start_handler))
    dp.add_handler(CallbackQueryHandler(region_button_callback, pattern=region_callback_verifier))
    dp.add_handler(CallbackQueryHandler(game_callback, pattern=game_callback_verifier))
    dp.add_handler(CommandHandler(["flag", "position"], game_handler))
    dp.add_handler(CommandHandler('regions', regions))
    dp.add_handler(CommandHandler('stats', get_user_stats))


    geo_bot.start_polling()
    geo_bot.idle()
if __name__ == '__main__':
    main()
