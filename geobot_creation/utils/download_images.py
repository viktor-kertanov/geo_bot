from random import randint
from time import sleep

import requests
from fake_useragent import UserAgent


def dl_img(img_url, filename):
    ua = UserAgent()
    headers = {"User-Agent": str(ua.random)}
    image = requests.get(img_url, headers=headers).content
    if str(image) not in "Wikimedia Error":
        with open(filename, "wb") as file:
            file.write(image)
            print(f"Success: {filename}")
            sleep(randint(5, 7))
    else:
        print(f"Could not download:\n{img_url}")
        return None


if __name__ == "__main__":
    print("Hello world!")
