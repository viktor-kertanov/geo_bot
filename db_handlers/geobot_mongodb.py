from pymongo import MongoClient
from config import MONGO_GEO_BOT, MONGO_GEO_BOT_DB
from learn_bot.emoji_handler import random_emoji
from datetime import datetime

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
            "chat_id": chat_id,
            "emoji": random_emoji()
        }
        db.users.insert_one(user)

    return user
