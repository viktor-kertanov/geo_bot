import requests
from bs4 import BeautifulSoup


class WikiCountry:
    def __init__(self, country_wiki_url):
        self.country_wiki_url = country_wiki_url

    @property
    def country_flag(self):
        """
        Locating the url that has the picture of a country flag.
        """

        req = requests.get(self.country_wiki_url)
        soup = BeautifulSoup(req.content, "html.parser")
        infobox_data = soup.select_one("table.infobox.vcard")
        try:
            images = infobox_data.select("a.image")
        except AttributeError:
            return None
        flags = [el for el in images if "flag" in el.get("title", "").lower()]
        try:
            country_flag_url = flags[0].get("href")
        except IndexError:
            return None

        country_flag = f"https://en.wikipedia.org{country_flag_url}"
        country_flag_image = requests.get(country_flag).content
        flag_image_soup = BeautifulSoup(country_flag_image, "html.parser")
        country_images_url = flag_image_soup.select_one(
            "span.mw-filepage-other-resolutions"
        ).find_all("a")
        max_res_index = self._wiki_max_res_img(country_images_url)
        country_full_image_url = country_images_url[max_res_index].get("href")
        country_full_image_url = f"https:{country_full_image_url}"
        return country_full_image_url

    @property
    def position_on_map_image(self):
        """ "
        Locating the url of an image that shows the position of a country on a map
        """
        position_page = requests.get(self.country_wiki_url).content
        position_soup = BeautifulSoup(position_page, "html.parser")
        infobox_full_data = position_soup.select("td.infobox-full-data a")
        position = [
            el
            for el in infobox_full_data
            if "projection" in el.get("href", "").lower()
            or "location" in el.get("href", "").lower()
            or "location" in el.get("title", "").lower()
            or "ortho" in el.get("href", "").lower()
        ]
        try:
            image_page_url = position[0].get("href")
        except IndexError:
            return None

        image_page_url = f"https://en.wikipedia.org{image_page_url}"
        image_page = requests.get(image_page_url).content
        image_soup = BeautifulSoup(image_page, "html.parser")
        try:
            position_image_res = image_soup.select_one(
                "span.mw-filepage-other-resolutions"
            ).find_all("a")
        except AttributeError:
            return None
        max_res_index = self._wiki_max_res_img(position_image_res)
        position_image = position_image_res[max_res_index].get("href")
        position_image = f"https:{position_image}"
        return position_image

    def _wiki_max_res_img(self, html_list):
        """Returning the index with the highest resolution on wikipedia"""
        res_list = []
        for item in html_list:
            res = int(item.text.split()[0].replace(",", ""))
            res_list.append(res)
        max_res = max(res_list)
        # print(f"Res_list:{res_list}")
        # print(f"Max res: {max_res}")
        return res_list.index(max_res)


if __name__ == "__main__":
    country_page = "https://en.wikipedia.org/wiki/Barbados"

    a = WikiCountry(country_page)
    flag_url = a.country_flag
    position_url = a.position_on_map_image
