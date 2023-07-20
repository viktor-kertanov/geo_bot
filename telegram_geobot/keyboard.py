from random import choice

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegram_geobot.logs.log_config import logger


def game_keyboard(answer_options, question, game_name):
    keyboard = []
    answer_options_pretty = [
        f"✅  {el['emoji']}{el['region_data']['russian']['region_name']}"
        if el["numeric_code"] == question["numeric_code"]
        else f"⭕️  {el['emoji']}{el['region_data']['russian']['region_name']}"
        for el in answer_options
    ]
    answer_options_alpha_3 = [el["iso_alpha_3_code"] for el in answer_options]
    for c_idx, country in enumerate(answer_options, start=1):
        country_name = country["region_data"]["russian"]["region_name"]
        callback_data = {
            "answer_options_pretty": answer_options_pretty,
            "answer_options_alpha_3": answer_options_alpha_3,
            "correct_answer_name": question["region_data"]["russian"]["region_name"],
            "correct_answer_alpha_3": question["iso_alpha_3_code"],
            "user_answer_pretty": f"{country['emoji']}{country_name}",
            "user_answer_name": country_name,
            "user_answer_alpha_3": country["iso_alpha_3_code"],
            "user_win": (lambda x, y: True if x == y else False)(
                country["iso_alpha_3_code"], question["iso_alpha_3_code"]
            ),
            "button_index": c_idx,
            "game_name": game_name,
            "callback_name_id": "play_game_callback_id",
            "ru_wiki_article": question["ru_wiki_article"],
            "en_wiki_article": question["country_page_url"],
            "country_emoji": question["emoji"],
        }

        logger.info(
            f"Button # {c_idx}: {callback_data['user_answer_name']} :: {callback_data['user_answer_alpha_3']}"
        )
        button = InlineKeyboardButton(country_name, callback_data=callback_data)
        cur_row = [button]
        keyboard.append(cur_row)

    return InlineKeyboardMarkup(keyboard)


def region_settings_keyboard(user_active_regions):
    visualize_data = {
        True: "✅",
        False: "➖",
    }
    row_len = 2
    region_keyboard, cur_row = [], []
    for region, value in user_active_regions.items():
        visualize = visualize_data[value]
        callback_data = {
            "user_active_regions": user_active_regions,
            "button_pressed_data": region,
            "callback_name_id": "region_settings_callback_id",
        }
        button = InlineKeyboardButton(
            f"{visualize} {region}", callback_data=callback_data
        )
        if len(cur_row) < row_len:
            cur_row.append(button)
        if len(cur_row) == row_len:
            region_keyboard.append(cur_row)
            cur_row = []
    if cur_row:
        region_keyboard.append(cur_row)

    region_keyboard.append(
        [InlineKeyboardButton("🏁 Старт", callback_data="start_please")]
    )

    return InlineKeyboardMarkup(region_keyboard)


def menu_keyboard(
    country_name: str = None,
    wiki_url: str = None,
    start_button_exists: bool = True,
    only_start_button: bool = False,
):
    globe_emojis = ["🌎", "🌏", "🌍"]

    flag_alias = "🚩 Игра Флаги"
    position_alias = "🗺️ Игра Атлас"
    start_alias = "🏁 Старт"
    stats_alias = "📊 Статистика"
    regions_alias = f"{choice(globe_emojis)} Регионы игры"

    if only_start_button:
        game_keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(start_alias, callback_data="start_please")]]
        )
        return game_keyboard

    buttons_grid = [
        [
            InlineKeyboardButton(flag_alias, callback_data="flag_play_please"),
            InlineKeyboardButton(position_alias, callback_data="position_play_please"),
        ],
        [
            InlineKeyboardButton(regions_alias, callback_data="change_regions_please"),
            InlineKeyboardButton(stats_alias, callback_data="stats_please"),
        ],
    ]
    if start_button_exists:
        buttons_grid.insert(
            1, [InlineKeyboardButton(start_alias, callback_data="start_please")]
        )
    if country_name and wiki_url:
        buttons_grid[1].insert(
            1, InlineKeyboardButton(f"{country_name} Википедия", url=wiki_url)
        )

    game_keyboard = InlineKeyboardMarkup(buttons_grid)

    return game_keyboard


if __name__ == "__main__":
    a = region_settings_keyboard()
