'''There are functions in this module that were used for one-time enrichment of the db. This is closely connected with parsing data from Wiki
also this may be handy in future if there's a need for occasional update of the data.
'''
import json
from telegram_geobot.country_data.wiki_data import WikiCountry
from emoji import emojize, is_emoji
import requests
from bs4 import BeautifulSoup
from telegram_geobot.utils.download_images import dl_img
from glob import glob
from telegram_geobot.db_handlers.geobot_mongodb import mongo_db

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


def download_position_images(db):
    DL_FOLDER = "telegram_geobot/country_data/images/positions/"
    already_have = glob(f"{DL_FOLDER}*.png")
    alpha_3_already_have = [el.split('/')[-1].split('_')[0] for el in already_have]
    
    countries = db.iso_country_data.find({"iso_alpha_3_code": {"$nin": alpha_3_already_have}})
    
    for country in countries:
        alpha_3 = country['iso_alpha_3_code']
        country_name = '_'.join(country['country_name'].split(' '))
        numeric = country['numeric_code']
        alpha_2 = country['iso_alpha_2_code']
        download_url = country['country_position_url']
        extension = download_url.split('.')[-1]
        filename = f"{DL_FOLDER}{alpha_3}_{numeric}_{alpha_2}_{country_name}_[position].{extension}"
        dl_img(download_url, filename)

    return None


def enrich_with_game_region(db):
    collection = db['iso_country_data']
    # countries = collection.find({"region_data.russian.region_3": {"$exists": False}, "region_data.russian.game_region": {"$exists": False}})
    countries = collection.find({"region_data.russian.game_region": {"$exists": True}})
    region_languages = ["russian", "english", "french", "spanish", "arabic", "chinese"]
    region_languages = ["russian"]
    for c_idx, country in enumerate(countries, start=1):
        if country["country_name"] == "Antarctica" or country["country_name"] == "Taiwan, Province of China":
            continue
        try:
            game_region = country["region_data"]["english"]["region_3"]
            region_3_exists = True
        except KeyError:
            region_3_exists = False

        for lang in region_languages:
            aux_region = country["region_data"][lang]
            collection.update_one(
                        {'_id': country['_id']},
                        {
                            '$set': {
                                f"region_data.{lang}.game_region":
                                    (lambda x: aux_region["region_3"] if x else aux_region["region_2"])\
                                    (region_3_exists)
                            }
                        }
                    )
    

if __name__ == '__main__':
    enrich_with_game_region(mongo_db)
    print('Hello world!')
