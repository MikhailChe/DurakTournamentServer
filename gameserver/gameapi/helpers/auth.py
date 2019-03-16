import logging
from uuid import UUID

from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest, HttpResponseNotFound

from gameapi.game.models import Game
from gameapi.games_manager import DoesNotExist, game_manager
from gameapi.models import Token

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
