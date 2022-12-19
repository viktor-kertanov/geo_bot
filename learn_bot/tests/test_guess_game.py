from learn_bot.guess_game import get_bot_number


def test_get_bot_number():
    user_number = 10
    random_interval = 10
    assert (user_number - 10) <= get_bot_number(user_number, random_interval) <= (user_number + 8)

