import datetime
from .utils import get_achievements

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.timezone import make_aware

from .forms import (
    CreateExpansionInGameForm,
    CreatePlayerForm,
    CreatePlayerInGameForm,
    ImageForm,
    RecordForm,
)
from .models import ALL_COLORS, ExpansionInGame, Game, Image, Player, PlayerInGame, Record


def index(request, feedback_message=None):
    return render(request, 'website/index.html')


def games(request, feedback_message=None):
    games = []
    for game in Game.objects.filter(finalised=True).order_by('-id'):
        games.append(
            {
                'id': game.id,
                'draw': game.draw,
                'game_players': game.game_players.all().order_by('-score'),
                'remaining_spots': range(
                    settings.MAX_NUMBER_OF_PLAYERS - game.game_players.count()
                ),
            }
        )
    context = {
        'games': games,
        'number_of_players_in_system': Player.objects.filter(games__gt=0)
        .distinct('name')
        .count(),
        'feedback_message': feedback_message,
    }
    return render(request, 'website/games.html', context)


def players(request, player_id=None):
    if player_id:
        # TODO: add a dedicated page for each player with deeper statistic analysis
        pass
    else:
        all_players = Player.objects.filter(games__gt=0).order_by('-win_rate').distinct()

        chart_labels = ['Oro', 'Plata', 'Bronce', 'otros']
        chart_data = {}

        players_global_data = []

        for player in all_players:
            player_games = player.player_games
            chart_data[player.id] = [
                player_games.filter(position=1).count(),
                player_games.filter(position=2).count(),
                player_games.filter(position=3).count(),
                player_games.exclude(position__in=[1, 2, 3]).count(),
            ]

            players_global_data.append(
                {
                    'favourite_color': player.player_games.values('color')
                    .annotate(color_frequency=Count('color'))
                    .order_by('-color_frequency')
                    .first()['color'],
                    'games_played': player.player_games.count(),
                    'wins': player.wins,
                    'losses': player.losses,
                    'average_position': player.average_position,
                    'win_rate': player.win_rate,
                    'id': player.id,
                    'name': player.name,
                }
            )

        context = {
            'achievements': get_achievements(),
            'players_global': players_global_data,
            'chart': {'labels': chart_labels, 'data': chart_data},
        }
        return render(request, 'website/players.html', context)


@login_required
def create_player(request, feedback_message=None):

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
        'player_form': CreatePlayerForm(),
        'feedback_message': feedback_message,
    }
    return render(request, 'website/create_player.html', context)


@login_required
def create_expansions_in_game(request, game_id):
    game = Game.objects.get(pk=game_id)
    feedback_message = None

    if request.method == 'POST':
        if request.POST.get('delete_expansion_in_game_id', None):
            expansion_in_game = get_object_or_404(
                ExpansionInGame, pk=request.POST['delete_expansion_in_game_id']
            )
            game_id = expansion_in_game.game.id
            feedback_message = {
                'message': ('Are you ok?'),
                'color': 'yellow',
            }
            try:
                feedback_message = {
                    'message': (
                        f'Expansion "{expansion_in_game.expansion.name}" eliminada '
                        f'de la Partida {game_id}'
                    ),
                    'color': 'green',
                }
                expansion_in_game.delete()

            except Exception as err:
                feedback_message = {
                    'message': (f'WTF, llama a Dvitto: {err}'),
                    'color': 'red',
                }
        else:
            form = CreateExpansionInGameForm(request.POST)

            if form.is_valid():
                try:
                    expansion_in_game = ExpansionInGame.objects.create(
                        expansion=form.cleaned_data['expansion'],
                        use_rules=form.cleaned_data['use_rules'],
                        use_tiles=form.cleaned_data['use_tiles'],
                        game=game,
                    )

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
                feedback_message = {'message': form.errors, 'color': 'red'}

        game.calculate_tiles_for_game()

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

    try:
        game = Game.objects.create(start_date=datetime.datetime.now())
        return redirect(reverse('create_expansions_in_game', kwargs={'game_id': game.id}))

    except Exception as err:
        feedback_message = {'message': err, 'color': 'red'}

    return create_player(request, feedback_message)


@login_required
def create_players_in_game(request, game_id, feedback_message=None):

    if request.method == 'POST':
        if request.POST.get('delete_player_in_game_id', None):
            player_in_game = get_object_or_404(
                PlayerInGame, pk=request.POST['delete_player_in_game_id']
            )
            game_id = player_in_game.game.id

            feedback_message = {
                'message': ('Are you ok?'),
                'color': 'yellow',
            }

            try:
                feedback_message = {
                    'message': (
                        f'"{player_in_game.player}" eliminado de la Partida {game_id}'
                    ),
                    'color': 'green',
                }
                player_in_game.delete()

            except Exception as err:
                feedback_message = {
                    'message': (f'WTF, llama a Dvitto: {err}'),
                    'color': 'red',
                }
        else:
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
                feedback_message = {'message': form.errors, 'color': 'red'}

    players_in_game_form = CreatePlayerInGameForm()
    players_in_game_form.fields['player'].queryset = Player.objects.exclude(
        id__in=PlayerInGame.objects.filter(game__id=game_id).values_list(
            'player__id', flat=True
        )
    )

    all_colors = ALL_COLORS
    used_colors = [
        (player_in_game.color.upper(), player_in_game.color.title())
        for player_in_game in PlayerInGame.objects.filter(game__id=game_id)
    ]
    available_colors = [item for item in all_colors if item not in used_colors]
    players_in_game_form.fields['color'].choices = available_colors

    context = {
        'game_id': game_id,
        'players_in_game': PlayerInGame.objects.filter(game__id=game_id),
        'players_in_game_form': players_in_game_form,
        'feedback_message': feedback_message,
    }
    return render(request, 'website/create_players_in_game.html', context)


@login_required
def in_game(request, game_id, feedback_message=None):
    players_in_game = PlayerInGame.objects.filter(game__id=game_id).order_by(
        'player__name'
    )
    game = Game.objects.get(pk=game_id)

    session_key = 'players_points'
    if not request.session.get(session_key):
        # this is the first time we get to the "in_game" screen
        # We set the current datetime to the Game
        game.start_date = datetime.datetime.now()
        game.save()

        # And we set the sessions for scoring
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
            image = Image.objects.create(image=uploaded_image, name=image_name, game=game)
            feedback_message = {
                'message': (
                    f'Imagen subida (<a target="_blank" href="{image.image.url}">'
                    ' Ver</a>)'
                ),
                'color': 'green',
            }
        else:
            feedback_message = {'message': form.errors, 'color': 'red'}

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
        session_key: request.session.get(session_key),
        'players_in_game': players_in_game,
        'game': game,
        'game_images': game.game_images.all(),
        'expansions_in_game': game.game_expansions.order_by(
            'expansion__is_mini', 'expansion__name', 'expansion__number_of_tiles'
        ),
        'total_number_of_tiles': game.total_number_of_tiles,
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

    finally:
        del request.session['players_points']

    return redirect(reverse('game_info', kwargs={'game_id': game.id}))


def game_info(request, game_id):
    game = Game.objects.get(pk=game_id)
    context = {
        'game': game,
        'records': game.game_records.all(),
        'game_images': game.game_images.all(),
        'players_in_game': game.game_players.all().order_by('-score'),
        'expansions_in_game': game.game_expansions.order_by(
            'expansion__is_mini', 'expansion__name', 'expansion__number_of_tiles'
        ),
        'total_number_of_tiles': game.total_number_of_tiles,
    }
    return render(request, 'website/game_info.html', context)


def records(request):
    context = {'achievements': get_achievements(), 'records': Record.objects.all()}
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
            feedback_message = {'message': form.errors, 'color': 'red'}

    context = {'record_form': RecordForm(), 'feedback_message': feedback_message}
    return render(request, 'website/add_record.html', context)
