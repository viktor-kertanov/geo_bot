import json
from pymongo import MongoClient
from config import MONGO_GEO_BOT, MONGO_GEO_BOT_DB
from learn_bot.emoji_handler import random_emoji
from telegram_geobot.country_data.iso_country_parser import iso_country_parser
from telegram_geobot.country_data.wiki_data import WikiCountry
from emoji import emojize, is_emoji
import requests
from bs4 import BeautifulSoup

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


def enrich_with_region_data(db, region_data_filename, update_region_data=False):
    '''Obtaining the region data in different languages and adding that to the db
    update_region_data: bool if True than the data is overwritten in mongo db. If False -- we skip
    '''

    # getting the full list of iso_alpha_3_country codes 
    all_countries = db.iso_country_data.find()

    # getting all the region_data
    with open(region_data_filename, 'r', encoding='UTF-8') as f:
        region_data_raw = f.read()
        region_data = json.loads(region_data_raw)

    for c_idx, country in enumerate(all_countries, start=1):
        country_name = country['country_name']
        numeric_code = country['numeric_code']
        
        # working-through each language and creating dict with all languages by country
        country_regions_dict = {}
        for lang in region_data:
            # new field for a country is only created for the first language, than the data should be "pushed"
            try:
                data_row = region_data[lang][numeric_code]
            except KeyError:
                print('We have encountered the problem')
                print(f'No data in the source about {country_name} :: {numeric_code}. Lang: {lang}')
                continue

            # optimising data row -- not taking excessive field into db. We already have them via other sources
            del data_row["numeric_id"]
            del data_row["parent_numeric_id"]
            del data_row["alpha3_id"]
            country_regions_dict[lang] = data_row
            
        
        
        if 'region_data' not in country or update_region_data:
            print(f'{c_idx}. {country_name} :: {numeric_code}')
            db.iso_country_data.update_one(
                {'_id': country['_id']},
                {
                    '$set': {'region_data': country_regions_dict}
                }
            )

def get_flag_emojis(db):
    '''Getting all the emojis of flags in one query to play in Telegram bot'''
    all_flags_cur = db.iso_country_data.find({},{"_id": 0, "emoji": True})
    
    return [el["emoji"] for el in all_flags_cur]


def enrich_db_with_flag_position_url(db):
    countries = db.iso_country_data.find(
        {"$or": [
            {"country_flag_url": None},
            {"country_position_url": None}
        ]}
    )
    for c_idx, country in enumerate(countries, start=1):
        wiki_article = country["country_page_url"]
        wiki_country = WikiCountry(wiki_article)
        flag_img = wiki_country.country_flag
        position_img = wiki_country.position_on_map_image
        if flag_img:
            db.iso_country_data.update_one(
                {'_id': country['_id']},
                {
                    '$set': {'country_flag_url': flag_img}
                }
            )
            print(f'{c_idx}. {country["country_name"]}:: successfully added flag: {flag_img}')
        else:
            print(f'{c_idx}. {country["country_name"]}:: SKIP flag')
        if position_img:
            db.iso_country_data.update_one(
                {'_id': country['_id']},
                {
                    '$set': {'country_position_url': position_img}
                }
            )
            print(f'{c_idx}. {country["country_name"]}:: successfully added position: {position_img}')
        else:
            print(f'{c_idx}. {country["country_name"]}:: SKIP position')


def enrich_with_ru_wiki_article(db):
    countries = db.iso_country_data.find({"ru_wiki_article": ""})
    for c_idx, country in enumerate(countries, start=1):
        eng_article = country["country_page_url"]
        req = requests.get(eng_article)
        soup = BeautifulSoup(req.content, "html.parser")
        ru_wiki_article = soup.select_one("li.interlanguage-link.interwiki-ru a").get("href", None)
        if ru_wiki_article:
            db.iso_country_data.update_one(
                {'_id': country['_id']},
                {
                    '$set': {"ru_wiki_article": ru_wiki_article}
                }
            )
        else:
            print(f'{c_idx}. No wiki article for {country["country_name"]}.')

def enrich_with_ru_capital(db):
    countries = db.iso_country_data.find({"capital.russian": {"$exists": False}})
    for c_idx, country in enumerate(countries, start=1):
        capital_data_row = {"capital_name": "", "capital_wiki_article_url": ""}
        db.iso_country_data.update_one(
                    {'_id': country['_id']},
                    {
                        '$set': {
                            "capital.russian": capital_data_row
                        }
                    }
                )
        ru_article = country["ru_wiki_article"]
        req = requests.get(ru_article)
        soup = BeautifulSoup(req.content, "html.parser")
        info_data = soup.select("table.infobox tr")
        for data_el in info_data:
            try:
                data_row = data_el.select_one("th a").get("title", None)
            except:
                data_row = None
            if data_row == "Столица":
                capital_data = data_el.select_one("td span a")
                if not capital_data:
                    continue
                capital_url = f'https://ru.wikipedia.org{capital_data.get("href")}'
                capital_ru = capital_data.get("title")
                capital_data_row = {"capital_name": capital_ru, "capital_wiki_article_url": capital_url}
                db.iso_country_data.update_one(
                    {'_id': country['_id']},
                    {
                        '$set': {
                            "capital.russian": capital_data_row
                        }
                    }
                )
                continue


def enrich_with_eng_capital(db):
    countries = db.iso_country_data.find({"capital.english": {"$exists": False}})
    for c_idx, country in enumerate(countries, start=1):
        capital_data_row = {"capital_name": "", "capital_wiki_article_url": ""}
        db.iso_country_data.update_one(
                    {'_id': country['_id']},
                    {
                        '$set': {
                            "capital.english": capital_data_row
                        }
                    }
                )
        article = country["country_page_url"]
        req = requests.get(article)
        soup = BeautifulSoup(req.content, "html.parser")
        info_data = soup.select("table.infobox tr")
        for data_el in info_data:
            try:
                data_row = data_el.select_one("th.infobox-label").text.lower()
            except AttributeError:
                data_row = None
            if data_row and "capital" in data_row:
                capital_data = data_el.select_one("td a")
                capital_url = f'https://en.wikipedia.org{capital_data.get("href")}'
                capital_eng = capital_data.get("title")
                capital_data_row = {"capital_name": capital_eng, "capital_wiki_article_url": capital_url}
                print(f'{c_idx}. Updating {country["country_name"]} with english capital data: {capital_eng} :: {capital_url}.')
                db.iso_country_data.update_one(
                    {'_id': country['_id']},
                    {
                        '$set': {
                            "capital.english": capital_data_row
                        }
                    }
                )
                continue

if __name__ == '__main__':
    
    print('Hello World!')