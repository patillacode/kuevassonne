import datetime
from enum import Enum

import pytz
from django.conf import settings
from django.db import models


class Color(Enum):
    RED = 'Red'
    BLUE = 'Blue'
    YELLOW = 'Yellow'
    PINK = 'Pink'
    GREEN = 'Green'
    BLACK = 'Black'

    def __str__(self):
        return self.name


class Expansion(models.Model):
    name = models.CharField(max_length=255, unique=True)
    release_year = models.IntegerField()
    is_mini = models.BooleanField(default=False)
    number_of_tiles = models.IntegerField(default=0)
    games = models.ManyToManyField(
        'Game', through='ExpansionInGame', blank=True, related_name='expansions'
    )

    def __str__(self):
        return self.name


class Player(models.Model):
    name = models.CharField(max_length=64, unique=True)
    wins = models.IntegerField(default=0)
    win_rate = models.FloatField(
        blank=True, null=True, help_text='Percentage of games won'
    )
    games = models.ManyToManyField(
        'Game', through='PlayerInGame', blank=True, related_name='players'
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = ''.join(self.name.split())
        super().save(*args, **kwargs)


class Game(models.Model):
    start_date = models.DateTimeField('datetime game started')
    end_date = models.DateTimeField('datetime game ended', blank=True, null=True)

    duration = models.CharField(max_length=9, blank=True, null=True)

    total_time = models.IntegerField(
        help_text='Number of seconds the game lasted for.', blank=True, null=True
    )
    avg_seconds_per_turn = models.IntegerField(
        help_text='Number of seconds of the average turn.', blank=True, null=True
    )
    total_number_of_tiles = models.IntegerField(blank=True, null=True)

    image = models.ImageField(blank=True)
    winner = models.ForeignKey(Player, on_delete=models.CASCADE, blank=True, null=True)

    finalised = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} ({self.date})'

    @property
    def name(self):
        return f'Partida {self.id}'

    @property
    def date(self):
        return self.start_date.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime(
            '%Y-%m-%d'
        )

    @property
    def podium(self):
        podium = {}
        for player in self.game_players.all().order_by('position')[:3]:
            podium[player.player.name] = {
                'score': player.score,
                'color': player.color.lower(),
            }
        return podium

    @property
    def winner_points(self):
        return PlayerInGame.objects.get(game=self, player=self.winner).score

    def calculate_tiles_for_game(self):
        # after adding an expansion (where its tiles were used) to a game
        # we recalculate the number of tiles for that game
        number_of_tiles = 0
        for expansion_used_in_game in self.game_expansions.all():
            if expansion_used_in_game.use_tiles:
                number_of_tiles += expansion_used_in_game.expansion.number_of_tiles

        self.total_number_of_tiles = number_of_tiles
        self.save()

    def finalize(self):
        # calculate some data for the game

        if self.finalised:
            raise Exception(
                'This game has already been finalised, you need to '
                'access the admin to amend any errors.'
            )

        if not self.end_date:
            raise Exception(
                'Game doesn\'t seem to have an end date and time. Please set the '
                '"end_date" before finalising a game.'
            )

        players_in_game = self.game_players.filter(game=self).order_by('-score')
        if not players_in_game:
            raise Exception('There are no players in this game. Weird...')

        self.total_time = (self.end_date - self.start_date).total_seconds()
        self.duration = str(datetime.timedelta(seconds=self.total_time)).split(".")[0]
        self.avg_seconds_per_turn = self.total_time / self.total_number_of_tiles

        # set some data for the players too
        max_points = 0
        for player_in_game in players_in_game:
            if player_in_game.score > max_points:
                self.winner = player_in_game.player
                max_points = player_in_game.score

        self.winner.wins += 1
        self.winner.save()

        for player_in_game in players_in_game:
            player = player_in_game.player
            games_played = player.games.all().count()
            player.win_rate = round((player.wins / games_played) * 100, 2)
            player.save()

        for position, player_in_game in enumerate(
            PlayerInGame.objects.filter(game=self).order_by('-score'), 1
        ):
            player_in_game.position = position
            player_in_game.save()

        self.finalised = True
        self.save()


class PlayerInGame(models.Model):
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name='player_games'
    )
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='game_players')
    score = models.IntegerField(default=0)
    position = models.IntegerField(default=0)
    color = models.CharField(
        max_length=7, choices=[(tag.name, tag.value) for tag in Color]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['player', 'game'], name='player_only_once_per_game'
            ),
            models.UniqueConstraint(
                fields=['color', 'game'], name='color_only_once_per_game'
            ),
        ]

    def __str__(self):
        return f'Partida {self.game.id} - {self.player.name}'


class ExpansionInGame(models.Model):
    expansion = models.ForeignKey(
        Expansion, on_delete=models.CASCADE, related_name='expansion_games'
    )
    game = models.ForeignKey(
        Game, on_delete=models.CASCADE, related_name='game_expansions'
    )
    use_rules = models.BooleanField()
    use_tiles = models.BooleanField(default=True)

    def __str__(self):
        return f'Partida {self.game.id} - {self.expansion.name}'


class Image(models.Model):
    image = models.ImageField(default=None)
    name = models.CharField(max_length=255, blank=True, null=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='game_images')

    def __str__(self):
        return self.name or self.image.name


class Record(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(default=None)
    description = models.TextField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='game_records')
