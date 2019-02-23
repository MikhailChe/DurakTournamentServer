import ujson
from uuid import UUID

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound

# Create your views here.
from gameapi.games_manager import DoesNotExist, game_manager
from gameapi.models import Game, Token


def game_auth(fn):
    def game_auth_wrapper(request, game_id, *args, **kwargs):
        try:
            game = check_game_id(game_id)
        except DoesNotExist:
            return HttpResponseNotFound('Game does not exist %s' % (game_id,))
        try:
            token_str = request.GET['token']
        except KeyError:
            return HttpResponseBadRequest('No token provided')
        try:
            token = check_token_exists(token_str)
        except Token.DoesNotExist:
            return HttpResponseBadRequest('Token invalid')

        if not check_token_in_game(game, token):
            return HttpResponseBadRequest('Token is not part of this game')
        return fn(request, game=game, token=token, *args, **kwargs)

    return game_auth_wrapper


def generate_state(game: Game, token: Token):
    reference_dict = {
        "action_accepted": False,
        "actions_available": ["put", "endturn", "take"],
        "game_field": {
            "cards": ["6C", "7H"],
            "field_cards": game.field.table,
            "deck_counter": len(game.field.deck),
            "trump": game.field.trump,
            "enemy_cards_counter": 6
        },
        "game_state": {
            "status": game.is_over(),
            "number_of_turns": game.number_of_turns,
            "number_of_moves": game.number_of_moves,
            "result": game.get_result(token)
        }
    }
    return ujson.dumps(reference_dict)


def check_game_id(game_id: UUID):
    return game_manager.get_game(game_id)


def check_token_exists(token: str):
    return Token.objects.get(token=token)


def check_token_in_game(game: Game, token: Token):
    return token in game.players


@game_auth
def get_state(request: HttpRequest, game: Game, token: Token = None):
    return HttpResponse(
        content=generate_state(game, token),
    )


@game_auth
def take_action(request: HttpRequest, game: Game, token: Token = None):
    action_str = request.GET['action']
    card_str = request.GET['card']
    try:
        game.take_action(token, action_str, card_str)
    except Game.ActionNotAllowed:
        return HttpResponseBadRequest('Action not allowed')
    except Game.ActionInvalid as e:
        return HttpResponseBadRequest('Action invalid %s', e)

    return HttpResponse(conten=generate_state(game, token))
