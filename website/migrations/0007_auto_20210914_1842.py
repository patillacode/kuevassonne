# Generated by Django 3.2.5 on 2021-09-14 16:42

from django.db import migrations, models


def add_average_position_and_losses_values(apps, schema_editor):

    Player = apps.get_model('website', 'Player')
    PlayerInGame = apps.get_model('website', 'PlayerInGame')
    Game = apps.get_model('website', 'Game')

    db_alias = schema_editor.connection.alias
    all_games = Game.objects.using(db_alias).all()

    for game in all_games:
        players_in_game = game.game_players.all()

        min_points = min(list(players_in_game.values_list('score', flat=True)))
        losers = players_in_game.filter(score=min_points)
        for loser in losers:
            loser.player.losses += 1
            loser.player.save()

    for data in (
        PlayerInGame.objects.all()
        .values('player')
        .annotate(average=models.Avg('position'))
    ):
        player = Player.objects.get(pk=data['player'])
        player.average_position = round(data['average'], 2)
        player.save()


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0006_auto_20210913_1756'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='average_position',
            field=models.FloatField(blank=True, help_text='Average position', null=True),
        ),
        migrations.AddField(
            model_name='player',
            name='losses',
            field=models.IntegerField(default=0),
        ),
        migrations.RunPython(add_average_position_and_losses_values),
    ]
