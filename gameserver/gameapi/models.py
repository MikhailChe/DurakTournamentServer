# Create your models here.
from django.contrib.auth.models import User
from django.db import models


class Token(models.Model):
    token = models.UUIDField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    issued_at = models.DateTimeField()
    valid = models.BooleanField()
    invalidated_at = models.DateTimeField()


class TokenAccessLog(models.Model):
    token = models.ForeignKey(Token, on_delete=models.CASCADE)
    access_time = models.DateTimeField()


class GameField(object):
    def __init__(self):
        self.player_cards = {}
        self.deck = []
        self.trump = None
        self.table = []
        self.leftover = []

    def randomize_game(self):
        """
        Game initializer
        """
        # TODO: not implemented
        pass

    def take_action(self, token, actiontype, card):
        # TODO: not implemented
        pass

    def get_state(self, token):
        # TODO: not implemented
        pass


class ActionNotAllowed(Exception):
    pass


class ActionInvalid(Exception):
    pass


class Game(object):
    ActionNotAllowed = ActionNotAllowed
    ActionInvalid = ActionInvalid

    def __init__(self):
        self.number_of_moves = 0
        self.number_of_turns = 0
        self.players = []
        self.field = GameField()
        self.active_player = None

    def action_valid(self, token, action, card):
        # TODO: not implemented
        return False

    def is_over(self):
        # TODO: not implemented
        return True

    def take_action(self, token, action_str, card_str):
        # TODO: not implemented
        pass

    def get_result(self, token):
        """
        return None if game is not finished
        return win , loose or draw for token if game is over
        :param token:
        :return:
        """
        # TODO: not implemented
        pass
