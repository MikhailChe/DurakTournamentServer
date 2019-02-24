import logging
from typing import Dict
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
        game_id = uuid4()
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


game_manager = GameManager.get_instance()

game_ = Game()
players = {uuid4(), uuid4()}
game_.start(players)
test_game_id = game_manager.add_game(game_)
logger.info('Here are game players: %s', game_.players)
logger.info('Test game id %s', test_game_id)
logger.info('Game state: %s', game_)
