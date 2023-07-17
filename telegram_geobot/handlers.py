from telegram import ParseMode, Update
from telegram.ext import CallbackContext
from telegram_geobot.db_handlers.geobot_mongodb import mongo_db, get_or_create_user, get_n_sample_from_db
from telegram_geobot.emoji_handlers.flag_emojis import get_n_random_flags, POSITIVE_EMOJI
from telegram_geobot.keyboard import game_keyboard, region_settings_keyboard
from telegram_geobot.prompts.lose_win_replies import WIN_REPLIES, LOSE_REPLIES
from telegram_geobot.prompts.intro_text import INTRO_TEXT
from random import choice, sample
from telegram_geobot.config import settings as pydantic_settings
from glob import glob
from telegram_geobot.logs.log_config import logger
from datetime import datetime
from telegram_geobot.db_handlers.geobot_mongodb import mongo_db


def start_handler(update: Update, context: CallbackContext) -> None:
    user = get_or_create_user(
        mongo_db, update.effective_user, update.message.chat.id
    )
    
    random_flags = get_n_random_flags(6)
    first_half_flags = ''.join(random_flags[ :3])
    second_half_flags = ''.join(random_flags[3: ])
    
    intro_text = choice(INTRO_TEXT)
    update.message.reply_text(
        f'''{first_half_flags} <b>"Географичка"</b> {second_half_flags}

<span class='tg-spoiler'>{intro_text}</span>

<b>Что я умею:</b>

1) /flag - поиграть во флаги
2) /position - сыграть в атлас
3) /regions - выбрать регионы для игры
4) /stats - статистика игр

''',
    parse_mode=ParseMode.HTML)


def game_handler(update: Update, context: CallbackContext) -> None:
    user = get_or_create_user(
        mongo_db, update.effective_user, update.message.chat.id
    )
    user_chat_id = update.effective_chat.id

    regions_for_game = [el for el in user['active_regions'] if user['active_regions'][el]]
    answer_options = get_answer_options(
        mongo_db,
        regions_for_game=regions_for_game,
        n_answer_options=4
    )
    
    question = choice(answer_options)
    game_name = update.message.text
    
    if game_name == '/flag':
        img_dir = pydantic_settings.flag_img_dir
    if game_name == '/position':
        img_dir = pydantic_settings.position_img_dir

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

    lose_replies = LOSE_REPLIES
    win_replies = WIN_REPLIES
    
    if cb_data['user_win']:
        init_reply = choice(win_replies)
    else:
        init_reply = choice(lose_replies)
    
    answer_options_text = '\n'.join(cb_data['answer_options_pretty'])
    
    text = f"<span class='tg-spoiler'><b>{init_reply}</b></span>{chr(10)}{chr(10)}"
    text += f"<b>Ваш ответ:{chr(10)}</b><i>{cb_data['user_answer_pretty']}</i>{chr(10)}{chr(10)}"
    text += f"<span class='tg-spoiler'><b>Варианты ответа:</b>{chr(10)}{answer_options_text}</span>"
    text += f"<b>{chr(10)}{chr(10)}Флаги:</b> /flag"
    text += f"<b>{chr(10)}Атлас:</b> /position"
    text += f"<b>{chr(10)}Старт:</b> /start"
    
    
    update.callback_query.edit_message_caption(
        caption=text,
        parse_mode=ParseMode.HTML,
    )

    game_collection_data = {
        'game_time_utc': datetime.utcnow(),
        'user_id': query.from_user.id,
        'user_name': query.from_user.full_name,
        'user_chat': query.from_user.link,
        'game_name': cb_data['game_name'],
        'user_win': cb_data['user_win'],
        'answer_options_pretty': '||'.join(cb_data['answer_options_pretty']),
        'correct_answer': cb_data['user_answer_pretty'],
        'answer_options_alpha_3': '||'.join(cb_data['answer_options_alpha_3']),
        'correct_answer_alpha_3': cb_data['user_answer_alpha_3'],
    }
    
    try:
        mongo_db['games'].insert_one(game_collection_data)
    except Exception as e:
        logger.error(e, 'Could not write game data to games collection.')
    
    return update.callback_query.data


def get_answer_options(db, regions_for_game: list[str], n_answer_options: int) -> list:
    '''Function that pick n db elements to present them as options to the question.
    One of the options later becomes a question by simple random pick'''

    countries_sample = get_n_sample_from_db(db, n_answer_options, regions_for_game=regions_for_game)

    len_countries = len(countries_sample)
    random_order = sample(range(len_countries), len_countries)

    countries_ordered_aux = zip(countries_sample, random_order)
    answer_options = [el[0] for el in sorted(countries_ordered_aux, key = lambda x: x[1])]

    logger.info(f"Final answer options order: {', '.join([el['country_name'] for el in answer_options])}")

    return answer_options


def regions(update: Update, context: CallbackContext):
    user_data = get_or_create_user(mongo_db, update.effective_user, update.message.chat.id)
    user_active_regions = user_data['active_regions']
    logger.info('Вызван /regions ')
    
    update.message.reply_text(
        f'{choice(POSITIVE_EMOJI)} Во что играем? {choice(POSITIVE_EMOJI)}',
        reply_markup=region_settings_keyboard(user_active_regions)
    )

    return user_active_regions

def region_button_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query_data = query.data
    user_active_regions = query_data['user_active_regions']
    button_pressed = query_data['button_pressed_data']
    user_id = query.from_user.id
    collection = mongo_db['users']

    updated_active_regions = {f"$set": {f"active_regions.{button_pressed}": not user_active_regions[button_pressed]}}
    collection.update_one({"user_id": user_id}, updated_active_regions)
    
    new_active_regions = collection.find_one({'user_id': user_id})['active_regions']
    updated_keyboard = region_settings_keyboard(new_active_regions)

    update.callback_query.edit_message_text(
        f'{choice(POSITIVE_EMOJI)} Во что играем? {choice(POSITIVE_EMOJI)}',
        reply_markup=updated_keyboard
    )

def get_user_stats(update: Update, context: CallbackContext) -> None:
    collection = mongo_db['games']
    user_id = update.effective_chat.id
    games_count = collection.count_documents({'user_id': user_id})
    wins = collection.count_documents({'user_id': user_id, 'user_win': True})
    loses = games_count - wins

    flag_game_count = collection.count_documents({'user_id': user_id, 'game_name': '/flag'})
    flag_wins = collection.count_documents({'user_id': user_id, 'game_name': '/flag', 'user_win': True})
    flag_loses = flag_game_count - flag_wins

    position_game_count = collection.count_documents({'user_id': user_id, 'game_name': '/position'})
    position_wins = collection.count_documents({'user_id': user_id, 'game_name': '/position', 'user_win': True})
    position_loses = position_game_count - position_wins

    total_games = flag_game_count + position_game_count
    total_wins = flag_wins + position_wins
    total_loses = flag_loses + position_loses

    flags1 = ''.join(get_n_random_flags(9))
    flags2 = ''.join(get_n_random_flags(9))
    update.message.reply_text(
        f'''
{choice(POSITIVE_EMOJI)} <b>Статистика игр</b> {choice(POSITIVE_EMOJI)}

<u><b>Всего сыграно:</b></u> {total_games}
<b>🏆 Выигрыш:</b>  {total_wins} (<i>{total_wins/total_games*100:.0f}%</i>)
<b>🦖 Проигрыш:</b> {total_loses} (<i>{total_loses/total_games*100:.0f}%</i>)

{flags1}
<span class='tg-spoiler'>
<u><b>Игра "Флаги":</b></u> {flag_game_count}
<b>🏆 Выигрыш:</b>  {flag_wins} (<i>{flag_wins/flag_game_count*100:.0f}%</i>)
<b>🦋 Проигрыш:</b> {flag_loses} (<i>{flag_loses/flag_game_count*100:.0f}%</i>)

{flags2}

<u><b>Игра "Атлас":</b></u> {position_game_count}
<b>🏆 Выигрыш:</b>  {position_wins} (<i>{position_wins/position_game_count*100:.0f}%</i>)
<b>🧩 Проигрыш:</b> {position_loses} (<i>{position_loses/position_game_count*100:.0f}%</i>)
</span>
''',
parse_mode=ParseMode.HTML)


if __name__ == '__main__':
    print('Hello world!')