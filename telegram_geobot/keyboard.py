from telegram import (ReplyKeyboardMarkup, KeyboardButton,
                      InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.parsemode import ParseMode


def flag_keyboard(answer_options, correct_answer, buttons_in_row=1):
    keyboard = []
    for c_idx, country in enumerate(answer_options, start=1):
        country_name = country["region_data"]["russian"]["region_name"]
        button = InlineKeyboardButton(country_name, callback_data=country['numeric_code'])
        cur_row = [button]
        keyboard.append(cur_row)

    
    return InlineKeyboardMarkup(keyboard)


def flag_keyboard_main(answer_options, buttons_in_row=1):
    '''Aux keyboard in case I don't like inline buttons'''
    keyboard = []
    for c_idx, country in enumerate(answer_options, start=1):
        country_name = country["country_name"]
        button = KeyboardButton(country_name, callback_data=c_idx)
        cur_row = [button]
        keyboard.append(cur_row)

    
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)


def positions_keyboard(answer_options, buttons_in_row=1):
    keyboard = []
    for c_idx, country in enumerate(answer_options, start=1):
        country_name = country["region_data"]["russian"]["region_name"]
        emoji = country["emoji"]
        button = InlineKeyboardButton(f"{emoji} {country_name}", callback_data=country['numeric_code'])
        cur_row = [button]
        keyboard.append(cur_row)

    
    return InlineKeyboardMarkup(keyboard)