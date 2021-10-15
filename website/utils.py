from django.db.models import Count, Max
from .models import Player, PlayerInGame


def get_player_max_win_streak(player):
    max_streak = 0
    current_streak = 0

    player_positions = list(
        PlayerInGame.objects.filter(player=player)
        .order_by('game__id')
        .values_list('position', flat=True)
    )

    for position in player_positions:
        if position == 1:
            current_streak += 1
        else:
            current_streak = 0

        if current_streak > max_streak:
            max_streak = current_streak

    return max_streak


def get_player_max_loss_streak(player):
    max_streak = 0
    current_streak = 0

    players_in_game = PlayerInGame.objects.filter(player=player).order_by('game__id')

    for player_in_game in players_in_game:
        if player_in_game.position == player_in_game.game.game_players.count():
            current_streak += 1
        else:
            current_streak = 0

        if current_streak > max_streak:
            max_streak = current_streak

    return max_streak


def get_achievements():
    all_players = Player.objects.all()
    if not all_players:
        return {}

    win_streak_data = {
        player.name: get_player_max_win_streak(player) for player in all_players
    }
    max_win_streak = max(win_streak_data.values())
    win_streak_names = [
        key for key, value in win_streak_data.items() if value == max_win_streak
    ]

    loss_streak_data = {
        player.name: get_player_max_loss_streak(player) for player in all_players
    }
    max_loss_streak = max(loss_streak_data.values())
    loss_streak_names = [
        key for key, value in loss_streak_data.items() if value == max_loss_streak
    ]

    best_win_streak = {
        'player_name': ' & '.join(win_streak_names),
        'value': max_win_streak,
    }

    worst_loss_streak = {
        'player_name': ' & '.join(loss_streak_names),
        'value': max_loss_streak,
    }

    most_losses_player = all_players.order_by(
        '-losses', '-average_position', 'wins', 'win_rate'
    ).first()

    most_regular_player = all_players.order_by(
        'average_position', '-wins', '-win_rate'
    ).first()

    best_wr_player = (
        all_players.filter(games__gt=0)
        .order_by('-win_rate', '-wins', 'average_position')
        .first()
    )

    most_golds = Player.objects.aggregate(most_golds=Max('wins')).get('most_golds')
    most_golds_names = ' & '.join(
        Player.objects.filter(wins=most_golds)
        .order_by('name')
        .values_list('name', flat=True)
    )

    most_silvers = (
        PlayerInGame.objects.filter(position=2)
        .values('player__name')
        .annotate(num_silvers=Count('player__name'))
        .aggregate(most_silvers=Max('num_silvers'))
        .get('most_silvers')
    )
    most_silvers_names = ' & '.join(
        PlayerInGame.objects.filter(position=2)
        .values('player__name')
        .annotate(num_silvers=Count('player__name'))
        .filter(num_silvers=most_silvers)
        .order_by('player__name')
        .values_list('player__name', flat=True)
    )

    achievements = {
        'best_wr': {
            'player_name': best_wr_player.name,
            'value': best_wr_player.win_rate,
            'number_of_games': best_wr_player.games.count(),
        },
        'best_average': {
            'player_name': most_regular_player.name,
            'value': most_regular_player.average_position,
        },
        'most_golds': {
            'player_name': most_golds_names,
            'value': most_golds,
        },
        'most_silvers': {
            'player_name': most_silvers_names,
            'value': most_silvers,
        },
        'most_losses': {
            'player_name': most_losses_player.name,
            'value': most_losses_player.losses,
        },
        'best_win_streak': {
            'player_name': best_win_streak['player_name'],
            'value': best_win_streak['value'],
        },
        'worst_loss_streak': {
            'player_name': worst_loss_streak['player_name'],
            'value': worst_loss_streak['value'],
        },
    }

    return achievements
