from config import logging
from emoji import emojize
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from config import API_TOKEN, USER_EMOJI
from random import randint, choice
import os
from os.path import isfile, join
from PIL import Image

def random_emoji():
    emoji_raw = choice(USER_EMOJI)
    emoji = emojize(emoji_raw, language='alias')

    return emoji

def user_emoji(user_data):
    if 'emoji' not in user_data:
        return random_emoji()

    return user_data['emoji']

def greet_user(update, context):
    print('Вызван /start, vk')
    print(f'Our user_data is: {context.user_data}')
    context.user_data['emoji'] = user_emoji(context.user_data)
    update.message.reply_text(f"Привет! {context.user_data['emoji']}")

def talk_to_me(update, context):
    text_to_repeat = update.message.text
    
    context.user_data['emoji'] = user_emoji(context.user_data)
    update.message.reply_text(f"{text_to_repeat}{context.user_data['emoji']}")

    internal_msg = f'We have just echoed: "{text_to_repeat}"'
    logging.info(internal_msg)
    print(internal_msg)
    return None

def guess_number(update, context):
    usr_msg = update.message.text
    print(f'user message is: {usr_msg}')

    try:
        usr_number = usr_msg.split(' ')[-1]
        usr_number = int(usr_number)
        print(f'user number is {usr_number}.')
    except (TypeError, ValueError) as e:
        error_msg = 'Вы не умеете играть в эту игру. Напишите "/guess n", где n - целое число.'
        print(error_msg)
        logging.info(f'Our error looks like this: {e}')
        update.message.reply_text(error_msg)
    
    guess = randint(usr_number-10, usr_number+11)
    print(f'Our guess is {guess}')
    
    if guess == usr_number:
        update.message.reply_text(f'Ничья! Мы оба загадали число {usr_number}🥹')
    elif guess < usr_number:
        update.message.reply_text(f'Ты выиграл, потому что ты загадал {usr_number}, а я загадал {guess} 🎉 🎊 ❤️')
    else:
        update.message.reply_text(f'К сожалению, ты проиграл: я загадал {guess}, а ты {usr_number} но я по-прежнему бездушный бот. А у тебя душа есть... 💔')

def convert_png_to_jpg():
    #converting png images to jpeg images, taking care of the alpha-layers and filling the transparency with white
    images_dir = "data/country_images/"
    images = [f'{images_dir}{f}' for f in os.listdir(images_dir) if isfile(join(images_dir, f)) and '.png' in f]
    new_file_ext = '.jpeg'
    for image in images:
        new_img_name = image.replace('.png', new_file_ext)
        if isfile(new_img_name):
            #if the image already exists we move to the next flag
            print(f"Moving to next image as we already have this one:: {new_img_name}")
            continue
        
        original_img = Image.open(image)
        if original_img.mode in ('RGB','P', 'L'):
            output_img = original_img.convert('RGB')
            output_img.save(new_img_name, format='JPEG', quality=95)
        else:
            original_img.load() # required for png.split()
            output_img = Image.new("RGB", original_img.size, (255, 255, 255))
            output_img.paste(original_img, mask=original_img.split()[3]) # 3 is the alpha channel
            output_img.save(new_img_name, format='JPEG', quality=95)
        
        print(f'Successfully created image:: {new_img_name}')

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
        

def main():
    echo_bot = Updater(API_TOKEN, use_context=True)
    
    #dispatcher & registering handlers
    dp = echo_bot.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(CommandHandler("guess", guess_number))
    dp.add_handler(CommandHandler("flag", send_flag_picture))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))
    logging.info('Бот стартовал')
    
    echo_bot.start_polling()
    echo_bot.idle()


if __name__ == '__main__':
    # convert_png_to_jpg()
    main()

    print('Hello world!')
