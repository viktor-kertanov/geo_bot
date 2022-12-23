from pymongo import MongoClient
from config import MONGO_GEO_BOT, MONGO_GEO_BOT_DB
from learn_bot.emoji_handler import random_emoji
from datetime import datetime
from telegram_geobot.country_data.iso_country_parser import iso_country_parser
from emoji import emojize, is_emoji


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


def enrich_iso_db_with_emoji(db):
    '''Where possible, this function adds emoji to iso_data'''
    #querying all elements of iso_country_data, excepts those with emoji
    db_data = db.iso_country_data.find()
    
    #going countries one-by-one 
    for c_idx, country in enumerate(db_data, start=1):
        #obtaining necessary data from db
        name = country["country_name"]
        name_for_emoji = '_'.join(name.lower().split(' '))
        iso_alpha_2_code = country["iso_alpha_2_code"].lower()
        
        #trying to get emoji for a particular country
        emoji = emojize(f':{name_for_emoji}:', language='alias')
        if not is_emoji(emoji):
            emoji = emojize(f':{iso_alpha_2_code}:', language='alias')
        
        #updating iso_country_data with emoji, if we got one
        if is_emoji(emoji):
            print(f'{c_idx}. Adding emoji {emoji} for {name}.')
            db.iso_country_data.update_one(
                {'_id': country['_id']},
                {'$set': {"emoji": emoji}}
            )
        else:
            print(f'{c_idx}. Skpping emoji for {name}. Add manually.')
        
    return db_data


def add_emoji_manually(db):
    '''Find blank flag emojis in ISO country data db and paste manually through input.'''
    blank_emojis = db.iso_country_data.find({"emoji": None})
    for c_idx, country in enumerate(blank_emojis, start=1):
        name = country["country_name"]
        # getting user input
        manual_emoji = input(f'Please insert emoji for {name} below. {country["country_page_url"]}\n').strip()
        
        # inserting to db if emoji
        if is_emoji(manual_emoji):
            print(f'{c_idx}. Inserting emoji {manual_emoji} for {name}.')
            db.iso_country_data.update_one(
                {'_id': country['_id']},
                {'$set': {'emoji': manual_emoji}}
            )
        else:
            print(f'{c_idx}. What you have inserted - [{manual_emoji}] - is not emoji. Skipping {name}.')
    return blank_emojis

if __name__ == '__main__':
    # db_data = enrich_iso_db_with_emoji(mongo_db)
    add_emoji_manually(mongo_db)


    print('Hello World!')