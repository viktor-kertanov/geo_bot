from db_handlers.mongo_db import mongo_db, get_or_create_user,  save_anketa
from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, ParseMode
from telegram.ext import ConversationHandler
from learn_bot.bot_keyboard import main_keyboard


def anketa_start(update, context):
    update.message.reply_text(
        "Введите имя и фамилию, пожалуйста 🙏🏻",
        reply_markup=ReplyKeyboardRemove()
    )
    return "name"


def anketa_name(update, context):
    user_name = update.message.text
    if len(user_name.split()) < 2:
        update.message.reply_text(
            'Введите пожалуйста имя и фамили ю в формате "[Имя]⎵[Фамилия]"'
        )
        return "name"
    else:
        context.user_data["anketa"] = {"name": user_name}
        reply_keyboard = [[1, 2, 3, 4, 5]]
        update.message.reply_text(
            "Пожалуйста оцените нашего бота по шкале от 1 🤮 до 5 😍",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True)
        )
        return "rating"


def anketa_rating(update, context):
    context.user_data["anketa"]["rating"] = update.message.text
    update.message.reply_text(
        "Напишите пожалуйста комментарий или нажмите /skip, чтобы пропустить. "
    )
    return "comment"


def anketa_skip(update, context):
    context.user_data["anketa"]["comment"] = None
    user = get_or_create_user(
        mongo_db, update.effective_user,
        update.message.chat.id
    )
    save_anketa(mongo_db, user['user_id'], context.user_data["anketa"])
    user_text = format_anketa(context.user_data["anketa"])
    update.message.reply_text(
        user_text, reply_markup=main_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END


def anketa_comment(update, context):
    context.user_data["anketa"]["comment"] = update.message.text
    user = get_or_create_user(
        mongo_db,
        update.effective_user, update.message.chat.id
    )
    save_anketa(mongo_db, user['user_id'], context.user_data["anketa"])
    user_text = format_anketa(context.user_data["anketa"])
    update.message.reply_text(
        user_text, reply_markup=main_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END


def format_anketa(anketa):
    user_text = f"""<b>Имя Фамилия: </b> {anketa["name"]}
<b>Оценка: </b> {anketa["rating"]} """
    if anketa["comment"]:
        user_text += f"\n<b>Комментарий: </b> {anketa['comment']}"
    print(anketa)
    return user_text


def anketa_fallback(update, context):
    update.message.reply_text(
        "Были введены данные, которые мы не можем обработать.\n\
        Попробуйте ещё раз ввести данные в правильном формате. "
    )
