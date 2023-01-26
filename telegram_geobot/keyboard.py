from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton)
from telegram_geobot.db_handlers.geobot_mongodb import get_region_names, get_region_names_low_level, mongo_db
import numpy as np

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

        print(f"Button # {c_idx}: {callback_data['user_answer_name']} :: {callback_data['user_answer_alpha_3']}")
        button = InlineKeyboardButton(country_name, callback_data=callback_data)
        cur_row = [button]
        keyboard.append(cur_row)

    
    return InlineKeyboardMarkup(keyboard)

def region_settings_keyboard():
    regions = [el for el in get_region_names_low_level(mongo_db)]
    num_cols = 3
    num_rows = int(np.ceil(len(regions) / num_cols))
    region_keyboard, cur_row = [], []
    for r_idx, region in enumerate(regions):
        if r_idx % num_cols == 0:
            cur_row = []
            cur_row.append(region)
        else:
            cur_row.append(region)
        if len(cur_row) == num_cols or r_idx+1 ==len(regions):
            region_keyboard.append(cur_row)
    
    return region_keyboard


if __name__ == '__main__':
    a = region_settings_keyboard()
    print('Hello world!')