from django.db import models
from django.conf import settings
from enum import Enum
import pytz


class Color(Enum):
    RED = 'Red'
    BLUE = 'Blue'
    YELLOW = 'Yellow'
    PINK = 'Pink'
    GREEN = 'Green'
    BLACK = 'Black'

    def __str__(self):
        return self.name


class Image(models.Model):
    image = models.ImageField(default=None)
    name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name or self.image.name


class Expansion(models.Model):
    name = models.CharField(max_length=255)
    release_year = models.IntegerField()
    is_mini = models.BooleanField(default=False)
    number_of_tiles = models.IntegerField(default=0)
    games = models.ManyToManyField(
        'Game', through='ExpansionInGame', blank=True, related_name='expansions'
    )

    def __str__(self):
        return self.name


class Player(models.Model):
    name = models.CharField(max_length=64)
    wins = models.IntegerField(default=0)
    win_rate = models.FloatField(
        blank=True, null=True, help_text='Percentage of games won'
    )
    games = models.ManyToManyField(
        'Game', through='PlayerInGame', blank=True, related_name='players'
    )

    def __str__(self):
        return self.name


class Game(models.Model):
    start_date = models.DateTimeField('datetime game started')
    end_date = models.DateTimeField('datetime game ended', blank=True, null=True)

    # players = models.ManyToManyField(PlayerInGame)
    # expansions = models.ManyToManyField(ExpansionInGame)

    total_time = models.IntegerField(
        help_text='Number of seconds the game lasted for.', blank=True, null=True
    )
    avg_seconds_per_turn = models.IntegerField(
        help_text='Number of seconds of the average turn.', blank=True, null=True
    )
    total_number_of_tiles = models.IntegerField(blank=True, null=True)

    images = models.ManyToManyField(Image, blank=True)
    winner = models.ForeignKey(Player, on_delete=models.CASCADE, blank=True, null=True)

    finalised = models.BooleanField(default=False)

    def __str__(self):
        date = self.start_date.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime(
            '%Y-%m-%d %H:%M'
        )
        return f'Partida {self.id} ({date})'

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

        players_in_game = PlayerInGame.objects.filter(game=self)
        if not players_in_game:
            raise Exception('There are no players in this game. Weird...')

        self.total_time = (self.end_date - self.start_date).total_seconds()
        self.avg_seconds_per_turn = (
            self.total_time
            / players_in_game.count()  # noqa: W503
            / self.total_number_of_tiles  # noqa: W503
        )

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
            player.win_rate = (player.wins / games_played) * 100
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
            )
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

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['expansion', 'game'], name='expansion_only_once_per_game'
            )
        ]

    def __str__(self):
        return f'Partida {self.game.id} - {self.expansion.name}'

    def calculate_tiles_for_game(self):
        # after adding an expansion (where its tiles were used) to a game
        # we recalculate the number of tiles for that game
        number_of_tiles = 0
        for expansion_used_in_game in ExpansionInGame.objects.filter(game=self.game):
            if expansion_used_in_game.use_tiles:
                number_of_tiles += expansion_used_in_game.expansion.number_of_tiles

        self.game.total_number_of_tiles = number_of_tiles
        self.game.save()

    def save(self, *args, **kwargs):
        if not self.id:
            super().save(*args, **kwargs)

        self.calculate_tiles_for_game()
        super().save(*args, **kwargs)
