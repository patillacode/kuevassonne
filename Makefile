reload-from-server: reload-db reload-media
statics-and-migrations: docker-setup
install: python-install statics-and-migrations

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
	echo "Bringing latest db dump from server..." && \
	scp totoro:~/projects/kuevassonne/database_backup.sql . && \
	echo "Dropping local database 'kuevassonne'..."
	dropdb kuevassonne && \
	echo "Re-creating local database 'kuevassonne'..." && \
	createdb kuevassonne && \
	echo "Importing dump..." && \
	psql kuevassonne < database_backup.sql && \
	. venv/bin/activate && \
	echo "Running migrations..." && \
	python manage.py migrate && \
	echo "Latest data from server has been reloaded locally!"

reload-media:
	echo "Deleting local 'media' folder..." && \
	rm -r ./media && \
	echo "Bringing 'media' folder from server..." && \
	scp -r totoro:~/projects/kuevassonne/media  .

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

create-styles-dev:
	cd website/static/css && \
  npx tailwindcss -i styles.css -o dist.css --watch

create-styles-prod:
	cd website/static/css && \
  npx tailwindcss -i styles.css -o dist.css

