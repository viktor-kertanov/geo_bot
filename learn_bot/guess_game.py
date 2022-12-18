from random import randint


def guess_number_game(user_number: int) -> str:
    guess = randint(user_number-10, user_number+11)

    print(f'Our guess is {guess}')

    if guess == user_number:
        message = f'Ничья! Мы оба загадали число {user_number}🥹'
    elif guess < user_number:
        message = f'''Ты выиграл, потому что ты загадал
         {user_number}, а я загадал {guess} 🎉 🎊 ❤️'''
    else:
        message = f'''К сожалению, ты проиграл: я загадал {guess},
         а ты {user_number} но я по-прежнему бездушный бот.\
         А у тебя душа есть... 💔'''

    return message
