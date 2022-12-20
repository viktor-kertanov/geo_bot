from datetime import datetime
from unittest.mock import Mock

import pytest
from telegram import Bot, Chat,  Message, Update, User
from telegram.ext import Updater
from telegram.ext.callbackcontext import CallbackContext


@pytest.fixture
def effective_user():
    return User(
        id=1670826999,
        first_name='Viktor',
        last_name='Kertanov',
        username='viktor_kertanov',
        is_bot=False
    )


@pytest.fixture
def updater():
    bot = Bot(token='123')
    return Updater(bot=bot, use_context=True)


def make_message(text, user, bot):
    message = Message(
        message_id=1,
        from_user=user,
        date=datetime.now(),
        chat=Chat(id=1, type='private'),
        text=text,
        bot=bot
    )

    message.reply_text = Mock(return_value=None)

    return message


def call_handler(updater, handler, message):
    update = Update(update_id=1, message=message)
    context = CallbackContext.from_update(update,  updater.dispatcher)

    return handler(update, context)


# below is the way to create our own fixture/clas
# @pytest.fixture
# def effective_user():
#     class EffectiveUser:
#         def __init__(
#             self,
#             id,
#             first_name,
#             last_name,
#             username,
#             chat_id,
#             emoji
#         ):

#             self.id = id
#             self.first_name = first_name
#             self.last_name = last_name
#             self.username = username
#             self.chat_id = chat_id
#             self.emoji = emoji

#     return EffectiveUser(
#         1670826999,
#         'Viktor',
#         'Kertanov',
#         'viktor_kertanov',
#         1670826999,
#         '🔥'
#     )
