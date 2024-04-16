FROM python:latest

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1


COPY ./requirements.txt .

RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y netcat-traditional

COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

COPY . /app/

ENTRYPOINT [ "/app/entrypoint.sh" ]