from django.contrib import admin

from .models import Expansion, ExpansionInGame, Game, Image, Player, PlayerInGame

admin.site.register(Expansion)
admin.site.register(ExpansionInGame)
admin.site.register(Game)
admin.site.register(Image)
admin.site.register(Player)
admin.site.register(PlayerInGame)
