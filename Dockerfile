FROM python:3.11

WORKDIR /opt

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/opt

RUN mkdir -p /opt/telegram_geobot

COPY requirements.txt requirements.txt
COPY .env .env 

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt

COPY telegram_geobot/. telegram_geobot/.

ENTRYPOINT ["python3", "-m", "telegram_geobot.main"]