'''Obtaining the info about country regions by continent, area etc.
Source: https://unstats.un.org/unsd/methodology/m49/

'''
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from telegram_geobot.utils.json_handler import save_data_as_json

REGION_SOURCE_URL = "https://unstats.un.org/unsd/methodology/m49/"

LANGUAGE_LOCATORS = {
    'english': 'GeoGroupsENG',
    'russian': 'GeoGroupsRUS',
    'french': 'GeoGroupsFRA',
    'spanish': 'GeoGroupsESP',
    'arabic': 'GeoGroupsARB',
    'chinese': 'GeoGroupsCHN'
}


def region_parser(language_locator: str) -> list[dict]:
    '''Function that obtains the info about regions in one language'''
    req = requests.get(REGION_SOURCE_URL)
    soup = BeautifulSoup(req.content, "html.parser")

    # there are a few tables in the source: 
    # 0) list of countries;
    # 1) geo regions (what we need)
    # 2) recent changes etc

    country_data = soup.select_one(f'table#{language_locator}')
    rows = country_data.select('tr')[1:]

    region_data = {}
    for el in rows:
        cells = el.select('td')
        numeric_id = cells[1].text
        alpha_3_id = cells[2].text.strip()
        parent_id = el.get('data-tt-parent-id')
        region_name = cells[0].text
        
        row = {
            "numeric_id": numeric_id,
            "region_name": region_name,
            "alpha3_id": alpha_3_id,
            "parent_numeric_id": parent_id
        }

        region_level = 1
        while alpha_3_id and parent_id and parent_id != '001':
            higher_region = region_data[parent_id]
            higher_region_name = higher_region["region_name"]
            row[f'region_{region_level}'] = higher_region_name
            
            parent_id = higher_region["parent_numeric_id"]
            region_level +=1
            


        region_data[numeric_id] = row
    

    return {
        country: region_data[country] for country in region_data 
        if region_data[country]["alpha3_id"]
    }


def all_language_region_data() -> dict:
    '''function that collects the info about region in different languages and stores the output as json'''
    
    all_lang_data = {}
    for lang in LANGUAGE_LOCATORS:
        lang_data = region_parser(LANGUAGE_LOCATORS[lang])
        all_lang_data[lang] = lang_data
    
    # saving region data in different languages as json object
    today = datetime.now().strftime("%y%m%d")
    output_filename = f'telegram_geobot/country_data/region_data/{today}_region_data.json'
    
    save_data_as_json(all_lang_data, output_filename)
    
    return all_lang_data


if __name__ == '__main__':
    all_region_data = all_language_region_data()
    print('hello world!')