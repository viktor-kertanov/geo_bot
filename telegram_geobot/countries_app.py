from helpers.countries import countries_html, WikiCountry
from helpers.db_interface import add_country, create_countries_tb, select_db_country_titles
from random import randint
from time import sleep

create_countries_tb()
existing_in_db = select_db_country_titles()

for i, country_html in enumerate(countries_html()):
    country = WikiCountry(country_html)
    country_title = country.country_title
    print(f"{i+1}. {country_title}")
    if country_title in existing_in_db:
        print(f"We already have {country_title}")
        continue
    else:
        insert_tuple = country.db_tuple_insert
        add_country(insert_tuple)
        country.dl_img()
        sleep(randint(1,3))


