from django.contrib import admin, messages
from django.http import HttpResponseRedirect

from .models import (
    Expansion,
    ExpansionInGame,
    Game,
    Image,
    Player,
    PlayerInGame,
    Record,
)

admin.site.register(Expansion)
admin.site.register(ExpansionInGame)
admin.site.register(Image)
admin.site.register(Player)
admin.site.register(PlayerInGame)
admin.site.register(Record)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    change_form_template = "website/admin/change_form.html"

    def response_change(self, request, obj):
        if "_finalize" in request.POST:
            try:
                obj.finalize()
            except Exception as err:
                self.message_user(request, err, level=messages.ERROR)
            else:
                obj.save()
                self.message_user(request, "Game has been finalized!")
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)
