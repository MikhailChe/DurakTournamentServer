import logging
import ujson
from uuid import UUID

from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound

from gameapi.games_manager import DoesNotExist, game_manager
from gameapi.models import Card, Game, Token

# Create your views here.

logger = logging.getLogger(__name__)


def token_auth(fn):
    def token_auth_wrapper(request, *args, **kwargs):
        try:
            token_str = request.GET['token']
        except KeyError:
            return HttpResponseBadRequest('No token provided')
        try:
            token = check_token_exists(token_str)
            if token is None:
                return HttpResponseBadRequest('Token  invalid')
        except Token.DoesNotExist:
            return HttpResponseBadRequest('Token  invalid')
        kwargs.update({'token': token})
        logger.debug('token_auth: Calling with arguments: %s %s', args, kwargs)
        return fn(request, *args, **kwargs)

    return token_auth_wrapper


def game_auth(fn):
    def game_auth_wrapper(request, game_id, *args, **kwargs):
        try:
            game = check_game_id(game_id)
        except DoesNotExist:
            return HttpResponseNotFound('Game does not exist')

        try:
            token = kwargs['token']
        except KeyError:
            return HttpResponseBadRequest('No token provided. Maybe you should use token_auth decorator')

        if not check_token_in_game(game, token.token):
            logger.warning('Token is not part of this game. (%s not in %s)', token, game.players)
            return HttpResponseBadRequest('Token is not part of this game.')

        kwargs.update({'game': game})
        return fn(request, *args, **kwargs)

    return game_auth_wrapper


def check_game_id(game_id: UUID):
    return game_manager.get_game(game_id)


def check_token_exists(token: str):
    try:
        return Token.objects.get(token=token)
    except ValidationError:
        return None


def check_token_in_game(game: Game, token: Token):
    return token in game.players


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
