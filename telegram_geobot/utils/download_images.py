from random import randint
from time import sleep
from fake_useragent import UserAgent
import requests


def dl_img(img_url, filename):
    headers = {"User-Agent": str(UserAgent().random)}
    image = requests.get(img_url, headers=headers).content
    if not "Wikimedia Error" in str(image):
        with open(filename, 'wb') as file:
            file.write(image)
            print(f"Success: {filename}")
            sleep(randint(5, 7))
    else:
        print(f"Could not download:\n{img_url}")
        return None


if __name__ == '__main__':
    print('Hello world!')