import requests
from bs4 import BeautifulSoup
from random import randint
from time import sleep
import os
import base64



class BiggestCity:
    def __init__(self, city_html):
        self.city_html = city_html

    @property
    def city_title(self):
        return self.city_html.find_all("td")[2].select_one("td a").get("title")

    @property
    def city_image_small(self):
        return self.city_html.find_all("td")[1].select_one("img").get("srcset").split()[2].replace('//', 'https://')

    @property
    def country_title(self):
        return self.city_html.select_one("span.nowrap span.nowrap").get("data-sort-value")

    @property
    def country_flag(self):
        return self.city_html.select_one("span.flagicon img.thumbborder").get("srcset").split()[2].replace('//', 'https://')

    @property
    def city_image(self):
        city_image_url = f"""https://ru.wikipedia.org{self.city_html.find_all("td")[1].select_one("td a").get("href")}"""
        city_image_content = requests.get(city_image_url).content
        image_soup = BeautifulSoup(city_image_content, "html.parser")
        city_image = f"""https:{image_soup.select_one("div.fullImageLink a").get("href")}"""
        return city_image


def biggest_cities():
    cities_db = requests.get("https://w.wiki/4UK3").content
    city_soup = BeautifulSoup(cities_db, "html.parser")
    cities = city_soup.find_all("tr")[1:]
    all_cities = [BiggestCity(city) for city in cities]
    return all_cities


if __name__ == '__main__':

    print("Hello world!")