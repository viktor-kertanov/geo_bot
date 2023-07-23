from unittest.mock import patch

from learn_bot.handlers import talk_to_me
from learn_bot.tests.conftest import call_handler, make_message


@patch("learn_bot.handlers.get_or_create_user", return_value={"emoji": ":heart_eyes:"})
def test_talk_to_me(updater, effective_user):
    message = make_message("Проверка бота!", effective_user, updater.bot)
    call_handler(updater, talk_to_me, message)
    assert message.reply_text.called
    args, kwargs = message.reply_text.call_args
    assert args[0] == "Проверка бота! :heart_eyes:"
    assert "reply_markup" in kwargs
