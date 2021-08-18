install: python-install

python-install:
	python3 -m venv venv && \
	. venv/bin/activate && \
	pip install --upgrade pip && \
	pip install -r requirements.txt

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

docker-reset:
	echo "Stopping container..." && \
	docker stop kuevassonne || true && \
	echo "Deleting container..." && \
	docker rm kuevassonne || true && \
	echo "Deleting image..." && \
	docker rmi kuevassonne || true && \
	echo "Rebuilding image..." && \
	docker build --tag kuevassonne . && \
	echo "Running new image in new container..." && \
	docker run -d --name kuevassonne --publish 5055:5055 kuevassonne && \
	echo "Set restart on failure..." && \
	docker update --restart=on-failure kuevassonne
