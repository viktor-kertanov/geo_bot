from telegram import (ReplyKeyboardMarkup, KeyboardButton,
                      InlineKeyboardButton, InlineKeyboardMarkup)
import json


def flag_keyboard(answer_options, question):
    keyboard = []
    answer_options_pretty = [
            f"✅  {el['emoji']}{el['region_data']['russian']['region_name']}"
            if el['numeric_code'] == question['numeric_code']
            else f"❌  {el['emoji']}{el['region_data']['russian']['region_name']}"
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
        "button_index": c_idx
        }

        print(f"Button # {c_idx}: {callback_data['user_answer_name']} :: {callback_data['user_answer_alpha_3']}")
        button = InlineKeyboardButton(country_name, callback_data=callback_data)
        cur_row = [button]
        keyboard.append(cur_row)

    
    return InlineKeyboardMarkup(keyboard)


def position_keyboard(answer_options, question):
    keyboard = []
    answer_options_pretty = [
            f"✅  {el['emoji']}{el['region_data']['russian']['region_name']}"
            if el['numeric_code'] == question['numeric_code']
            else f"❌  {el['emoji']}{el['region_data']['russian']['region_name']}"
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
        "button_index": c_idx
        }

        print(f"Button # {c_idx}: {callback_data['user_answer_name']} :: {callback_data['user_answer_alpha_3']}")
        button = InlineKeyboardButton(f"{country['emoji']}{country_name}", callback_data=callback_data)
        cur_row = [button]
        keyboard.append(cur_row)

    
    return InlineKeyboardMarkup(keyboard)