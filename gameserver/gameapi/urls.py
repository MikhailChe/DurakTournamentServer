from django.urls import path

import gameapi.views

urlpatterns = [
    path('<uuid:game_id>/get_state/', gameapi.views.get_state, name='get_state'),
    path('<uuid:game_id>/take_action/', gameapi.views.take_action, name='take_action')
]
