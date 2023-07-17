from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton)
from telegram_geobot.db_handlers.geobot_mongodb import get_region_names, get_region_names_low_level, mongo_db
import numpy as np
from telegram import Update
from telegram.ext import CallbackContext
from telegram_geobot.logs.log_config import logger

def game_keyboard(answer_options, question, game_name):
    keyboard = []
    answer_options_pretty = [
            f"✅  {el['emoji']}{el['region_data']['russian']['region_name']}"
            if el['numeric_code'] == question['numeric_code']
            else f"⭕️  {el['emoji']}{el['region_data']['russian']['region_name']}"
            for el in answer_options
            ]
    answer_options_alpha_3 = [
            el['iso_alpha_3_code'] for el in answer_options
        ]
    for c_idx, country in enumerate(answer_options, start=1):
        country_name = country["region_data"]["russian"]["region_name"]
        callback_data = {
        "answer_options_pretty": answer_options_pretty,
        "answer_options_alpha_3": answer_options_alpha_3,
        "correct_answer_name": question['region_data']['russian']['region_name'],
        "correct_answer_alpha_3": question['iso_alpha_3_code'],
        "user_answer_pretty": f"{country['emoji']}{country_name}",
        "user_answer_name": country_name,
        "user_answer_alpha_3": country['iso_alpha_3_code'],
        "user_win": (lambda x, y: True if x == y else False)(country['iso_alpha_3_code'], question['iso_alpha_3_code']),
        "button_index": c_idx,
        "game_name": game_name
        }

        logger.info(f"Button # {c_idx}: {callback_data['user_answer_name']} :: {callback_data['user_answer_alpha_3']}")
        button = InlineKeyboardButton(country_name, callback_data=callback_data)
        cur_row = [button]
        keyboard.append(cur_row)
    
    return InlineKeyboardMarkup(keyboard)

def region_settings_keyboard(user_active_regions):
    visualize_data = {
        True: '✅',
        False: '➖',
    }
    row_len = 2
    region_keyboard, cur_row = [], []
    max_region_character_len = max([len(el) for el in user_active_regions])
    for region, value in user_active_regions.items():
        visualize = visualize_data[value]
        align_spaces = chr(0x00A0)
        callback_data = {'user_active_regions': user_active_regions, 'button_pressed_data': region}
        button = InlineKeyboardButton(f'{visualize} {region}', callback_data=callback_data)
        if len(cur_row) < row_len:
            cur_row.append(button)
        if len(cur_row) == row_len:
            region_keyboard.append(cur_row)
            cur_row =[]
    if cur_row:
        region_keyboard.append(cur_row)
    
    return InlineKeyboardMarkup(region_keyboard)


if __name__ == '__main__':
    a = region_settings_keyboard()
    print('Hello world!')