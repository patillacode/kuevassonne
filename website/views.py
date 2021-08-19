import datetime

from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import redirect, render, reverse
from django.utils.timezone import make_aware

from .forms import (
    CreateExpansionInGameForm,
    CreateGameForm,
    CreatePlayerForm,
    CreatePlayerInGameForm,
    ImageForm,
    RecordForm,
)
from .models import (
    Expansion,
    ExpansionInGame,
    Game,
    Image,
    Player,
    PlayerInGame,
    Record,
)


def get_general_standings_per_game(players):
    all_games = Game.objects.all().order_by('-id')
    all_players = players

    player_data = {}

    for game in all_games:
        player_data[game.id] = {}

        all_players_in_game = PlayerInGame.objects.filter(game=game).order_by(
            '-player__win_rate'
        )
        for player_in_game in all_players_in_game:

            for player in all_players:

                if player.name not in player_data[game.id].keys():
                    player_data[game.id][player.name] = None

                if player_in_game.player == player:
                    player_data[game.id][player_in_game.player.name] = {
                        'position': player_in_game.position,
                        'score': player_in_game.score,
                    }
    return player_data


def process_data_per_player(general_standings):
    data_per_player = {}
    for player_name, game_data in general_standings.items():
        data_per_player[player_name] = []
        for game_id, data in game_data.items():
            data_per_player[player_name].append(data)

    return data_per_player


def games(request, feedback_message=None):
    players = Player.objects.all().order_by('-win_rate')

    context = {
        'players': players,
        'data_per_game': get_general_standings_per_game(players),
        'feedback_message': feedback_message,
    }
    return render(request, 'website/games.html', context)


def index(request, feedback_message=None):
    context = {}
    return render(request, 'website/index.html', context)


def players(request, player_id=None):
    if player_id:
        pass
    else:
        all_players = Player.objects.all()

        chart_labels = ['Oro', 'Plata', 'Bronce', 'otros']
        chart_data = {}

        for player in all_players:
            player_games = player.player_games
            chart_data[player.id] = [
                player_games.filter(position=1).count(),
                player_games.filter(position=2).count(),
                player_games.filter(position=3).count(),
                player_games.exclude(position__in=[1, 2, 3]).count(),
            ]

        context = {
            'players': all_players.order_by('-win_rate'),
            'chart': {'labels': chart_labels, 'data': chart_data},
        }
        return render(request, 'website/players.html', context)


@login_required
def create_player(request):
    feedback_message = None

    if request.method == 'POST':
        form = CreatePlayerForm(request.POST)
        if form.is_valid():
            player_name = form.cleaned_data['name']
            Player.objects.create(name=player_name)
            feedback_message = {'message': f'"{player_name}" creado', 'color': 'green'}
        else:
            feedback_message = {
                'message': f'"{form.data["name"]}" ya existe',
                'color': 'red',
            }

    context = {
        # 'game_form': CreateGameForm(initial={'start_date': datetime.datetime.now()}),
        'player_form': CreatePlayerForm(),
        'feedback_message': feedback_message,
    }
    return render(request, 'website/create_player.html', context)


@login_required
def create_expansions_in_game(request, game_id):
    game = Game.objects.get(pk=game_id)
    feedback_message = None

    if request.method == 'POST':
        form = CreateExpansionInGameForm(request.POST)

        if form.is_valid():
            try:
                expansion = Expansion.objects.get(name=form.cleaned_data['expansion'])
                use_rules = form.cleaned_data['use_rules']
                use_tiles = form.cleaned_data['use_tiles']
                expansion_in_game = ExpansionInGame.objects.create(
                    expansion=expansion,
                    use_rules=use_rules,
                    use_tiles=use_tiles,
                    game=game,
                )

                game.calculate_tiles_for_game()

                feedback_message = {
                    'message': (
                        f'Expansión "{expansion_in_game.expansion.name}" añadida a'
                        f' Partida {game.id}'
                    ),
                    'color': 'green',
                }

            except IntegrityError as err:
                feedback_message = {
                    'message': (
                        f'La expasión "{form.cleaned_data["expansion"]}" ya está en la '
                        f'Partida {game_id}. {err}'
                    ),
                    'color': 'red',
                }
        else:
            feedback_message = {'message': {form.errors}, 'color': 'red'}

    context = {
        'game_id': game_id,
        'expansions_in_game': ExpansionInGame.objects.filter(game__id=game_id),
        'expansions_in_game_form': CreateExpansionInGameForm(),
        'feedback_message': feedback_message,
        'total_number_of_tiles': game.total_number_of_tiles,
    }
    return render(request, 'website/create_expansions_in_game.html', context)


@login_required
def create_game(request):

    feedback_message = None

    if request.method == 'POST':
        form = CreateGameForm(request.POST)

        if form.is_valid():
            game_start_date = form.cleaned_data['start_date']
            game = Game.objects.create(start_date=game_start_date)
            # feedback_message = {'message': f'{game} creada', 'color': 'green'}
            # context = {'feedback_message': feedback_message}
            return redirect(
                reverse('create_expansions_in_game', kwargs={'game_id': game.id})
            )

        else:
            feedback_message = {'message': {form.errors}, 'color': 'red'}

    context = {
        'game_form': CreateGameForm(initial={'start_date': datetime.datetime.now()}),
        'feedback_message': feedback_message,
    }
    return render(request, 'website/create_game.html', context)


@login_required
def create_players_in_game(request, game_id):
    feedback_message = None

    if request.method == 'POST':
        form = CreatePlayerInGameForm(request.POST)
        if form.is_valid():
            try:
                player_in_game = PlayerInGame.objects.create(
                    player=Player.objects.get(name=form.cleaned_data['player']),
                    color=form.cleaned_data['color'],
                    game=Game.objects.get(pk=game_id),
                )
                feedback_message = {
                    'message': (
                        f'"{player_in_game.player}" añadido a Partida '
                        f'{player_in_game.game.id}'
                    ),
                    'color': 'green',
                }
            except IntegrityError:
                feedback_message = {
                    'message': (
                        f'"{form.cleaned_data["player"]}" ya está en la partida o '
                        'el color ya ha sido utilizado.'
                    ),
                    'color': 'red',
                }
        else:
            feedback_message = {'message': {form.errors}, 'color': 'red'}

    context = {
        'game_id': game_id,
        'players_in_game': PlayerInGame.objects.filter(game__id=game_id),
        'players_in_game_form': CreatePlayerInGameForm(),
        'feedback_message': feedback_message,
    }
    return render(request, 'website/create_players_in_game.html', context)


@login_required
def in_game(request, game_id, feedback_message=None):
    players_in_game = PlayerInGame.objects.filter(game__id=game_id)

    session_key = 'players_points'
    if request.session.get(session_key, None) is None:
        request.session[session_key] = {}
        for player in players_in_game:
            player_name = player.player.name.lower()
            request.session[session_key][player_name] = {
                'point_list': [],
                'total_points': 0,
            }

    if request.method == 'POST' and 'image' in request.FILES:
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_image = form.cleaned_data['image']
            image_name = form.cleaned_data['name']
            game = Game.objects.get(pk=game_id)
            image = Image.objects.create(image=uploaded_image, name=image_name, game=game)
            feedback_message = {
                'message': (
                    f'Imagen subida (<a target="_blank" href="{image.image.url}">'
                    ' Ver</a>)'
                ),
                'color': 'green',
            }
        else:
            feedback_message = {'message': {form.errors}, 'color': 'red'}

    elif request.method == 'POST' and 'points_to_add' in request.POST:

        try:
            points_to_add = int(request.POST['points_to_add'])

        except ValueError:
            feedback_message = {
                'message': (
                    f'"{request.POST["points_to_add"]}" no es un número válido...'
                ),
                'color': 'red',
            }
        else:
            for player in players_in_game:
                player_name = player.player.name.lower()
                if str(player.id) == request.POST['player_id']:
                    request.session[session_key][player_name]['point_list'].append(
                        points_to_add
                    )
                    total_points = sum(
                        request.session[session_key][player_name]['point_list']
                    )
                    request.session[session_key][player_name][
                        'total_points'
                    ] = total_points
                    player.score = total_points
                    player.save()

                else:
                    request.session[session_key][player_name]['point_list'].append(0)

    context = {
        'players_in_game': players_in_game,
        'game': Game.objects.get(pk=game_id),
        session_key: request.session.get(session_key),
        'feedback_message': feedback_message,
        'images_form': ImageForm(),
    }

    return render(request, 'website/in_game.html', context)


@login_required
def finalize(request, game_id):

    try:
        game = Game.objects.get(pk=game_id)
        game.end_date = make_aware(datetime.datetime.now())
        game.save()
        game.finalize()
        feedback_message = {'message': f'{game} finalizada', 'color': 'green'}

    except Exception as err:
        feedback_message = {'message': (err), 'color': 'red'}
        return in_game(request, game_id, feedback_message)

    # request.session.flush()
    request.session.pop('players_points')
    return game_info(request, game.id)


def game_info(request, game_id):
    game = Game.objects.get(pk=game_id)
    context = {
        'game': game,
        'records': game.game_records.all(),
        'game_images': game.game_images.all(),
        'players_in_game': game.game_players.all(),
        'expansions_in_game': game.game_expansions.all(),
        'total_number_of_tiles': game.total_number_of_tiles,
    }
    return render(request, 'website/game_info.html', context)


def records(request):
    context = {'records': Record.objects.all()}
    return render(request, 'website/records.html', context)


@login_required
def add_record(request):
    feedback_message = None
    if request.method == 'POST':
        form = RecordForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_image = form.cleaned_data['image']
            record_name = form.cleaned_data['name']
            record_game = form.cleaned_data['game']
            record_description = form.cleaned_data['description']

            record = Record.objects.create(
                image=uploaded_image,
                name=record_name,
                game=record_game,
                description=record_description,
            )
            feedback_message = {
                'message': f'Record "{record.name or record.id}" guardado',
                'color': 'green',
            }
        else:
            feedback_message = {'message': {form.errors}, 'color': 'red'}

    context = {'record_form': RecordForm(), 'feedback_message': feedback_message}
    return render(request, 'website/add_record.html', context)
