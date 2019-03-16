from django.urls import path

import gameapi.views

urlpatterns = [
    path('my_games_list/', gameapi.views.get_games_list, name='my_games_list'),

    path('play/<uuid:game_id>/get_state/', gameapi.views.get_state, name='get_state'),
    path('play/<uuid:game_id>/take_action/', gameapi.views.take_action, name='take_action')
]
