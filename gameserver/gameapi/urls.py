from django.urls import path

import gameapi.views
import gameapi.tournament.views

urlpatterns = [

    path('tournament/list', gameapi.tournament.views.get_tournaments_list, name='get_tournaments_list'),
    path('tournament/register', gameapi.tournament.views.register_in_tournament, name='register_in_tournament'),

    path('get_games_list/', gameapi.views.get_games_list, name='get_games_list'),

    path('play/<uuid:game_id>/get_state/', gameapi.views.get_state, name='get_game_state'),
    path('play/<uuid:game_id>/take_action/', gameapi.views.take_action, name='take_game_action')
]
