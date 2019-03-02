import logging
from operator import itemgetter
from typing import Dict, List
from uuid import uuid4, UUID

from gameapi.models import Game, Token

logger = logging.getLogger(__name__)


class DoesNotExist(Exception):
    pass


class GameManager(object):
    DoesNotExist = DoesNotExist
    _instance = None

    def __init__(self):
        self.games: Dict[UUID, Game] = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def add_game(self, game: Game):
        game_id = UUID('1111-1111-1111-1111-1111-1111-1111-1111')
        self.games[game_id] = game
        return game_id

    def get_game(self, game_id: UUID) -> Game:
        """
        Get game from game manager

        :raises DoesNotExist: if game is not registered in game manager
        """
        logger.info('Getting game with game_id = %s', game_id)
        try:
            return self.games[game_id]
        except KeyError:
            logger.exception(
                'Game "%s" doesnt exist. Existing games: %s',
                game_id,
                self.games.keys()
            )
            raise DoesNotExist('Game with id "%s" doesnt exist' % game_id)

    def list_games(self, user_id: UUID) -> List[UUID]:
        """
        List games that user_id is in
        """
        return [game_id for game_id, game in self.games.items() if user_id in game.players]


game_manager = GameManager.get_instance()

try:
    game_ = Game()
    tokens = list(map(itemgetter('token'), Token.objects.filter(valid=True).values('token')[:2]))
    players = set(tokens)
    game_.start(players)
    test_game_id = game_manager.add_game(game_)
    logger.info('Here are game players: %s', game_.players)
    logger.info('Test game id %s', test_game_id)
    logger.info('Game state: %s', str(game_.field))
except Exception:
    pass
