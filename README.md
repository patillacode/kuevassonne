<p align="center">
    <a href="https://code.patilla.es"><img src="https://img.shields.io/badge/patillacode-kuevassonne-orange?style=for-the-badge" alt=""></a>
</p>

<p align="center">
    <a href="https://github.com/patillacode/kuevassonne/pulse">
        <img src="https://img.shields.io/github/commit-activity/m/patillacode/kuevassonne?style=for-the-badge&label=commits&color=green" alt="">
    </a>
    <a href="https://github.com/patillacode/kuevassonne/stargazers">
        <img src="https://img.shields.io/github/stars/patillacode/kuevassonne?style=for-the-badge&label=stars&color=blue" alt="">
    </a>
    <a href="https://github.com/patillacode/kuevassonne/issues">
        <img src="https://img.shields.io/github/issues/patillacode/kuevassonne?style=for-the-badge&label=issues&color=red" alt="">
    </a>
    <a href="https://kuevassonne.patilla.es">
        <img src="https://img.shields.io/uptimerobot/status/m789114481-aad8a1ae4e2ead5b0c88c459?style=for-the-badge&label=live" alt="">
    </a>
</p>

# Kuevassonne
## _A personal Carcassonne game tracker website_

### Idea

We needed something better than the good old _excel file_ to keep track of our Carcassonne games (yes, we get very competitive) \
Something that would make _setting up a game_ fast, something that would let you choose the players, assign colors, select expansions, check win rates, see pictures... Basically a nice little web app\
This is it!

### Execution

I decided to give it a go with a Django project, Python is my pocket pick when it comes to programming languages and Django allows me to set the thing up as fast as it comes.
Postgresql for the DB side of things and I have a home server where I host these little projects I do (docker & nginx do the trick)

### Set up
_I assume you have a postgresql db server running somewhere_

You can just:
```bash
# clone the repo
git clone git@github.com:patillacode/relatos-a-medida.git

# go into the project folder
cd kuevassonne

# run the install command
make install
```

Or if you prefer to do things step by step, knowingly:
```bash
# clone the repo
git clone git@github.com:patillacode/kuevassonne.git

# go into the project folder
cd kuevassonne

# create a virtual environment (venv)
python3 -m venv venv

# activate the venv
source venv/bin/activate

# upgrade the pip tool
pip install --upgrade pip

# install requirements
pip install -r requirements.txt

# run the Django command to set your statics
python manage.py collectstatic

# and the migrations
python manage.py migrate
```

### Run it

```bash
# this should make the app accessible under http://localhost:8000
python manage.py runserver

```
