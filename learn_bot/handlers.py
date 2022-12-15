from config import logging
from learn_bot.bot_keyboard import main_keyboard
from learn_bot.emoji_handler import user_emoji
from learn_bot.guess_game import guess_number_game
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

if __name__ == '__main__':

    print('Helo Bot!')