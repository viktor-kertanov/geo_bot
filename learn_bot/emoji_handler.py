from emoji import emojize
from config import USER_EMOJI
from random import choice

def random_emoji():
    emoji_raw = choice(USER_EMOJI)
    emoji = emojize(emoji_raw, language='alias')

    return emoji

def user_emoji(user_data):
    if 'emoji' not in user_data:
        return random_emoji()

    return user_data['emoji']


if __name__ == '__main__':

    print('Helo Bot!')