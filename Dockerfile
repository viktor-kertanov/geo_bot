FROM python:3.11

WORKDIR /opt

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/opt

RUN mkdir -p /opt/src

COPY requirements.txt requirements.txt
COPY .env .env 

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt

COPY src/. src/.
COPY tests/. tests/.

ENTRYPOINT ["gunicorn", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8001", "src.main:app"]