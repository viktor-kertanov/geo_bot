from telegram import ParseMode, Update
from telegram.ext import CallbackContext
from telegram_geobot.db_handlers.geobot_mongodb import mongo_db, get_or_create_user, get_n_sample_from_db
from telegram_geobot.emoji_handlers.flag_emojis import get_n_random_flags
from telegram_geobot.keyboard import game_keyboard
from random import choice, sample
from config import FLAG_IMG_DIR, POSITION_IMG_DIR
from glob import glob


def start_handler(update: Update, context: CallbackContext) -> None:
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


def game_handler(update: Update, context: CallbackContext) -> None:
    user = get_or_create_user(
        mongo_db, update.effective_user, update.message.chat.id
    )
    user_chat_id = update.effective_chat.id

    answer_options = get_answer_options(mongo_db, n_answer_options=4)
    
    question = choice(answer_options)
    game_name = update.message.text
    
    if game_name == '/flag':
        img_dir = FLAG_IMG_DIR
    if game_name == '/position':
        img_dir = POSITION_IMG_DIR

    question_img = [
        el for el in glob(f'{img_dir}*.jpeg')
        if question['iso_alpha_3_code'] in el
    ][0]
    

    keyboard = game_keyboard(answer_options, question, game_name)
    
    context.bot.send_photo(
        chat_id=user_chat_id,
        photo=open(question_img, 'rb'),
        reply_markup=keyboard
    )


def game_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    cb_data = update.callback_query.data
    lose_replies = ["Неправильно🫣", "Надо подучить🌊", "Не повезло🧐", "Жаль🙇‍♂️", "Старайтесь🪢"]
    win_replies = ["Сила знания🌏", "Всё верно🌍", "Вы географ🌎", "Правильно🗺"]
    if cb_data['user_win']:
        init_reply = choice(win_replies)
    else:
        init_reply = choice(lose_replies)
    answer_options_text = '\n'.join(cb_data['answer_options_pretty'])
    
    text = f"<b>{init_reply} </b>{chr(10)}{chr(10)}<b>Ваш ответ:{chr(10)}</b><i>{cb_data['user_answer_pretty']}</i>{chr(10)}{chr(10)}<b>Варианты ответа:</b>{chr(10)}{answer_options_text}"
    
    update.callback_query.edit_message_caption(
        caption=text,
        parse_mode=ParseMode.HTML
    )
    
    return update.callback_query.data


def get_answer_options(db, n_answer_options: int) -> list:
    '''Function that pick n db elements to present them as options to the question.
    One of the options later becomes a question by simple random pick'''

    countries_sample = get_n_sample_from_db(db, n_answer_options)
    # print(f"Initial order: {', '.join([el['country_name'] for el in countries_sample])}")

    len_countries = len(countries_sample)
    random_order = sample(range(len_countries), len_countries)
    # print(f"Random sequence is: {', '.join([str(el) for el in random_order])}")
    
    countries_ordered_aux = zip(countries_sample, random_order)
    answer_options = [el[0] for el in sorted(countries_ordered_aux, key = lambda x: x[1])]

    print(f"Final answer options order: {', '.join([el['country_name'] for el in answer_options])}")

    return answer_options


if __name__ == '__main__':
    print('Hello world!')