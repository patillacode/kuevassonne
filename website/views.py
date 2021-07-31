from django.shortcuts import render

from .models import Game, Player, PlayerInGame


def get_general_standings_per_game(players):
    all_games = Game.objects.all()
    all_players = players

    player_data = {}
    # for player in all_players:
    #     player_data[player.name] = {}

    for game in all_games:
        player_data[game.id] = {}

        all_players_in_game = PlayerInGame.objects.filter(game=game).order_by(
            '-player__win_rate'
        )
        for player_in_game in all_players_in_game:
            player_data[game.id][player_in_game.player.name] = {
                'position': player_in_game.position,
                'score': player_in_game.score,
            }

    for game in all_games:
        for player in all_players:
            if player.name not in player_data[game.id].keys():
                player_data[game.id][player.name] = None

    return player_data


def get_general_standings_per_player(players):
    all_games = Game.objects.all()
    all_players = players

    player_data = {}
    for player in all_players:
        player_data[player.name] = {}

    for game in all_games:
        all_players_in_game = PlayerInGame.objects.filter(game=game).order_by(
            '-player__win_rate'
        )
        for player_in_game in all_players_in_game:
            player_data[player_in_game.player.name][game.id] = {
                'position': player_in_game.position,
                'score': player_in_game.score,
            }

    for game in all_games:
        for player in all_players:
            if game.id not in player_data[player.name].keys():
                player_data[player.name][game.id] = None

    return player_data


def process_data_per_player(general_standings):
    data_per_player = {}
    for player_name, game_data in general_standings.items():
        data_per_player[player_name] = []
        for game_id, data in game_data.items():
            data_per_player[player_name].append(data)

    return data_per_player


def index(request):
    players = Player.objects.all().order_by('-win_rate')
    general_standings = get_general_standings_per_player(players)
    data_per_player = process_data_per_player(general_standings)

    context = {
        'players': players,
        'data_per_player': data_per_player,
        'data_per_game': get_general_standings_per_game(players),
        'games_ids': Game.objects.all().values_list('id', flat=True),
    }
    return render(request, 'website/index.html', context)


def create(request):
    context = {}
    return render(request, 'website/create.html', context)
