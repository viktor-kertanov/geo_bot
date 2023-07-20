from random import choice, random, sample

from pymongo import MongoClient
from pymongo.database import Database

from telegram_geobot.config import settings as pydantic_settings
from telegram_geobot.country_data.iso_country_parser import iso_country_parser
from telegram_geobot.logs.log_config import logger

mongo_url = f"mongodb+srv://{pydantic_settings.mongo_db_user}:"
mongo_url += f"{pydantic_settings.mongo_db_password}"
mongo_url += "@cluster0.fdilskv.mongodb.net/geobot_telegram?retryWrites=true&w=majority"


mongo_db_client = MongoClient(mongo_url)
mongo_db = mongo_db_client[pydantic_settings.mongo_db_name]


def get_answer_options(db, regions_for_game: list[str], n_answer_options: int) -> list:
    """Function that pick n db elements to present them as options to the question.
    One of the options later becomes a question by simple random pick"""

    chance = random()
    if chance < 0.3:
        countries_sample = get_n_sample_from_db(
            db, n_answer_options, regions_for_game=regions_for_game
        )
    else:
        particular_region = choice(regions_for_game)
        countries_sample = get_n_sample_from_db(
            db, n_answer_options, regions_for_game=[particular_region]
        )

    len_countries = len(countries_sample)
    random_order = sample(range(len_countries), len_countries)

    countries_ordered_aux = zip(countries_sample, random_order)
    answer_options = [el[0] for el in sorted(countries_ordered_aux, key=lambda x: x[1])]
    answers_options_modified = ", ".join([el["country_name"] for el in answer_options])
    logger.info(f"Final answer options order: {answers_options_modified}")

    return answer_options


def get_or_create_user(db: Database, effective_user, chat_id):
    collection = db["users"]
    user = collection.find_one({"user_id": effective_user.id})
    if not user:
        user = {
            "user_id": effective_user.id,
            "first_name": effective_user.first_name,
            "last_name": effective_user.last_name,
            "username": effective_user.username,
            "chat_id": chat_id,
            "is_bot": effective_user.is_bot,
            "language_code": effective_user.language_code,
            "regions": {
                "Европа": True,
                "Азия": True,
                "Африка": True,
                "Америка": True,
                "Карибы": True,
                "Океания": True,
            },
        }

        collection.insert_one(user)

    if not user.get("language_code", None):
        user = {
            "chat_id": chat_id,
            "is_bot": effective_user.is_bot,
            "language_code": effective_user.language_code,
        }

        collection.update_one({"user_id": effective_user.id}, {"$set": user})

    return user


def create_or_update_iso_data(db: Database, update_db_rows=False):
    iso_data = iso_country_parser()
    for c_idx, country_row in enumerate(iso_data, start=1):
        name = country_row["country_name"]
        country = db.iso_country_data.find_one({"country_name": name})

        if not country:
            print(f"{c_idx}. We are inserting the data for {name}")
            db.iso_country_data.insert_one(country_row)
        elif update_db_rows:
            print(f"{c_idx}. We are updating data for {name}")
            db.iso_country_data.update_one(
                {"_id": country["_id"]}, {"$set": country_row}
            )
        else:
            print(f"{c_idx}. Skipping {name} as the info is already in db.")


def get_flag_emojis(db):
    """Getting all the emojis of flags in one query to play in Telegram bot"""
    all_flags_cur = db.iso_country_data.find({}, {"_id": 0, "emoji": True})

    return [el["emoji"] for el in all_flags_cur]


def get_n_sample_from_db(
    db: Database, n: int, regions_for_game: list[str] = None, language: str = "russian"
) -> list:
    country_data = db["iso_country_data"]
    if not regions_for_game:
        regions = get_region_names(db, language)
        regions_for_game = choice(list(regions))

    logger.info(f"Current region for a game is :{regions_for_game}")

    sample = country_data.aggregate(
        [
            {
                "$match": {
                    f"region_data.{language}.game_region": {"$in": regions_for_game}
                }
            },
            {"$sample": {"size": n}},
        ]
    )

    return [el for el in sample]


def get_region_names(db: Database, language="russian") -> dict:
    regions = db.iso_country_data.aggregate(
        [
            {"$match": {"mute": {"$eq": False}}},
            {"$match": {f"region_data.{language}.game_region": {"$exists": True}}},
            {"$group": {"_id": f"$region_data.{language}.game_region"}},
        ]
    )

    return {el["_id"] for el in regions}


def get_region_names_low_level(db: Database, language="russian") -> dict:
    regions = db.iso_country_data.aggregate(
        [
            {"$match": {f"region_data.{language}.region_1": {"$exists": True}}},
            {
                "$group": {
                    "_id": f"$region_data.{language}.region_1",
                    "game_region": {"$first": f"$region_data.{language}.game_region"},
                }
            },
            {"$sort": {"game_region": 1}},
        ]
    )

    return {el["_id"]: el["game_region"] for el in regions}


def update_game_region(mongo_db: Database):
    collection = mongo_db["iso_country_data"]
    query = {"region_data.russian.game_region": "Северная и Южная Америка"}
    update = {"$set": {"region_data.russian.game_region": "Америка"}}

    result = collection.update_many(query, update)

    logger.info(f"Modified {result.modified_count} documents.")

    update = {"$unset": {"game_region": 1}}
    result = collection.update_many({}, update)
    logger.info(f"Deleted the 'field_to_delete' from {result.modified_count}.")


def set_user_active_regions(mongo_db: Database):
    collection = mongo_db["users"]
    regions = {
        "Европа": True,
        "Азия": True,
        "Африка": True,
        "Америка": True,
        "Карибы": True,
        "Океания": True,
    }
    update = {"$set": {"active_regions": regions}}

    result = collection.update_many({}, update)

    logger.info(f"Modified {result.modified_count} documents.")


def create_mute(mongo_db: Database):
    collection = mongo_db["iso_country_data"]
    update = {"$set": {"mute": False}}
    collection.update_many({}, update)


def west_indies(mongo_db: Database):
    collection = mongo_db["iso_country_data"]
    query = {"region_data.russian.game_region": "Северная и Южная Америка"}
    update = {"$set": {"region_data.russian.game_region": "Америка"}}

    result = collection.update_many(query, update)

    logger.info(f"Modified {result.modified_count} documents.")


def caribbean(mongo_db: Database):
    collection = mongo_db["iso_country_data"]
    query = {"region_data.english.region_1": "Caribbean"}
    region_languages = ["english", "french", "spanish", "arabic", "chinese"]

    for language in region_languages:
        result = collection.update_many(
            query,
            [
                {
                    "$set": {
                        f"region_data.{language}.game_region": f"$region_data.{language}.region_1"
                    }
                }
            ],
        )
        logger.info(f"Modified {result.modified_count} documents for {language}")


if __name__ == "__main__":
    region_names = get_region_names(mongo_db, "russian")
    logger.info(region_names)
