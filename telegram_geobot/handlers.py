from datetime import datetime
from glob import glob
from random import choice, random

from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from telegram_geobot.config import settings as pydantic_settings
from telegram_geobot.db.geobot_mongodb import (
    get_answer_options,
    get_or_create_user,
    mongo_db,
)
from telegram_geobot.flag_emojis import POSITIVE_EMOJI, get_n_random_flags
from telegram_geobot.keyboard import (
    game_keyboard,
    menu_keyboard,
    region_settings_keyboard,
)
from telegram_geobot.logs.log_config import logger
from telegram_geobot.menu_delete import remove_keyboard_on_root_message
from telegram_geobot.prompts.intro_text import INTRO_TEXT
from telegram_geobot.prompts.lose_win_replies import (
    LOSE_REPLIES,
    WIN_REPLIES,
    WIN_REPLIES_SHORT,
)


def start_handler(update: Update, context: CallbackContext) -> None:
    user_chat_id = update.effective_chat.id
    get_or_create_user(mongo_db, update.effective_user, user_chat_id)

    random_flags = get_n_random_flags(6)

    intro_text = choice(INTRO_TEXT)
    message_to_send = f"""{''.join(random_flags[ :3])} <b>"Географичка"</b> {''.join(random_flags[3: ])}

<span class='tg-spoiler'>{intro_text}</span>

"""
    message = context.bot.send_message(
        chat_id=user_chat_id,
        text=message_to_send,
        parse_mode=ParseMode.HTML,
        reply_markup=menu_keyboard(start_button_exists=False),
    )

    context.chat_data["root_message_id"] = message.message_id


@remove_keyboard_on_root_message
def game_handler(update: Update, context: CallbackContext) -> None:
    user_chat_id = update.effective_chat.id

    user = get_or_create_user(mongo_db, update.effective_user, user_chat_id)

    regions_for_game = [
        el for el in user["active_regions"] if user["active_regions"][el]
    ]
    answer_options = get_answer_options(
        mongo_db, regions_for_game=regions_for_game, n_answer_options=4
    )

    question = choice(answer_options)

    try:
        callback_data = update.callback_query.data
        if callback_data == "flag_play_please":
            game_name = "/flag"
        if callback_data == "position_play_please":
            game_name = "/position"

    except AttributeError:
        logger.info("No callback data")
        game_name = update.message.text

    if game_name == "/flag":
        img_dir = pydantic_settings.flag_img_dir
    if game_name == "/position":
        img_dir = pydantic_settings.position_img_dir

    logger.info(img_dir)
    question_img = [
        el for el in glob(f"{img_dir}*.jpeg") if question["iso_alpha_3_code"] in el
    ][0]

    keyboard = game_keyboard(answer_options, question, game_name)

    context.bot.send_photo(
        chat_id=user_chat_id, photo=open(question_img, "rb"), reply_markup=keyboard
    )


def game_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    cb_data = query.data

    lose_replies = LOSE_REPLIES

    win_prompt_chance = random()
    if win_prompt_chance < 0.3:
        win_replies = WIN_REPLIES
    else:
        win_replies = WIN_REPLIES_SHORT

    if cb_data["user_win"]:
        init_reply = choice(win_replies)
    else:
        init_reply = choice(lose_replies)

    answer_options_text = "\n".join(cb_data["answer_options_pretty"])

    text = f"<b>{init_reply}</b>{chr(10)}{chr(10)}"
    text += f"<b>Ваш ответ:{chr(10)}</b><i>{cb_data['user_answer_pretty']}</i>{chr(10)}{chr(10)}"
    text += f"<span class='tg-spoiler'><b>Варианты ответов:</b>{chr(10)}{answer_options_text}</span>"

    message = update.callback_query.edit_message_caption(
        caption=text,
        reply_markup=menu_keyboard(
            cb_data["country_emoji"], cb_data["ru_wiki_article"]
        ),
        parse_mode=ParseMode.HTML,
    )
    context.chat_data["root_message_id"] = message.message_id
    # Storing data to the database
    game_collection_data = {
        "game_time_utc": datetime.utcnow(),
        "user_id": query.from_user.id,
        "user_name": query.from_user.full_name,
        "user_chat": query.from_user.link,
        "game_name": cb_data["game_name"],
        "user_win": cb_data["user_win"],
        "answer_options_pretty": "||".join(cb_data["answer_options_pretty"]),
        "correct_answer": cb_data["user_answer_pretty"],
        "answer_options_alpha_3": "||".join(cb_data["answer_options_alpha_3"]),
        "correct_answer_alpha_3": cb_data["user_answer_alpha_3"],
    }

    try:
        mongo_db["games"].insert_one(game_collection_data)
    except Exception as e:
        logger.error(e, "Could not write game data to games collection.")

    return update.callback_query.data


def regions(update: Update, context: CallbackContext):
    if update.message:
        chat_id = update.message.chat.id
    else:
        chat_id = update.effective_chat.id
    user_data = get_or_create_user(mongo_db, update.effective_user, chat_id)
    user_active_regions = user_data["active_regions"]

    message = context.bot.send_message(
        chat_id=chat_id,
        text=f"{choice(POSITIVE_EMOJI)} Выбери регионы для игры {choice(POSITIVE_EMOJI)}",
        reply_markup=region_settings_keyboard(user_active_regions),
    )
    context.chat_data["message_id"] = message.message_id
    context.chat_data["menu_keyboard_sent"] = False
    return user_active_regions


def region_button_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query_data = query.data
    user_active_regions = query_data["user_active_regions"]
    button_pressed = query_data["button_pressed_data"]
    user_id = query.from_user.id
    collection = mongo_db["users"]

    if update.message:
        chat_id = update.message.chat.id
    else:
        chat_id = update.effective_chat.id

    active_regions_true = [key for key, value in user_active_regions.items() if value]

    if len(active_regions_true) == 1 and active_regions_true[0] == button_pressed:
        emojis = ["✅", "🦋", "🌈", "🙏🏻", "🐛", "🤨"]
        choice_emoji = choice(emojis)
        context.bot.send_message(
            chat_id=chat_id,
            text=f"{choice_emoji} Должен быть выбран хотя бы один регион {choice_emoji}",
        )
        new_active_regions = user_active_regions
    else:
        updated_active_regions = {
            "$set": {
                f"active_regions.{button_pressed}": not user_active_regions[
                    button_pressed
                ]
            }
        }
        collection.update_one({"user_id": user_id}, updated_active_regions)
        new_active_regions = collection.find_one({"user_id": user_id})["active_regions"]

    updated_keyboard = region_settings_keyboard(new_active_regions)

    query.edit_message_text(
        f"{choice(POSITIVE_EMOJI)} Выбери регионы для игры {choice(POSITIVE_EMOJI)}",
        reply_markup=updated_keyboard,
    )


def get_user_stats(update: Update, context: CallbackContext) -> None:
    collection = mongo_db["games"]

    if update.message:
        user_id = update.message.from_user.id
        chat_id = update.message.chat.id
    else:
        user_id = update.callback_query.from_user.id
        chat_id = update.effective_chat.id

    flag_game_count = collection.count_documents(
        {"user_id": user_id, "game_name": "/flag"}
    )
    flag_wins = collection.count_documents(
        {"user_id": user_id, "game_name": "/flag", "user_win": True}
    )
    flag_loses = flag_game_count - flag_wins

    position_game_count = collection.count_documents(
        {"user_id": user_id, "game_name": "/position"}
    )
    position_wins = collection.count_documents(
        {"user_id": user_id, "game_name": "/position", "user_win": True}
    )
    position_loses = position_game_count - position_wins

    total_games = flag_game_count + position_game_count
    total_wins = flag_wins + position_wins
    total_loses = flag_loses + position_loses

    stats_body = f"""
{choice(POSITIVE_EMOJI)} <b>Статистика игр</b> {choice(POSITIVE_EMOJI)}

<u><b>Всего сыграно:</b></u> {total_games}
<b>🏆 Выигрыш:</b>  {total_wins} (<i>{total_wins/total_games*100:.0f}%</i>)
<b>🦖 Проигрыш:</b> {total_loses} (<i>{total_loses/total_games*100:.0f}%</i>)

<span class='tg-spoiler'>
<u><b>Игра "Флаги":</b></u> {flag_game_count}
<b>🏆 Выигрыш:</b>  {flag_wins} (<i>{flag_wins/flag_game_count*100:.0f}%</i>)
<b>🦖 Проигрыш:</b> {flag_loses} (<i>{flag_loses/flag_game_count*100:.0f}%</i>)


<u><b>Игра "Атлас":</b></u> {position_game_count}
<b>🏆 Выигрыш:</b>  {position_wins} (<i>{position_wins/position_game_count*100:.0f}%</i>)
<b>🦖 Проигрыш:</b> {position_loses} (<i>{position_loses/position_game_count*100:.0f}%</i>)
</span>
"""
    message = context.bot.send_message(
        chat_id=chat_id,
        text=stats_body,
        parse_mode=ParseMode.HTML,
        reply_markup=menu_keyboard(only_start_button=True),
    )
    context.chat_data["root_message_id"] = message.message_id


if __name__ == "__main__":
    print("Hello world!")
