from telegram_geobot.db_handlers.geobot_mongodb import mongo_db, get_or_create_user
from telegram import ParseMode
from telegram_geobot.keyboard import flag_keyboard
import os
from os.path import join, isfile
from random import choice


def start_handler(update, context):
    update.message.reply_text(
        '''Бот 🌏 <b>"Географию учи"</b> 🌍!

Я помогу тебе выучить 🇫🇴 🇺🇾 <b>флаги</b> 🇬🇫 🇸🇨 стран мира, а также научу определять страны по их местоположению.

<b>Что я умею:</b>

1) /flags - поиграть во флаги;
2) /position - угадать страну по местоположению

''',
    parse_mode=ParseMode.HTML)

def flag_handler(update, context):
    user = get_or_create_user(
        mongo_db, update.effective_user, update.message.chat.id
    )

    flags_dir = "data/country_images_aux/"
    flags = [
        f'{flags_dir}{f}' for f in os.listdir(flags_dir)
        if isfile(join(flags_dir, f)) and 'flag' in f and '.jpeg' in f
    ]
    flag_to_send = choice(flags)
    print(flag_to_send)
    country = flag_to_send.split('/')[-1].split('_')[0].capitalize()
    usr_chat_id = update.effective_chat.id
    
    keyboard = flag_keyboard()
    context.bot.send_photo(
        chat_id=usr_chat_id,
        photo=open(flag_to_send, 'rb'),
        reply_markup=keyboard
    )