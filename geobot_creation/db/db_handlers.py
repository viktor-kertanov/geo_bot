from pymongo import MongoClient
from pymongo.database import Database

from geobot_creation.obtain_country_data.iso_country_parser import (
    iso_country_parser,
)
from telegram_geobot.logs.log_config import logger
from telegram_geobot.config import settings as pydantic_settings

mongo_url = f"mongodb+srv://{pydantic_settings.mongo_db_user}:"
mongo_url += f"{pydantic_settings.mongo_db_password}"
mongo_url += "@cluster0.fdilskv.mongodb.net/geobot_telegram?retryWrites=true&w=majority"


mongo_db_client = MongoClient(mongo_url)
mongo_db = mongo_db_client[pydantic_settings.mongo_db_name]


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


def enrich_with_fields(mongo_db: Database):
    collection = mongo_db['users']
    users_without_is_admin = collection.find({"is_bot": {"$exists": False}})

    for user in users_without_is_admin:
        collection.update_one({"_id": user["_id"]}, {"$set": {"is_bot": False}})


if __name__ == '__main__':
    logger.info('Hello world!')
