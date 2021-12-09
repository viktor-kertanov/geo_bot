import requests
from bs4 import BeautifulSoup
from random import randint
from time import sleep
import os
from helpers.db_interface import country_title_get_db_row, write_image_to_db
import base64
from typing import Type, List
from fake_useragent import UserAgent


class WikiCountry:
    def __init__(self, country_html):
        self.country_html = country_html
        self.images_path = "country_images_svg/"

    @property
    def country_flag_svg(self):
        """
        Locating the url that has the picture of a country flag.
        """
        country_flag_url = self.country_html.select_one("span.flagicon a").get("href")
        country_flag = f"https://ru.wikipedia.org{country_flag_url}"
        country_flag_image = requests.get(country_flag).content
        flag_image_soup = BeautifulSoup(country_flag_image, "html.parser")
        country_full_image_url = flag_image_soup.select_one("div.fullImageLink a").get("href")
        country_full_image_url = f"https:{country_full_image_url}"
        return country_full_image_url

    def _wiki_max_res_img(self, html_list):
        """Returning the index with the highest resolution on wikipedia """
        res_list = []
        for item in html_list:
            res = int(item.text.split()[0])
            res_list.append(res)
        max_res = max(res_list)
        # print(f"Res_list:{res_list}")
        # print(f"Max res: {max_res}")
        return res_list.index(max_res)

    @property
    def country_flag(self):
        """
        Locating the url that has the picture of a country flag.
        """
        country_flag_url = self.country_html.select_one("span.flagicon a").get("href")
        country_flag = f"https://ru.wikipedia.org{country_flag_url}"
        country_flag_image = requests.get(country_flag).content
        flag_image_soup = BeautifulSoup(country_flag_image, "html.parser")
        country_images_url = flag_image_soup.select_one("span.mw-filepage-other-resolutions").find_all('a')
        max_res_index = self._wiki_max_res_img(country_images_url)
        country_full_image_url = country_images_url[max_res_index].get("href")
        country_full_image_url = f"https:{country_full_image_url}"
        return country_full_image_url

    @property
    def title_and_article_html(self):
        """AUX property method that locates the html containing title and article html"""
        return self.country_html.find_all("td")[2]

    @property
    def country_title(self):
        """
        Getting the ru title of a country + setting an attribute that has a first lower letter of the name
        """
        country_title = self.title_and_article_html.select_one("td a").text
        self.first_letter_ru = country_title[0].lower()
        return country_title

    @property
    def country_article_link(self):
        """
        Locating the url of a Wikipedia article about a given country, article in Russian language.
        """
        country_article_link = self.title_and_article_html.select_one("td a").get("href")
        country_article_link = f"https://ru.wikipedia.org{country_article_link}"
        return country_article_link

    @property
    def position_on_map_image_svg(self):
        """"
        Locating the url of an image that shows the position of a country on a map
        """
        position_page = requests.get(self.country_article_link).content
        position_soup = BeautifulSoup(position_page, "html.parser")
        image_page_url = position_soup.select_one("table.infobox tbody [data-wikidata-property-id='P242'] a").get("href")
        image_page_url = f"https://ru.wikipedia.org{image_page_url}"
        image_page = requests.get(image_page_url).content
        image_soup = BeautifulSoup(image_page, "html.parser")
        position_image = image_soup.select_one("div.fullImageLink a").get("href")
        position_image = f"https:{position_image}"
        return position_image

    @property
    def position_on_map_image(self):
        """"
        Locating the url of an image that shows the position of a country on a map
        """
        position_page = requests.get(self.country_article_link).content
        position_soup = BeautifulSoup(position_page, "html.parser")
        image_page_url = position_soup.select_one("table.infobox tbody [data-wikidata-property-id='P242'] a").get(
            "href")
        image_page_url = f"https://ru.wikipedia.org{image_page_url}"
        image_page = requests.get(image_page_url).content
        image_soup = BeautifulSoup(image_page, "html.parser")
        position_image_res = image_soup.select_one("span.mw-filepage-other-resolutions").find_all('a')
        max_res_index = self._wiki_max_res_img(position_image_res)
        position_image = position_image_res[max_res_index].get("href")
        position_image = f"https:{position_image}"
        return position_image

    @property
    def capital(self):
        """
        We get the capital of a country in Russian language
        """
        country_article = self.country_article_link
        country_content = requests.get(country_article).content
        country_soup = BeautifulSoup(country_content, "html.parser")
        capital = country_soup.select_one("tbody span[data-wikidata-property-id='P36'] a")
        no_capital = country_soup.select_one("tbody span.ts-comment-commentedText")
        hard_capital = country_soup.find_all("tbody div[data-wikidata-property-id='P36'] li")
        if capital:
            capital = capital.get("title")
        elif no_capital:
            capital = country_soup.select_one("tbody span.ts-comment-commentedText").get("title")
        else:
            capital = ', '.join([c.text() for c in hard_capital])
        return capital

    @property
    def country_eng_title(self):
        """
        We get the English title of a country
        """
        page = requests.get(self.country_article_link).content
        soup = BeautifulSoup(page, "html.parser")
        try:
            eng_title = soup.select_one("li.interlanguage-link a[lang='en']").get("title").split(" — ")[0]
            self.country_first_lttr_lower_en = eng_title[0].lower()
        except:
            eng_title = self.country_title
            self.country_first_lttr_lower_en = eng_title[0].lower()
        return eng_title

    @property
    def list_images_in_dir(self):
        """
        Method that returns list of files within the directory subscribed for storing additional materials like
        flag images, position images etc.
        """
        return os.listdir(self.images_path)

    @property
    def img_structure_for_dl(self):
        """
        key is the attribute of self which is a direct url link to an image or other type of file.
        values if the suffix for naming files of that type. we need this suffix in order to have
        more beautiful filenames.
        If we need too dl some other files, first we have to create an attribute for this class,
        then we have to add this attribute in the dictionary.
        """
        return {
            "country_flag": "flag",
            "position_on_map_image": "position"
        }


    def dl_img(self):
        """
        Method for downloading images from Wiki to the path that works for different object attributes.
        We'll have specific filenames for flag images, for position images. Also we check if the file already
        exists in the path for images of an object of this class.
        """
        images_attrs = ["country_flag", "position_on_map_image"]
        for dl_prefix in images_attrs:
            country_db_row = country_title_get_db_row(self.country_title)
            db_col_name = f"{dl_prefix}_bytes"
            headers = {"User-Agent": str(UserAgent().random)}
            img_url = self.__getattribute__(dl_prefix)
            country_eng_title = self.country_eng_title.lower().strip()
            img_type = img_url.split('.')[-1]
            filename_prefix = {
                "country_flag": "flag",
                "position_on_map_image": "position"
            }
            filename = f"{country_eng_title}_{filename_prefix[dl_prefix]}.{img_type}"
            if country_db_row[db_col_name]:
                print(f"{self.country_title} :: {dl_prefix} is already in the db.")
            else:
                image = requests.get(img_url, headers=headers).content
                if not "Wikimedia Error" in str(image):
                    write_image_to_db(self.country_title, db_col_name, image)
                    with open(f"helpers/country_images/{filename}", 'wb') as file:
                        file.write(image)
                        print(f"Success: {self.country_eng_title.replace(' ','__')} // {filename_prefix[dl_prefix]}")
                        sleep(randint(5, 7))
                else:
                    print(f"Could not download: {img_url}")
                    return None

    @property
    def db_tuple_insert(self):
        """INSERT INTO countries(
                country_title,
                country_eng_title,
                images_path,
                country_flag,
                country_article_link,
                position_on_map_image,
                capital)
                VALUES (?,?,?,?,?,?,?)"""

        return (self.country_title,
                self.country_eng_title,
                self.capital,
                self.country_flag,
                self.country_article_link,
                self.position_on_map_image,
                )


def countries_html() -> List:
    countries_url = "https://w.wiki/dWv"
    countries_db = requests.get(countries_url).content
    countries_soup = BeautifulSoup(countries_db, "html.parser")
    countries = [c for c in countries_soup.find_all("tr") if c.select_one("td span.flagicon")]
    return countries


if __name__ == '__main__':
    dl_images = [WikiCountry(c) for c in countries_html()[10:25]]
    for c in dl_images:
        print(c.position_on_map_image)

    print("Hello world!")