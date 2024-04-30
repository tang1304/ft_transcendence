FROM python:3.11.4-slim-buster

ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir -p $APP_HOME
RUN mkdir $APP_HOME/staticfiles
RUN mkdir $APP_HOME/media
WORKDIR $APP_HOME

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends netcat
RUN pip install --upgrade pip
COPY ./app/requirements.txt .
RUN pip install -r requirements.txt

COPY ./app .

COPY ./docker/django/entrypoint.sh .
COPY ./app/user_management/static/default_pp.jpg /home/app/web/media/default_pp.jpg
RUN chmod +x entrypoint.sh

ENTRYPOINT ["bash" , "entrypoint.sh"]

EXPOSE 8000
