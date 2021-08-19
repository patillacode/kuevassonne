FROM python:3.8-slim-buster

MAINTAINER PatillaCode

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y make gcc
RUN mkdir kuevassonne

COPY . kuevassonne

WORKDIR kuevassonne

RUN pip install --upgrade pip && pip install -r requirements.txt

# RUN python manage.py collectstatic --noinput
# RUN python manage.py migrate

# CMD ["python", "manage.py", "runserver", "0.0.0.0:5055"]
# CMD exec gunicorn kuevassonne.wsgi:application --bind 0.0.0.0:5055 --workers 1
