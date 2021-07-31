install: python-install

python-install:
	python3 -m venv venv && \
	. venv/bin/activate && \
	pip install --upgrade pip && \
	pip install -r requirements.txt

serve:
	. venv/bin/activate && \
	FLASK_APP=flaskr FLASK_ENV=development \
	APP_SETTINGS=flaskr.config.DevelopmentConfig \
	flask run --extra-files flaskr/templates/base.html

shell:
	. venv/bin/activate && \
	python manage.py shell

reset-db:
	. venv/bin/activate && \
	rm -rf db.sqlite3 && \
	rm -rf website/migrations/*.py && \
	python manage.py migrate && \
	export DJANGO_SUPERUSER_PASSWORD='deved' && \
	export DJANGO_SUPERUSER_USERNAME='admin' && \
	export DJANGO_SUPERUSER_EMAIL='admin@admin.com' && \
	python manage.py createsuperuser --noinput && \
	python manage.py makemigrations website && \
	python manage.py migrate
