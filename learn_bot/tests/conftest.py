import pytest


@pytest.fixture
def effective_user():
    class EffectiveUser:
        def __init__(
            self,
            id,
            first_name,
            last_name,
            username,
            chat_id,
            emoji
        ):

            self.id = id
            self.first_name = first_name
            self.last_name = last_name
            self.username = username
            self.chat_id = chat_id
            self.emoji = emoji
    
    return EffectiveUser(
        1670826999,
        'Viktor',
        'Kertanov',
        'viktor_kertanov',
        1670826999,
        '🔥'
    )
