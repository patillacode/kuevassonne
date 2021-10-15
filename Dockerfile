FROM python:3.8-slim-buster

MAINTAINER PatillaCode

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y make gcc
RUN mkdir kuevassonne

COPY . kuevassonne

WORKDIR kuevassonne

COPY ./requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

