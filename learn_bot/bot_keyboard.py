from telegram import ReplyKeyboardMarkup, KeyboardButton


def main_keyboard():
    return ReplyKeyboardMarkup([['Прислать флаг', KeyboardButton('Мой координаты', request_location=True)]])

if __name__ == '__main__':

    print('Helo Bot!')