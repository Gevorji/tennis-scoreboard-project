import os

from dotenv import load_dotenv

from .match_init import (MatchInitializationService as _MatchInitializationService,
                        GAME_CONFIGURATION)
from .player_init import PlayerInitializationService as _PlayerInitializationService
from .data_storage import DataStorageService as _DataStorageService
from .match_score_calc import MatchScoreCalculationService as _MatchScoreCalculationService

load_dotenv()

MatchInitializationService = _MatchInitializationService(GAME_CONFIGURATION)
PlayerInitializationService = _PlayerInitializationService()
DataStorageService = _DataStorageService()
MatchScoreCalculationService = _MatchScoreCalculationService()
