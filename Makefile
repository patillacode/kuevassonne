install: python-install

python-install:
	python3 -m venv venv && \
	. venv/bin/activate && \
	pip install --upgrade pip && \
	pip install -r requirements.txt

docker-setup:
	python manage.py collectstatic --no-input && \
	python manage.py migrate
# 	python manage.py createsuperuser --noinput

docker-reset:
	docker-compose down --volumes && \
	docker rmi kuevassonne_website || true && \
	docker-compose build && \
	docker-compose up --build --remove-orphans

serve:
	. venv/bin/activate && \
	python manage.py runserver

shell:
	. venv/bin/activate && \
	python manage.py shell

reset-db:
	. venv/bin/activate && \
	rm -rf db.sqlite3 && \
	dropdb kuevassonne && \
	createdb kuevassonne && \
	rm -rf website/migrations/*.py && \
	python manage.py migrate && \
	export DJANGO_SUPERUSER_PASSWORD='deved' && \
	export DJANGO_SUPERUSER_USERNAME='admin' && \
	export DJANGO_SUPERUSER_EMAIL='admin@admin.com' && \
	python manage.py createsuperuser --noinput && \
	python manage.py makemigrations website && \
	python manage.py migrate
