# Create your models here.
import datetime
import logging
import random
import uuid
from enum import Enum
from typing import Dict, List, Set

from django.contrib.auth.models import User
from django.db import models

logger = logging.getLogger(__name__)


class Token(models.Model):
    token = models.UUIDField(default=uuid.uuid4)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    issued_at = models.DateTimeField(auto_now_add=True)
    valid = models.BooleanField(default=True)
    invalidated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return ' '.join([
            ('[ VALID ]' if self.valid else '[INVALID]'),
            self.owner.username,
            (str(self.token)[:6] + '...'),
        ])


class TokenAccessLog(models.Model):
    token = models.ForeignKey(Token, on_delete=models.CASCADE)
    access_time = models.DateTimeField()


class Card(object):
    class Suit(Enum):
        SPADES = 'S'
        CLUBS = 'C'
        DIAMONDS = 'D'
        HEARTS = 'H'

    def __init__(self, value: int, suit: Suit):
        if value < 6 or value > 14:
            raise ValueError('Card value incorrect %s', value)
        self.value: int = value
        self.suit: Card.Suit = suit

    @classmethod
    def from_string(cls, card_str):
        if card_str is None:
            raise ValueError('Card string is None')
        if len(card_str) < 2:
            raise ValueError('Incorrect card format: too short')
        card_value_str = card_str[:-1]
        card_suit_str = card_str[-1]
        return cls(int(card_value_str), Card.Suit(card_suit_str))

    def card_value_str(self):
        human_names = {
            11: 'Jack',
            12: 'Queen',
            13: 'King',
            14: 'Ace',
        }
        if self.value in human_names:
            return human_names[self.value]
        else:
            return str(self.value)

    def __str__(self):
        return self.card_value_str()[0] + self.suit.name[0]

    def __repr__(self):
        return (
            self.__class__.__qualname__ + '[' +
            ', '.join(map(repr, self.__dict__.items())) +
            ']'
        )

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return other.value == self.value and other.suit == self.suit

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.value, self.suit))


class GameField(object):
    def __init__(self):
        self.player_cards: Dict[uuid.UUID, Set[Card]] = {}
        self.deck: List[Card] = []
        self.trump: Card = None
        self.table: List[List[Card]] = []
        self.leftover: Set[Card] = []
        self.seed = None

    def randomize_game(self, players: Set[uuid.UUID], seed=None):
        """
        Game initializer
        """
        if not len(players) == 2:
            raise ValueError(
                'Illegal number of players for game %d (%s)' % (
                    len(players),
                    players
                )
            )
        if seed is None:
            seed = random.getrandbits(128)
        self.seed = seed
        logger.info('Seeding game field with %d', seed)
        random.seed(seed)

        all_cards: List[Card] = [Card(value, suit) for value in range(6, 15, 1) for suit in Card.Suit]
        while all_cards:
            card = random.choice(all_cards)
            all_cards.remove(card)
            self.deck.append(card)
        for player in players:
            player_cards: Set[Card] = set()
            while len(player_cards) < 6:
                player_cards.add(self.deck.pop())
            self.player_cards[player] = player_cards
        # TODO: modify for 3+ users game
        self.trump = self.deck[0]
        return self

    def get_state(self, token):
        return {
            'cards': self.player_cards[token],
            'field_cards': self.table,
            'deck_counter': len(self.deck),
            'trump': self.trump,
            'enemy_cards_counter': sum(
                map(
                    len,
                    map(
                        lambda k: self.player_cards[k],
                        filter(
                            lambda k: not k == token, self.player_cards.keys()
                        )
                    )
                )
            )
        }

    def __str__(self):
        return (
            self.__class__.__qualname__ + '[\n' +
            ',\n'.join(map(lambda s: '    ' + s, [
                'deck: [' + ','.join(map(str, self.deck)) + ']',
                'trump: ' + str(self.trump),
                'player_cards: {' + '; '.join(
                    [str(token) + ':' + ','.join(map(str, cards)) for token, cards in self.player_cards.items()]
                ) + '}',
                'table: [' + ', '.join(
                    ['(' + ','.join(map(str, cards)) + ')' for cards in self.table]
                ) + ']',
            ])) +
            '\n]'
        )

    def __repr__(self):
        return (
            self.__class__.__qualname__ + '[' +
            ', '.join(map(repr, self.__dict__.items())) +
            ']'
        )

    def get_player_with_least_trump_suit(self):
        trump = self.trump
        trump_suit = trump.suit
        players_trumps = {
            player:
                list(map(lambda card: card.value,
                         filter(lambda card: card.suit == trump_suit, cards)
                         )
                     )
            for player, cards in self.player_cards.items()
        }
        global_minima = None
        minimal_trump_player = None
        for player in players_trumps:
            try:
                min_ = min(players_trumps[player])
                if global_minima is None or min_ < global_minima:
                    global_minima = min_
                    minimal_trump_player = player
            except ValueError:
                pass
        return minimal_trump_player


class Game(object):
    class ActionNotAllowed(Exception):
        pass

    class ActionInvalid(Exception):
        pass

    class NoPlayersActive(Exception):
        pass

    class Action(Enum):
        PUT = 'put'
        TAKE = 'take'
        ENDTURN = 'endturn'

    def __init__(self):
        self.number_of_moves: int = 0
        self.number_of_turns: int = 0
        self.field: GameField = GameField()
        self.players: List[uuid.UUID] = []
        self.active_player: uuid.UUID = None
        self.defending_player: uuid.UUID = None
        self.winners: Set[uuid.UUID] = None
        self.seed: int = None
        self.started_at = None

    def __repr__(self):
        return self.__class__.__qualname__ + '[' + ', '.join(
            map(repr, self.__dict__.items())
        ) + ']'

    def is_action_allowed(self, token: uuid.UUID, action: Action):
        attacking_actions = [Game.Action.PUT, Game.Action.ENDTURN]
        defending_actions = [Game.Action.PUT, Game.Action.TAKE]
        if not token == self.active_player:
            return False
        if self.is_attacking(token):
            return action in attacking_actions
        return action in defending_actions

    def is_action_valid(self, token: uuid.UUID, action: Action, card: Card):
        """
        Assumes that **`action`** is allowed
        """
        if action == Game.Action.PUT:
            if card not in self.field.player_cards[token]:
                return False
            return self.can_put_card(token, card)
        elif action == Game.Action.ENDTURN:
            return self.can_end_turn(token)
        elif action == Game.Action.TAKE:
            return self.can_take(token)
        return False

    def can_put_card(self, token: uuid.UUID, card: Card):
        if self.is_attacking(token):
            return self.can_attack_with(card)
        else:
            return self.can_defend_with(card)

    def is_defending(self, token):
        return self.defending_player == token

    def is_attacking(self, token):
        return not self.is_defending(token)

    def can_attack_with(self, card: Card):
        cards_on_table = {card for pair in self.field.table for card in pair}

        if not cards_on_table:
            return True

        set_of_card_values_on_table = {card.value for card in cards_on_table}
        if card.value in set_of_card_values_on_table:
            return True
        return False

    def can_defend_with(self, card: Card):
        attacking_pair: List[Card] = next(filter(lambda pair: len(pair) == 1, self.field.table), None)
        if attacking_pair is None:
            raise Exception('Could not find attacking pair card: %s, game: %s' % (card, self))
        attacking_card: Card = attacking_pair[0]

        if attacking_card.suit == card.suit:
            return attacking_card.value < card.value
        return card.suit == self.field.trump.suit

    def can_end_turn(self, token: uuid.UUID):
        return self.is_attacking(token)

    def can_take(self, token: uuid.UUID):
        return self.is_defending(token)

    def take_action(self, token: uuid.UUID, action: Action, card: Card):
        # TODO: not implemented
        if not self.is_action_allowed(token, action):
            raise Game.ActionNotAllowed('Action not allowed %s %s' % (token, action))
        if not self.is_action_valid(token, action, card):
            raise Game.ActionInvalid('Action invalid %s %s %s' % token, action, card)
        if action == Game.Action.PUT:
            self.put_card_on_table(token, card)
        elif action == Game.Action.TAKE:
            self.take_table_cards(token)
            self.equalize_players_cards()
            # TODO: modify switch_turns for 3+ users game
        elif action == Game.Action.ENDTURN:
            self.throw_cards()
            self.equalize_players_cards()
            self.switch_turns()
        self.detect_gameover()
        self.number_of_moves += 1

    def put_card_on_table(self, token: uuid.UUID, card: Card):
        active_card_pair = next(filter(lambda pair: len(pair) == 1, self.field.table), None)
        if active_card_pair is None:
            active_card_pair = []
            self.field.table.append(active_card_pair)
        self.field.player_cards[token].remove(card)
        active_card_pair.append(card)

    def take_table_cards(self, token):
        for pair in self.field.table:
            for card in pair:
                self.field.player_cards[token].add(card)
        self.field.table.clear()

    def throw_cards(self):
        for pair in self.field.table:
            for card in pair:
                self.field.leftover.add(card)
        self.field.table.clear()

    def equalize_players_cards(self):
        # TODO: modify for 3+ users game
        attacking_players = set(self.players) - {self.defending_player}
        for token in attacking_players:
            player = self.field.player_cards[token]
            while len(player) < 6:
                if len(self.field.deck) == 0:
                    break
                # TODO: take cards in coorect order (trump should be last)
                player.add(self.field.deck.pop())
        defending_player = self.field.player_cards[self.defending_player]
        while len(defending_player) < 6:
            if len(self.field.deck) == 0:
                break
            defending_player.add(self.field.deck.pop())

    def switch_turns(self):
        index = self.players.index(self.defending_player)
        new_index = (index + 1) % len(self.players)
        self.active_player = self.defending_player
        self.defending_player = self.players[new_index]

        self.number_of_turns += 1

    def detect_gameover(self):
        if len(self.field.deck) == 0 and (
            # TODO: modify for 3+ user games
            any(
                map(
                    lambda player, cards: len(cards) == 0,
                    filter(
                        lambda player, cards: not player == self.defending_player,
                        self.field.player_cards.items()
                    )
                )
            )
        ):
            if len(self.field.player_cards[self.defending_player]) != 0:
                self.winners = {player for player in self.players}
            self.active_player = None
            self.defending_player = None
            return True
        return False

    def is_over(self):
        # TODO: not implemented
        return self.active_player is None

    def get_result(self, token):
        """
        return None if game is not finished
        return winer , looser or draw for token if game is over
        :param token:
        :return:
        """
        if not self.is_over():
            return None
        if not self.winners:
            return 'draw'
        return 'winner' if token in self.winners else 'looser'

    def get_state(self, token):
        return {
            'game_field': self.field.get_state(token),
            'actions_available': list(map(
                lambda action: action.value,
                filter(
                    lambda action: self.is_action_allowed(token, action),
                    (action for action in Game.Action)
                )
            )
            ),
            # ['put', 'endturn', 'take'],
            'game_state': {
                'status': self.is_over(),
                'number_of_turns': self.number_of_turns,
                'number_of_moves': self.number_of_moves,
                'result': self.get_result(token)
            }
        }

    def start(self, players: Set[uuid.UUID], last_winners: Set[uuid.UUID] = None, seed=None):
        if seed is None:
            seed = random.getrandbits(128)
        random.seed(seed)
        logger.info('Seeding whole game with %s', seed)
        self.seed = seed
        if last_winners is None:
            last_winners = set()
        self.field.randomize_game(set(players), seed=seed)
        self.players = list(players)
        self.active_player = self.select_starting_player(set(players), last_winners)
        self.defending_player = self.select_defending_player(self.active_player)
        self.started_at = datetime.datetime.utcnow()
        return self

    def select_starting_player(self, players: Set[uuid.UUID], last_winners: Set[uuid.UUID]):
        choose_from = players & last_winners
        if choose_from:
            return random.sample(choose_from, 1)[0]
        return self.field.get_player_with_least_trump_suit()

    def select_defending_player(self, active_player):
        active_index = self.players.index(active_player)
        defending_index = (active_index + 1) % len(self.players)
        return self.players[defending_index]
