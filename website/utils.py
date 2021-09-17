from django.db.models import Count
from .models import Game, Player, PlayerInGame


def get_achievements():
    all_games = Game.objects.filter(finalised=True)
    all_players = Player.objects.all()
    all_players_in_game = PlayerInGame.objects.all()

    streak_data = {
        player.name: {
            'current_win_streak': 0,
            'max_win_streak': 0,
            'current_loss_streak': 0,
            'max_loss_streak': 0,
        }
        for player in all_players
    }
    previous_winner = None
    previous_loser = None

    for game in all_games:
        winner = game.game_players.order_by('-score').first().player.name
        if (
            winner == previous_winner
            or streak_data[winner]['current_win_streak'] == 0  # noqa: W503
        ):
            streak_data[winner]['current_win_streak'] += 1
            if (
                streak_data[winner]['current_win_streak']
                > streak_data[winner]['max_win_streak']  # noqa: W503
            ):
                streak_data[winner]['max_win_streak'] += 1
        else:
            streak_data[winner]['current_win_streak'] = 1

        previous_winner = winner

        loser = game.game_players.order_by('score').first().player.name
        if (
            loser == previous_loser
            or streak_data[loser]['current_loss_streak'] == 0  # noqa: W503
        ):
            streak_data[loser]['current_loss_streak'] += 1
            if (
                streak_data[loser]['current_loss_streak']
                > streak_data[loser]['max_loss_streak']  # noqa: W503
            ):
                streak_data[loser]['max_loss_streak'] += 1
        else:
            streak_data[loser]['current_loss_streak'] = 1

        previous_loser = loser

    max_win_streak = 0
    max_loss_streak = 0

    for streak_values in streak_data.values():
        if streak_values['max_win_streak'] > max_win_streak:
            max_win_streak = streak_values['max_win_streak']
        if streak_values['max_loss_streak'] > max_loss_streak:
            max_loss_streak = streak_values['max_loss_streak']

    win_streak_names = []
    loss_streak_names = []

    for name, streak_values in streak_data.items():
        if streak_values['max_win_streak'] == max_win_streak:
            win_streak_names.append(name)
        if streak_values['max_loss_streak'] == max_loss_streak:
            loss_streak_names.append(name)

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

    most_golds_player = (
        all_players_in_game.filter(position=1)
        .values('player__name', 'position')
        .annotate(num_golds=Count('id'))
        .order_by('-num_golds', '-player__win_rate')
        .first()
    )

    most_silvers_player = (
        all_players_in_game.filter(position=2)
        .values('player__name', 'position')
        .annotate(num_silvers=Count('id'))
        .order_by('-num_silvers', 'player__average_position', '-player__win_rate')
        .first()
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
            'player_name': most_golds_player['player__name'],
            'value': most_golds_player['num_golds'],
        },
        'most_silvers': {
            'player_name': most_silvers_player['player__name'],
            'value': most_silvers_player['num_silvers'],
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
