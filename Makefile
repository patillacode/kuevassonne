install: python-install

python-install:
	python3 -m venv venv && \
	. venv/bin/activate && \
	pip install --upgrade pip && \
	pip install -r requirements.txt

docker-setup:
	python manage.py collectstatic --no-input && \
	python manage.py migrate

docker-reset:
	git pull origin main && \
	docker-compose build && \
	docker-compose up -d --remove-orphans

docker-full-reset:
	docker-compose down --volumes && \
	docker rmi kuevassonne_website || true && \
	docker-compose build && \
	docker-compose up --remove-orphans

serve:
	. venv/bin/activate && \
	python manage.py runserver

shell:
	. venv/bin/activate && \
	python manage.py shell

reload-db:
	dropdb kuevassonne && \
	createdb kuevassonne && \
	psql kuevassonne < database_backup.sql && \
	. venv/bin/activate && \
	python manage.py migrate

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
