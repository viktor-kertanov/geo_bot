learn:
	python -m learn_bot.bot

geo:
	python -m telegram_geobot.main

build:
	docker build -t telegram_geobot .

login:
	aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 153366345243.dkr.ecr.eu-central-1.amazonaws.com
	docker tag telegram_geobot:1.0.1 153366345243.dkr.ecr.eu-central-1.amazonaws.com/vk-aws-repo:1.0.1
	docker push 153366345243.dkr.ecr.eu-central-1.amazonaws.com/vk-aws-repo