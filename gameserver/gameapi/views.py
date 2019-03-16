import logging
import ujson

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest

from gameapi.game.models import Game, Card
from gameapi.games_manager import game_manager
from gameapi.helpers.auth import token_auth, game_auth
from gameapi.models import Token

# Create your views here.

logger = logging.getLogger(__name__)


@token_auth
def get_games_list(request: HttpRequest, token: Token = None):
    logger.debug('/my_games_list handler %s %s', request, token)
    if token is None:
        return HttpResponseBadRequest()
    games = list(map(str, game_manager.list_games(token.token)))
    logger.debug('Games: %s', games)
    return HttpResponse(
        content=ujson.dumps(games)
    )


@token_auth
@game_auth
def get_state(request: HttpRequest, game: Game = None, token: Token = None):
    logger.debug('/get_state handler')
    if game is None or token is None:
        return HttpResponseBadRequest()
    state = game.get_state(token.token)
    logger.debug(state)
    return HttpResponse(
        content=ujson.dumps(state),
    )


@game_auth
def take_action(request: HttpRequest, game: Game, token: Token):
    logger.debug('/take_action handler')
    if 'action' not in request.GET:
        return HttpResponseBadRequest('No action provided')
    action_str = request.GET['action']
    card_str = request.GET.get(key='card', default=None)

    uuid = token.token
    action = Game.Action(action_str)
    card = Card.from_string(card_str) if card_str else None
    action_accepted = True
    try:
        game.take_action(uuid, action, card)
    except Game.ActionNotAllowed:
        logger.warning(
            'Action not allowed  %s %s',
            action, token,
        )
        action_accepted = False
    except Game.ActionInvalid:
        logger.warning(
            'Action invalid %s %s',
            action, token,
        )
        action_accepted = False

    new_state = game.get_state(uuid)
    new_state.update({
        'action_accepted': action_accepted,
    })
    logger.debug(new_state)
    return HttpResponse(content=ujson.dumps(new_state))
