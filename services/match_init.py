# Service creates a new match instance.
# Also stores a meta info (number of sets, tiebreaks allowed and any other rules that affects the game)
# inside a match score attribute

from models import Match, Player


class MatchInitializationService:

    def __init__(self, game_configuration: dict):
        self._game_configuration = game_configuration

    def create_new_match(self, player1_name, player2_name):
        new_match = Match(
            player1=Player(name=player1_name), player2=Player(name=player2_name),
            match_score={
                'metadata': self.get_match_score_metadata(),
                'sets': [],
                'finished': False
            }
        )

        return new_match

    def get_match_score_metadata(self):
        return self._game_configuration

