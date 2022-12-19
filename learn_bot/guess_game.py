from random import randint


def get_bot_number(user_number: int, random_interval: int = 10) -> int:
    return randint(user_number-random_interval, user_number+random_interval+1)


def guess_number_game(user_number: int, bot_number: int) -> str:
    if bot_number == user_number:
        message = f'Ничья! Мы оба загадали число {user_number}🥹'
    elif bot_number < user_number:
        message = f'''Ты выиграл, потому что ты загадал\
 {user_number}, а я загадал {bot_number} 🎉 🎊 ❤️'''
    else:
        message = f'''К сожалению, ты проиграл: я загадал {bot_number},\
 а ты {user_number} но я по-прежнему бездушный бот.\
 А у тебя душа есть... 💔'''

    return message
