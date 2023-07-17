import learn_bot.config as config
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from db_handlers.db_interface import select_db_country_titles, country_title_get_db_row
from telegram_geobot.prompts.lose_win_replies import WIN_REPLIES, LOSE_REPLIES
from telegram_geobot.logs.log_config import logger


def random_countries():
    sample = random.sample(select_db_country_titles(), 4)
    logger.info(sample)
    question = random.choice(sample)
    logger.info(question)
    wrong_replies = LOSE_REPLIES
    correct_replies = WIN_REPLIES
    question_dict = {}
    for c in sample:
        if c != question:
            question_dict[c] = f"{random.choice(wrong_replies)}: <b>{question}</b>."
        else:
            question_dict[c] = f"{random.choice(correct_replies)}! <b>{question}</b>."

    logger.info(question_dict)
    question_country_row = country_title_get_db_row(question)

    q_types = {
        "position_on_map_image_bytes": "<b>Что за страна изображена на карте?</b>",
        "country_flag_bytes": "<b>Флаг какой страны изображен на рисунке?</b>"
    }

    question_to_ask = random.choice(list(q_types.keys()))

    return {"sample": sample,
            "replies": question_dict,
            "question_country": question_country_row,
            "question": q_types[question_to_ask],
            "image": question_country_row[question_to_ask]}


def start(update: Update, context: CallbackContext) -> None:
    """Sends a message with three inline buttons attached."""
    countries = random_countries()
    q = countries["sample"]
    logger.info(q)
    r = countries["replies"]
    logger.info(r)
    img = countries["image"]

    logger.info("-"*100)
    for i in range(4):
        logger.info(f"{q[i]} ::: {r[q[i]]}")
        logger.info(f"{len(q[i].encode('UTF-8'))}::: {len(r[q[i]].encode('UTF-8'))}")
    logger.info("-"*100)
    logger.info(countries["question"])
    keyboard = [
        [
            InlineKeyboardButton(q[0], callback_data=r[q[0]]),
            InlineKeyboardButton(q[1], callback_data=r[q[1]])
        ],
        [
            InlineKeyboardButton(q[2], callback_data=r[q[2]]),
            InlineKeyboardButton(q[3], callback_data=r[q[3]])
        ]
    ]

    chat_id = update.message.chat.id
    context.bot.send_photo(chat_id=chat_id, photo=img)

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(countries["question"], reply_markup=reply_markup, parse_mode="HTML")


def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    query.edit_message_text(text=query.data, parse_mode="HTML")


def help_command(update: Update, context: CallbackContext) -> None:
    """Displays info on how to use the bot."""
    update.message.reply_text("Use /start *to test* this bot", parse_mode="HTML")


def main() -> None:
    updater = Updater(config.api_token, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help_command))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()