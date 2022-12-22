from telegram import (ReplyKeyboardMarkup, KeyboardButton,
                      InlineKeyboardButton, InlineKeyboardMarkup)

def flag_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                '🇵🇫', callback_data=1
            ),
            InlineKeyboardButton(
                '🇹🇻', callback_data=2
            )
        ],
        [
            InlineKeyboardButton(
                '🇫🇴', callback_data=3
            ),
            InlineKeyboardButton(
                '🇸🇽', callback_data=4
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)