from config import logging
from learn_bot.bot_keyboard import main_keyboard
from learn_bot.emoji_handler import user_emoji, emoji_by_string
from learn_bot.guess_game import guess_number_game
from learn_bot.clarifai_handler import object_exists_on_img, clarifai_processor, what_is_on_picture
import os
from os.path import isfile, join
from random import randint, choice

def greet_user(update, context):
    print('Вызван /start, vk')
    
    context.user_data['emoji'] = user_emoji(context.user_data)
    update.message.reply_text(
        f"Привет! {context.user_data['emoji']}",
        reply_markup=main_keyboard()
        )

def guess_number_handler(update, context):
    usr_msg = update.message.text
    print(f'user message is: {usr_msg}')

    try:
        user_number = usr_msg.split(' ')[-1]
        user_number = int(user_number)
        print(f'user number is {user_number}.')
        update.message.reply_text(guess_number_game(user_number))

    except (TypeError, ValueError) as e:
        error_msg = 'Вы не умеете играть в эту игру. Напишите "/guess n", где n - целое число.'
        print(error_msg)
        logging.info(f'Our error looks like this: {e}')
        update.message.reply_text(error_msg)

def send_flag_picture(update, context):
    flags_dir = "data/country_images/"
    flags = [
        f'{flags_dir}{f}' for f in os.listdir(flags_dir) 
        if isfile(join(flags_dir, f)) 
            and 'flag' in f 
            and '.jpeg' in f
    ]
    flag_to_send = choice(flags)
    country = flag_to_send.split('/')[-1].split('_')[0].capitalize()
    
    usr_chat_id = update.effective_chat.id
    context.bot.send_photo(chat_id=usr_chat_id, caption=country, photo=open(flag_to_send, 'rb'))

    return flags

def talk_to_me(update, context):
    text_to_repeat = update.message.text

    context.user_data['emoji'] = user_emoji(context.user_data)
    update.message.reply_text(
        f"{text_to_repeat}{context.user_data['emoji']}",
        reply_markup=main_keyboard())

    internal_msg = f'We have just echoed: "{text_to_repeat}"'
    logging.info(internal_msg)
    print(internal_msg)
    return None

def user_coordinates(update, context):
    context.user_data['emoji'] = user_emoji(context.user_data)
    coords = update.message.location
    update.message.reply_text(f"Ваши координаты:\n{coords} {context.user_data['emoji']}")
    print(coords)

def check_user_photo(update, context, default_object='cat'):
    confidence = 0.9
    caption = update.message.caption.strip().lower().split()[0]
    if caption:
        object = caption
    else:
        object=default_object

    context.user_data['emoji'] = user_emoji(context.user_data)
    update.message.reply_text('Обрабатываем фото 🌈')
    os.makedirs('learn_bot/downloads', exist_ok=True )
    print(update.message.photo[-1])
    file_id = update.message.photo[-1].file_id
    photo_file = context.bot.getFile(file_id)
    filename = join('learn_bot/downloads', f'{file_id}.jpeg')
    photo_file.download(filename)
    
    ai_response = clarifai_processor(filename)
    what_on_img = what_is_on_picture(ai_response, min_confidence=confidence)
    what_on_img = [el.name for el in what_on_img]
    object_exists = object_exists_on_img(ai_response, object, min_confidence=confidence)
    
    if object_exists:
        emoji = emoji_by_string(object)
        update.message.reply_text(f'Ура! На фото найден объект "{object}" {emoji}')
        object_folder = f'learn_bot/images/{object}_imgs'
        os.makedirs(object_folder, exist_ok=True)
        new_filename = join(object_folder, f"{object}_{file_id}.jpeg")
        os.rename(filename, new_filename)
        update.message.reply_text(f'📸 Мы сохранили фото для будущего использования 🎉 🥹 📸')
    else:
        update.message.reply_text(
            f'К сожалению, мы не нашли объект {object} на фото. \
                Мы нашли только следующие объекты (уверенность AI >= {confidence: .1%}): {", ".join(what_on_img)}'
        )
        os.remove(filename)


if __name__ == '__main__':

    print('Helo Bot!')