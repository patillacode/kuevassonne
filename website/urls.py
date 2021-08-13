from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # path('login/', views.login_user, name='login'),
    path('games/', views.games, name='games'),
    path('create/player/', views.create_player, name='create_player'),
    path('create/game/', views.create_game, name='create_game'),
    path(
        'create/expansions/<int:game_id>/',
        views.create_expansions_in_game,
        name='create_expansions_in_game',
    ),
    path(
        'create/players/<int:game_id>/',
        views.create_players_in_game,
        name='create_players_in_game',
    ),
    path('finalize/<int:game_id>/', views.finalize, name='finalize'),
    path('game/<int:game_id>/', views.game_info, name='game_info'),
    path('in_game/<int:game_id>/', views.in_game, name='in_game'),
    path('players/', views.players, name='players'),
    path('records/', views.records, name='records'),
    path('add_record/', views.add_record, name='add_record'),
]
