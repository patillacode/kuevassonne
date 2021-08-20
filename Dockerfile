FROM python:3.8-slim-buster

MAINTAINER PatillaCode

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y make gcc
RUN mkdir kuevassonne
#     # && \
#     # mkdir -p /static && \
#     # mkdir -p /media && \
#     # chmod -R 755 /static && \
#     # chmod -R 755 /media

COPY . kuevassonne

WORKDIR kuevassonne

# WORKDIR /kuevassonne
# ADD ./kuevassonne

COPY ./requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

