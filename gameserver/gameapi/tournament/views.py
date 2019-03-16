import logging
import ujson

from django.http import HttpRequest, HttpResponseBadRequest, HttpResponse

from gameapi.helpers.auth import token_auth
from gameapi.models import Token
from gameapi.tournament.models import Tournament

logger = logging.getLogger(__name__)


def get_tournaments_list(request: HttpRequest):
    logger.debug('/get_tournaments_list handler %s', request)
    tournaments = filter(lambda t: t.registration_finished == False, Tournament.objects.all())
    return HttpResponse(
        content=ujson.dumps(tournaments)
    )


@token_auth
def register_in_tournament(request: HttpRequest, token: Token = None):
    logger.debug('/register_in_tournament handler %s %s', request, token)
    if token is None:
        return HttpResponseBadRequest()
    if 'tournament' not in request.GET:
        return HttpResponseBadRequest('No tournament id provided')
    tournament_str = request.GET['tournament']
    tournament = Tournament.objects.get(id=tournament_str)
    tournament.register(token)
    return HttpResponse(
        content=ujson.dumps({
            'status': 'ok',
        })
    )
