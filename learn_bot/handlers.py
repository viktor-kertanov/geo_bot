from config import logging
from datetime import datetime
from db_handlers.mongo_db import mongo_db, get_or_create_user,\
                                 subscribe_user, unsubscribe_user,\
                                 save_flag_img_vote, user_voted,\
                                 get_flag_img_rating
from learn_bot.bot_keyboard import main_keyboard, img_rating_inline_keyboard
from learn_bot.emoji_handler import emoji_by_string
from learn_bot.guess_game import guess_number_game, get_bot_number
from learn_bot.clarifai_handler import (object_exists_on_img,
                                        clarifai_processor, what_is_on_picture)
from learn_bot.bot_jobs import vk_alram
import os
from os.path import isfile, join
from random import choice


def greet_user(update, context):
    user = get_or_create_user(
        mongo_db, update.effective_user, update.message.chat.id
    )
    print('Вызван /start, vk')
    update.message.reply_text(
        f"Привет! {user['emoji']}",
        reply_markup=main_keyboard()
        )


def guess_number_handler(update, context):
    get_or_create_user(
        mongo_db,  update.effective_user, update.message.chat.id
    )
    usr_msg = update.message.text
    print(f'user message is: {usr_msg}')

    try:
        user_number = usr_msg.split(' ')[-1]
        user_number = int(user_number)
        print(f'user number is {user_number}.')
        bot_number = get_bot_number(user_number, random_interval=10)
        print(f'bot number is {bot_number}.')
        update.message.reply_text(guess_number_game(user_number, bot_number))

    except (TypeError, ValueError) as e:
        error_msg = 'Вы не умеете играть в эту игру.\
             Напишите "/guess n", где n - целое число.'
        print(error_msg)
        logging.info(f'Our error looks like this: {e}')
        update.message.reply_text(error_msg)


def send_flag_picture(update, context):
    user = get_or_create_user(
        mongo_db, update.effective_user, update.message.chat.id
    )
    flags_dir = "data/country_images_aux/"
    flags = [
        f'{flags_dir}{f}' for f in os.listdir(flags_dir)
        if isfile(join(flags_dir, f)) and 'flag' in f and '.jpeg' in f
    ]
    flag_to_send = choice(flags)
    country = flag_to_send.split('/')[-1].split('_')[0].capitalize()
    usr_chat_id = update.effective_chat.id

    rating = get_flag_img_rating(mongo_db, flag_to_send)

    if user_voted(mongo_db, flag_to_send, user['user_id']):
        keyboard = None
        flag_caption = f"Рейтинг картинки {country}: {rating} 🧛🏻‍♂️"
    else:
        keyboard = img_rating_inline_keyboard(flag_to_send)
        flag_caption = None

    context.bot.send_photo(
        chat_id=usr_chat_id,
        photo=open(flag_to_send, 'rb'),
        reply_markup=keyboard,
        caption=flag_caption
    )

    return flags


def talk_to_me(update, context):
    user = get_or_create_user(
        mongo_db,  update.effective_user, update.message.chat.id
    )
    text_to_repeat = update.message.text

    update.message.reply_text(
        f"{text_to_repeat} {user['emoji']}",
        reply_markup=main_keyboard())

    internal_msg = f'We have just echoed: "{text_to_repeat}"'
    logging.info(internal_msg)
    print(internal_msg)
    return None


def user_coordinates(update, context):
    user = get_or_create_user(
        mongo_db,  update.effective_user, update.message.chat.id
    )
    coords = update.message.location
    update.message.reply_text(f"Ваши координаты:\n{coords} {user['emoji']}")
    print(coords)


def check_user_photo(update, context, default_object='cat'):
    get_or_create_user(
        mongo_db,  update.effective_user, update.message.chat.id
    )
    confidence = 0.9
    caption = update.message.caption.strip().lower().split()[0]
    if caption:
        object = caption
    else:
        object = default_object

    update.message.reply_text('Обрабатываем фото 🌈')
    os.makedirs('learn_bot/downloads', exist_ok=True)
    print(update.message.photo[-1])
    file_id = update.message.photo[-1].file_id
    photo_file = context.bot.getFile(file_id)
    filename = join('learn_bot/downloads', f'{file_id}.jpeg')
    photo_file.download(filename)

    ai_response = clarifai_processor(filename)
    what_on_img = what_is_on_picture(ai_response, min_confidence=confidence)
    what_on_img = [el.name for el in what_on_img]
    object_exists = object_exists_on_img(
        ai_response, object, min_confidence=confidence
    )

    if object_exists:
        emoji = emoji_by_string(object)
        update.message.reply_text(
            f'Ура! На фото найден объект "{object}" {emoji}'
        )
        object_folder = f'learn_bot/images/{object}_imgs'
        os.makedirs(object_folder, exist_ok=True)
        new_filename = join(object_folder, f"{object}_{file_id}.jpeg")
        os.rename(filename, new_filename)
        update.message.reply_text(
            '📸 Мы сохранили фото для будущего использования 🎉 🥹 📸'
        )
    else:
        update.message.reply_text(
            f'К сожалению, мы не нашли объект {object} на фото. \
                Мы нашли только следующие объекты \
                (уверенность AI >= {confidence: .1%}):\
                 {", ".join(what_on_img)}'
        )
        os.remove(filename)


def subscribe_user_handler(update, context):
    user = get_or_create_user(
        mongo_db,  update.effective_user, update.message.chat.id
    )
    subscribe_user(mongo_db, user)
    update.message.reply_text('Вы успешно подписались! ⚓️')


def unsubscribe_user_handler(update, context):
    user = get_or_create_user(
        mongo_db,  update.effective_user, update.message.chat.id
    )
    unsubscribe_user(mongo_db, user)
    update.message.reply_text('Вы успешно отписались! 🫠')


def set_alarm(update, context):
    try:
        alarm_seconds = abs(int(context.args[0]))
        context.job_queue.run_once(
            vk_alram,
            alarm_seconds,
            context=update.message.chat.id
        )
        update.message.reply_text(
            f'Уведомление через {alarm_seconds} секунд ⏱.\
              {datetime.now().strftime("%H:%M:%S")}'
        )
    except (TypeError, ValueError):
        update.message.reply_text("Введите целое число секунд после команды.")


def flag_picture_rating(update, context):
    user = get_or_create_user(
        mongo_db,  update.effective_user, update.effective_chat.id
    )
    update.callback_query.answer()
    callback_type, image_name, vote = update.callback_query.data.split('|')
    vote = int(vote)
    save_flag_img_vote(mongo_db, user, image_name, vote)

    rating = get_flag_img_rating(mongo_db, image_name)
    text = f"Спасибо!🫦\nРейтинг картинки: {rating}"
    update.callback_query.edit_message_caption(caption=text)


if __name__ == '__main__':

    print('Helo Bot!')
