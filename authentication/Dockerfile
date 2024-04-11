FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

WORKDIR /app

COPY ./requirement.txt .

RUN pip install -r requirements.txt

COPY . /app/