from emoji import emojize
from telegram_geobot.emoji_handlers.flag_emojis import USER_EMOJI
from random import choice


def random_emoji():
    emoji_raw = choice(USER_EMOJI)
    emoji = emojize(emoji_raw, language='alias')

    return emoji


def emoji_by_string(my_string):
    emoji = emojize(f":{my_string.lower().strip()}:", language='alias')
    if emoji == f":{my_string}:":
        return ""
    return emoji


def user_emoji(user_data):
    if 'emoji' not in user_data:
        return random_emoji()

    return user_data['emoji']


if __name__ == '__main__':
    a = emoji_by_string('dog')
    print(a)
    print('Helo Bot!')
