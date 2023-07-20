def region_callback_verifier(cb_data: dict[str]):
    try:
        if cb_data.get("callback_name_id", None) == "region_settings_callback_id":
            return True
    except AttributeError:
        return False


def game_callback_verifier(cb_data: dict[str]):
    try:
        if cb_data.get("callback_name_id", None) == "play_game_callback_id":
            return True
    except AttributeError:
        return False
