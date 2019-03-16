import logging
import uuid

from django.db import models
from django.utils import timezone

from gameapi.models import Token

logger = logging.getLogger(__name__)


class Tournament(models.Model):
    class RegistrationFinished(Exception):
        pass

    class InvalidState(Exception):
        pass

    token = models.UUIDField(default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    players = models.ManyToManyField(Token)
    registration_finishes_at = models.DateTimeField(null=True, blank=True)
    tournament_finished_at = models.DateTimeField(null=True, blank=True)

    @property
    def regestration_finished(self) -> bool:
        return self.registration_finishes_at < timezone.now()

    @property
    def tournament_finished(self) -> bool:
        return self.tournament_finished_at is not None


class GameSeries(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.DO_NOTHING)
    players = models.ManyToManyField(Token)
    current_game = models.UUIDField()
    games_in_series = models.IntegerField(default=10)


class GameResult(models.Model):
    game_series = models.ForeignKey(GameSeries, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)


class PlayerResult(models.Model):
    game_result = models.ForeignKey(GameResult, on_delete=models.DO_NOTHING)
    player = models.ForeignKey(Token, on_delete=models.DO_NOTHING)
    winner = models.BooleanField()
