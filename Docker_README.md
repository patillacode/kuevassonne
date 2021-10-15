# Kuevassonne (Docker)
## Steps to create a Docker image and run the containers


- Clone the repo
```bash
git clone https://github.com/patillacode/kuevassonne.git
```

- Create a `.env.prod` file under `kuevassonne/kuevassonne`with the following data (these are env vars for the Website container):
```bash
SECRET_KEY=YOUR_SECRET_KEY
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=YOUR_DATABASE_NAME
DATABASE_USER=YOUR_DATABASE_USERNAME
DATABASE_PASSWORD=YOUR_DATABASE_PASSWORD
DATABASE_HOST=postgres
DATABASE_PORT=5432
ALLOWED_HOSTS=127.0.0.1,localhost,YOUR_CUSTOM_DOMAIN.com
DEBUG=1
DJANGO_SUPERUSER_USERNAME=YOUR_DJANGO_ADMIN_USER_NAME
DJANGO_SUPERUSER_PASSWORD=YOUR_DJANGO_ADMIN_PASSWORD
DJANGO_SUPERUSER_EMAIL=YOUR_EMAIL
```

- Create a `env.data` file under `kuevassonne/kuevassonne` with the following data (these are env vars for the Postgres container):
```bash
POSTGRES_DB=YOUR_DATABASE_NAME
POSTGRES_USER=YOUR_DATABASE_USERNAME
POSTGRES_PASSWORD=YOUR_DATABASE_PASSWORD
```

- Create Docker images and run the container (I do this for you in a `make` command):
```bash
make docker-full-reset
```

- The first time you run it please create the superuser/admin by doing the following (this only need to be done the very first time you run it, since the database is set as a volume):
```bash
# access your container
docker exec -it kuevassonne_website_1 /bin/sh

# create the superuser with this command
python manage.py createsuperuser --noinput
```

At this point you should be able to access the site at `http://localhost:5055/`
Remember you would need to add the expansions you want through the admin: `http://localhost:5055/admin/`
