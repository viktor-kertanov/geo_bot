from telegram import (ReplyKeyboardMarkup, KeyboardButton,
                      InlineKeyboardButton, InlineKeyboardMarkup)


def main_keyboard():
    return ReplyKeyboardMarkup(
        [
            ['Прислать флаг', KeyboardButton(
                'Мой координаты', request_location=True), 'Заполнить анкету']
        ]
    )


def img_rating_inline_keyboard(image_name):
    callback_text = f"rating|{image_name}|"
    keyboard = [
        [
            InlineKeyboardButton(
                '🌊Нравтися🔥', callback_data=callback_text + '1'
            ),
            InlineKeyboardButton(
                '⛔️Не нравтися👎🏻', callback_data=callback_text + '-1'
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


if __name__ == '__main__':

    print('Helo Bot!')
