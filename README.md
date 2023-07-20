# Телеграм бот "Географичка"

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Прокачай знания в политической географии. Знай все флаги и страны

Географический обучающий бот [https://t.me/study_geo_bot]
Гео-телеграм бот должен уметь играть в города, во флаги стран, в столицы, в определение страны по местоположению на карте. Вести статистику по пользователям и выдавать результаты.

## Как деплоить проект на AWS Fargate

1. docker build -t telegram_geobot:1.0.3 . - билдим контейнер
2. docker run telegram_geobot:1.0.3- запускаем контейнер и смотрим, что в тестовом режиме всё работает в тестовом боте
3. Изменяем настройки .env файла, чтобы не тест-деплой был, а продовй
4. docker tag telegram_geobot:1.0.3 153366345243.dkr.ecr.eu-central-1.amazonaws.com/vk-aws-repo:1.0.3
5. login if needed:
   aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 153366345243.dkr.ecr.eu-central-1.amazonaws.com
6. docker push 153366345243.dkr.ecr.eu-central-1.amazonaws.com/vk-aws-repo:1.0.3
7. In AWS create new task definition.
8. In AWS services update the running service with a new task definition.
