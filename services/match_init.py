# Service creates a new match instance.
# Also stores a meta info (number of sets, tiebreaks allowed and any other rules that affects the game)
# inside a match score attribute
import uuid
from random import choice

from models import Match, Player
from services.data_storage import DataStorageService
from services.singleton import singleton
from services.errors import ApplicationError

GAME_CONFIGURATION = {
    'match_metadata': {
        'n_sets': 3
    }
}


@singleton
class MatchInitializationService:

    def __init__(self, game_configuration: dict):
        self._game_configuration = game_configuration
        self.data_storage = DataStorageService()

    def create_new_match(self, player1: str | Player, player2: str | Player):
        player1_id, player2_id = self._fetch_player_ids(player1, player2)

        new_match = Match(
            match_id=uuid.uuid4(),
            player1_id=player1_id, player2_id=player2_id,
            match_score={
                'current_set': {
                  'p1_gm_score': 0,
                  'p2_gm_score': 0,
                  'games': [],
                  'tiebreak': False,
                  'deuce': False,
                },
                'metadata': self.get_match_score_metadata(),
                'sets': [],
                'finished': False,
                'serve': choice([1, 2]),
                'winner': None
            }
        )

        return new_match

    def _fetch_player_ids(self, player1: str | Player, player2: str | Player):
        from_strs = {n: self.data_storage.get_player_by_name(p) for n, p in enumerate((player1, player2)) if
                     type(p) is str}
        model_objs = {n: p for n, p in enumerate((player1, player2)) if type(p) is Player}
        model_objs.update(from_strs)

        names_unexist = [{0: player1, 1: player2}[k] for k in (0, 1) if model_objs.get(k) is None]
        names_unexist = [{True: p.name, False: p}[type(p) is Player] for p in names_unexist]

        if names_unexist:
            raise ApplicationError(f'No such player(s) in database: {", ".join(names_unexist)}')

        return tuple(model_objs[p].player_id for p in model_objs)

    def get_match_score_metadata(self):
        return self._game_configuration['match_metadata'].copy()
