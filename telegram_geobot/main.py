from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    InvalidCallbackData,
    Updater,
)

from telegram_geobot.callback_verifiers import (
    game_callback_verifier,
    region_callback_verifier,
)
from telegram_geobot.config import settings as pydantic_settings
from telegram_geobot.handlers import (
    game_callback,
    game_handler,
    get_user_stats,
    invalid_callback_handler,
    region_button_callback,
    regions,
    start_handler,
)


def main():
    geo_bot = Updater(
        pydantic_settings.telegram_api_token,
        use_context=True,
        arbitrary_callback_data=True,
    )

    dp = geo_bot.dispatcher
    dp.add_handler(
        CallbackQueryHandler(invalid_callback_handler, pattern=InvalidCallbackData)
    )
    dp.add_handler(
        CallbackQueryHandler(region_button_callback, pattern=region_callback_verifier)
    )
    dp.add_handler(CallbackQueryHandler(game_callback, pattern=game_callback_verifier))
    dp.add_handler(CallbackQueryHandler(game_handler, pattern="flag_play_please"))
    dp.add_handler(CallbackQueryHandler(game_handler, pattern="position_play_please"))
    dp.add_handler(CallbackQueryHandler(start_handler, pattern="start_please"))
    dp.add_handler(CallbackQueryHandler(get_user_stats, pattern="stats_please"))
    dp.add_handler(CallbackQueryHandler(regions, pattern="change_regions_please"))

    dp.add_handler(CommandHandler("start", start_handler))
    dp.add_handler(CommandHandler(["flag", "position"], game_handler))
    dp.add_handler(CommandHandler("regions", regions))
    dp.add_handler(CommandHandler("stats", get_user_stats))

    geo_bot.start_polling()
    geo_bot.idle()


if __name__ == "__main__":
    main()
