from config import load
import random
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import ephem
import requests
from bs4 import BeautifulSoup as bs

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log')


PROXY = {
    'proxy_url': 'socks5://t1.learn.python.ru:1080',
    'urllib3_proxy_kwargs': {
        'username': 'learn',
        'password': 'python'
    }
}


def greet_user(update, context):
    print("Вызван /start")
    replies = [
        "Hello!",
        "Привет!",
        "Что делаешь?",
        "Йоу Пайтон реплай"
    ]
    random_int = random.randint(0,len(replies)-1)
    final_reply = replies[random_int]

    update.message.reply_text(final_reply)



def planets(update, context):
    """
    Команда /planets показывает список доступных в ephem планет
    """
    print("Выводим имеющиеся планеты")
    astro_bodies = ephem._libastro.builtin_planets()
    planets = [body[2] for body in astro_bodies if body[1] == 'Planet']
    planets_reply = "\n".join(planets)
    update.message.reply_text(planets_reply)


def constellation(update, context):
    print("Ищем созвездие планеты")
    planets_input = context.args
    planets_input = [p.lower().strip() for p in planets_input]
    print(planets_input)
    astro_bodies = ephem._libastro.builtin_planets()
    planets = [body[2].lower() for body in astro_bodies if body[1] == 'Planet']
    print(planets)
    for planet in planets_input:
        print(planet)
        if planet in planets:
            planet = planet.capitalize()
            print(f"The planet is: {planet}")
            planet_object = getattr(ephem, planet)()
            planet_object.compute(epoch=ephem.now())
            constellation = ephem.constellation(planet_object)[1]
            print(constellation)
            const_reply = f"{planet} is in {constellation}.\n"
            print(const_reply)
            update.message.reply_text(const_reply)
        else:
            const_reply = f"\n{planet} is not in the list of planets. Call /planets to see the list."
            update.message.reply_text(const_reply)

def talk_to_me(update, context):
    user_text = update.message.text
    print(user_text)
    update.message.reply_text(user_text)

city_db_ext = ['Москва', 'Санкт-Петербург', 'Гренада', 'Антананариву', 'Уссурийск', 'Копенгаген', 'Новороссийск', 'Калвер Сити', 'Иркутск', 'Амстердам', 'Антверпен']
city_db_ext = [city.lower().strip() for city in city_db_ext]
user_cities = []

def city_play(update, context, city_db = city_db_ext):
    user = update.message.from_user
    reply = f"{user['first_name']} {user['last_name']} {user['id']}"
    update.message.reply_text(reply)
    print(f"{user}")
    city_db = [city.lower().strip() for city in city_db_ext]
    user_input_city = context.args[0].lower().strip()
    print(f"User input city: {user_input_city}")
    last_letter = user_input_city[-1]
    print(last_letter)
    bot_cities_by_letter = [city for city in city_db if city[0] == last_letter]
    print(bot_cities_by_letter)
    final_city = random.choice(bot_cities_by_letter)
    print(f"Final citty: {final_city}")
    city_db_ext.remove(final_city)
    user_cities.append(context.args[0].lower().strip())
    print(city_db)
    print(f"User cities: {user_cities}")
    final_reply = f"Город на букву {last_letter.capitalize()}: {final_city.capitalize()}. Ваш ход!"
    print(f"City db external: {city_db_ext}")
    print(f"User cities: {user_cities}")
    update.message.reply_text(final_reply)


def main():
    config = load()
    mybot = Updater(config.api_token, request_kwargs=PROXY, use_context=True)
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(CommandHandler("city", city_play, pass_args=True))
    dp.add_handler(CommandHandler("planets", planets))
    dp.add_handler(CommandHandler("constellation", constellation, pass_args=True))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    mybot.start_polling()
    mybot.idle()


if __name__ == "__main__":
    main()
