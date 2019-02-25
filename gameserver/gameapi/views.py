import logging
import ujson
from uuid import UUID

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound

# Create your views here.
from gameapi.games_manager import DoesNotExist, game_manager
from gameapi.models import Game, Token, Card

logger = logging.getLogger(__name__)


def game_auth(fn):
    def game_auth_wrapper(request, game_id, *args, **kwargs):
        try:
            game = check_game_id(game_id)
        except DoesNotExist:
            return HttpResponseNotFound('Game does not exist')
        try:
            token_str = request.GET['token']
        except KeyError:
            return HttpResponseBadRequest('No token provided')
        try:
            token = check_token_exists(token_str)
        except Token.DoesNotExist:
            return HttpResponseBadRequest('Token invalid')

        if not check_token_in_game(game, token.token):
            logger.warning('Token is not part of this game. (%s not in %s)', token, game.players)
            return HttpResponseBadRequest('Token is not part of this game.')
        return fn(request, *args, game=game, token=token, **kwargs)

    return game_auth_wrapper


def check_game_id(game_id: UUID):
    return game_manager.get_game(game_id)


def check_token_exists(token: str):
    return Token.objects.get(token=token)


def check_token_in_game(game: Game, token: Token):
    return token in game.players


@game_auth
def get_state(request: HttpRequest, game: Game, token: Token):
    logger.debug('/get_state handler')
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
