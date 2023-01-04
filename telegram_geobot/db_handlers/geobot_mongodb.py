from pymongo import MongoClient
from config import MONGO_GEO_BOT, MONGO_GEO_BOT_DB
# from learn_bot.emoji_handler import random_emoji
from telegram_geobot.country_data.iso_country_parser import iso_country_parser


mongo_db_client = MongoClient(MONGO_GEO_BOT)
mongo_db = mongo_db_client[MONGO_GEO_BOT_DB]


def get_or_create_user(db, effective_user, chat_id):
    user = db.users.find_one({"user_id": effective_user.id})

    if not user:
        user = {
            "user_id": effective_user.id,
            "first_name": effective_user.first_name,
            "last_name": effective_user.last_name,
            "username": effective_user.username,
            "chat_id": chat_id
        }
        db.users.insert_one(user)

    return user


def create_or_update_iso_data(db, update_db_rows=False):
    iso_data = iso_country_parser()
    for c_idx, country_row in enumerate(iso_data, start=1):
        name = country_row["country_name"]
        country = db.iso_country_data.find_one({"country_name": name})

        if not country:
            print(f'{c_idx}. We are inserting the data for {name}')
            db.iso_country_data.insert_one(country_row)
        elif update_db_rows:
            print(f'{c_idx}. We are updating data for {name}')
            db.iso_country_data.update_one(
                {'_id': country['_id']},
                {'$set': country_row}
            )
        else:
            print(f'{c_idx}. Skipping {name} as the info is already in db.')


def get_flag_emojis(db):
    '''Getting all the emojis of flags in one query to play in Telegram bot'''
    all_flags_cur = db.iso_country_data.find({},{"_id": 0, "emoji": True})
    
    return [el["emoji"] for el in all_flags_cur]


def get_n_sample_from_db(db, n: int) -> list:
    sample = db.iso_country_data.aggregate([{"$sample": {"size": n}}])
    return [el for el in sample]

def get_region_names(db, language='russian', region_level=2) -> dict:
    regions = db.iso_country_data.aggregate([
        {"$match":{f"region_data.{language}.region_{region_level}": {"$exists": True}}},
        {"$group": {"_id": f"$region_data.{language}.region_{region_level}"}}

    ])

    return [el['_id'] for el in regions]

if __name__ == '__main__':
    a = get_region_names(mongo_db)
    print('Hello World!')
