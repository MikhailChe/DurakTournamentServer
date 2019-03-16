import logging
import threading
from datetime import timedelta, datetime
from itertools import product
from uuid import UUID

from django.utils import timezone

from gameapi.game.models import Game
from gameapi.games_manager import game_manager
from gameapi.models import GameSeries, Tournament, Token

logger = logging.getLogger(__name__)


class TournamentManager(object):
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def new_tournament(self):
        return Tournament(registration_finishes_at=timezone.now() + timedelta(hours=1))

    def get_active_tournaments(self):
        return filter(lambda t: not t.regestration_finished, Tournament.objects.all())

    def create_tournament_game_series(self, tournament: Tournament):
        for player1, player2 in product(tournament.players, repeat=2):
            if player1 == player2:
                continue
            players = {player1, player2}
            game_series = GameSeries(tournament=tournament, players=players)
            game_series.save()

    def register(self, tournament: Tournament, token: Token):
        if tournament.regestration_finished:
            raise Tournament.RegistrationFinished(
                'Cannnot register token. Finished at %s' %
                tournament.registration_finishes_at

            )
        tournament.players.add(token)

    def stop_tournament(self, tournament: Tournament):
        if not tournament.tournament_finished_at:
            raise Tournament.InvalidState('Registration must be finished before finishing tournament')
        tournament.registration_finished_at = timezone.now()


tournament_manager = TournamentManager.get_instance()

lock = threading.Lock()


class GameSeriesManager(object):
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_or_create_game(self, game_series: GameSeries) -> UUID:
        with lock:
            if game_series.current_game is None:
                game = Game()
                tokens = {player.token for player in game_series.players.all()}
                game.start(tokens)
                return game_manager.add_game(game)
            else:
                last_game = game_manager.get_game(game_series.current_game)
                game = Game()
                tokens = {player.token for player in game_series.players.all()}
                game.start(tokens, last_winners=last_game.winners)
                return game_manager.add_game(game)


game_series_manager = GameSeriesManager.get_instance()
