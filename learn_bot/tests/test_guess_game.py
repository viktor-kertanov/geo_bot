from learn_bot.guess_game import get_bot_number, guess_number_game


def test_get_bot_number():
    user_number = 10
    random_interval = 10
    assert (user_number - 10) <=\
           get_bot_number(user_number, random_interval)\
           <= (user_number + 10)


def test_guess_number_win():
    user_number = 10
    bot_number = 5
    msg = '''Ты выиграл, потому что ты загадал\
 10, а я загадал 5 🎉 🎊 ❤️'''
    assert msg == guess_number_game(user_number, bot_number)


def test_guess_number_lose():
    user_number = 10
    bot_number = 19
    msg = '''К сожалению, ты проиграл: я загадал 19,\
 а ты 10 но я по-прежнему бездушный бот.\
 А у тебя душа есть... 💔'''
    assert msg == guess_number_game(user_number, bot_number)


def test_guess_number_draw():
    user_number = 10
    bot_number = 10
    msg = 'Ничья! Мы оба загадали число 10🥹'
    assert msg == guess_number_game(user_number, bot_number)
 