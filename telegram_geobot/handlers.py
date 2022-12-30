from telegram import ParseMode, ReplyKeyboardRemove, ReplyKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

from telegram_geobot.db_handlers.geobot_mongodb import mongo_db, get_or_create_user, get_n_sample_from_db
from telegram_geobot.emoji_handlers.flag_emojis import get_n_random_flags
from telegram_geobot.keyboard import flag_keyboard, position_keyboard
from random import choice, sample
from config import FLAG_IMG_DIR, POSITION_IMG_DIR
from glob import glob
import json

def start_handler(update: Update, context: CallbackContext):
    user = get_or_create_user(
        mongo_db, update.effective_user, update.message.chat.id
    )
    
    random_flags = get_n_random_flags(6)
    first_half_flags = ''.join(random_flags[ :3])
    second_half_flags = ''.join(random_flags[3: ])
    
    update.message.reply_text(
        f'''{first_half_flags} <b>"Географию учи"</b> {second_half_flags}

Я помогу тебе выучить <b>флаги стран</b>, а также научу определять страны по их местоположению.

<b>Что я умею:</b>

1) /flags - поиграть во флаги;
2) /position - угадать страну по местоположению

''',
    parse_mode=ParseMode.HTML)


def flag_game_handler(update: Update, context: CallbackContext) -> None:
    user = get_or_create_user(
        mongo_db, update.effective_user, update.message.chat.id
    )
    
    answer_options = get_answer_options(mongo_db, n_answer_options=4)
    question = choice(answer_options)

    q_alpha_3 = question['iso_alpha_3_code']
    existing_flags = [
        el for el in glob(f'{FLAG_IMG_DIR}*.jpeg')
        if q_alpha_3 in el
    ]
    
    question_flag = existing_flags[0]

    usr_chat_id = update.effective_chat.id
    
    keyboard = flag_keyboard(answer_options, question)
    context.bot.send_photo(
        chat_id=usr_chat_id,
        photo=open(question_flag, 'rb'),
        reply_markup=keyboard
    )


def flag_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    cb_data = update.callback_query.data
    lose_replies = ["Неправильно🫣", "Подучить🌊", "Не повезло🧐", "Жаль🙇‍♂️", "Старайтесь🪢"]
    win_replies = ["Сила знания🌏", "Всё верно🌍", "Вы географ🌎", "Правильно🗺"]
    if cb_data['user_win']:
        init_reply = choice(win_replies)
    else:
        init_reply = choice(lose_replies)
    answer_options_text = '\n'.join(cb_data['answer_options_pretty'])
    text = f"<b>{init_reply} </b>{chr(10)}{chr(10)}<b>Ваш ответ:{chr(10)}</b><i>{cb_data['user_answer_pretty']}</i>{chr(10)}{chr(10)}<b>Варианты ответа:</b>{chr(10)}{answer_options_text}"
    update.callback_query.edit_message_caption(caption=text, parse_mode=ParseMode.HTML)
    return update.callback_query.data


def position_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    cb_data = update.callback_query.data
    lose_replies = ["Неправильно🫣", "Подучить🌊", "Не повезло🧐", "Жаль🙇‍♂️", "Старайтесь🪢"]
    win_replies = ["Сила знания🌏", "Всё верно🌍", "Вы географ🌎", "Правильно🗺"]
    if cb_data['user_win']:
        init_reply = choice(win_replies)
    else:
        init_reply = choice(lose_replies)
    answer_options_text = '\n'.join(cb_data['answer_options_pretty'])
    text = f"<b>{init_reply} </b>{chr(10)}{chr(10)}<b>Ваш ответ:{chr(10)}</b><i>{cb_data['user_answer_pretty']}</i>{chr(10)}{chr(10)}<b>Варианты ответа:</b>{chr(10)}{answer_options_text}"
    update.callback_query.edit_message_caption(caption=text, parse_mode=ParseMode.HTML)
    return update.callback_query.data


def get_answer_options(db, n_answer_options: int) -> list:
    countries_sample = get_n_sample_from_db(db, n_answer_options)
    print(f"Initial order: {', '.join([el['country_name'] for el in countries_sample])}")

    len_countries = len(countries_sample)
    random_order = sample(range(len_countries), len_countries)
    print(f"Random sequence is: {', '.join([str(el) for el in random_order])}")
    
    countries_ordered_aux = zip(countries_sample, random_order)
    answer_options = [el[0] for el in sorted(countries_ordered_aux, key = lambda x: x[1])]

    print(f"Final order: {', '.join([el['country_name'] for el in answer_options])}")

    return answer_options




def position_game_handler(update, context):
    user = get_or_create_user(
        mongo_db, update.effective_user, update.message.chat.id
    )
    answer_options = get_answer_options(mongo_db, 4)
    question = choice(answer_options)
    q_alpha_3 = question['iso_alpha_3_code']
    q_numeric = question['numeric_code']
    existing_positions = [
        el for el in glob(f'{POSITION_IMG_DIR}*.jpeg')
        if q_alpha_3 in el
    ]
    
    question_flag = existing_positions[0]

    usr_chat_id = update.effective_chat.id
    
    keyboard = position_keyboard(answer_options, question)

    # cb_data = flag_callback(update, context)
    # print(f"User answer is: {cb_data}")

    context.bot.send_photo(
        chat_id=usr_chat_id,
        photo=open(question_flag, 'rb'),
        reply_markup=keyboard, 
    )


if __name__ == '__main__':
    print('Hello world!')