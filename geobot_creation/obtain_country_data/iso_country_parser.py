"""The goal of this module is to parse the data of country abbrevations:
"ru" for Russia, "tr" for Turkey
for this goal we'll need the data, taken from Wikipedia:
    https://en.wikipedia.org/wiki/ISO_3166-1;
    https://ru.wikipedia.org/wiki/ISO_3166-1;
There's an interesting extension to this data:
    https://ru.wikipedia.org/wiki/ISO_3166-2"
"""
import requests
from bs4 import BeautifulSoup

COUNTRY_DATA_URL = "https://en.wikipedia.org/wiki/ISO_3166-1"
WIKI_DOMAIN = "https://en.wikipedia.org"


def iso_country_parser():
    req = requests.get(COUNTRY_DATA_URL)
    soup = BeautifulSoup(req.content, features="html.parser")
    country_table = soup.select(".wikitable")[
        1
    ]  # there are a few tables on the page, we pick the second table
    rows = country_table.select("tr")
    country_data = rows[1:]

    iso_data = []
    for country in country_data:
        cd = country.select("td")

        country_row = {
            "country_name": cd[0].text.split("[")[0].strip(),
            "country_page_url": f'{WIKI_DOMAIN}{cd[0].select_one("a").get("href")}',
            "iso_alpha_2_code": cd[1].text,
            "iso_alpha_3_code": cd[2].text,
            "numeric_code": cd[3].text,
            "iso_3166_2_url": f'{WIKI_DOMAIN}{cd[4].select_one("a").get("href")}',
            "independency": cd[5].text.strip(),
        }

        iso_data.append(country_row)

    return iso_data


if __name__ == "__main__":
    a = iso_country_parser()
    print("Hello world!")
