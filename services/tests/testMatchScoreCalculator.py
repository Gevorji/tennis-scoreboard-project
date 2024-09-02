# tests:
# 1. game doesn't end:
#   - game 0:0 set 0:0 p1
#   - game 30:30 set 0:0 p2
#   - game 40:40 set 0:0 p1
#   - game less:more set 0:0 p1
# 2. game ends:
#   - game 40:0 set 0:0 p1
#   - game less:more set 0:0 p2
# 3. set doesn't end:
#   - game 15:0 set 0:0 p1
#   - game 40:0 set 5:5 p1
#   - game 40:0 set 1:3 p1
#   - tiebreak 3:4 set 6:6 p1
#   - tiebreak 6:7 set 6:6 p1
# 4. set ends:
#   - game 30:40 set 4:5 p2
#   - tiebreak 5:6 set 6:6 p2
# 5. deuce starts:
#   - game 30:40 set 0:0 p1
# 6. tiebreak starts:
#   - game 0:40 set 6:5 p2
# 7. match ends:
#   - game more:less set 6:5 sets 1:1
#   - game 30:40 set 5:6 sets 0:1
#   - tiebreak 7:6 set 5:1 sets 1:1
# 8. clean match calculation:
#   - match score without current set p1
# 9. Various player specifications: 1, 2, '1', '2', 'player1', 'player2'

import unittest

from services.match_score_calc import MatchScoreCalculationService

score_calculator = MatchScoreCalculationService()

MATCH_METADATA = {'n_sets': 3}

GAME_DOESNT_END_TESTCASES = [
    (
        {
            'current_set': {'p1_gm_score': 0, 'p2_gm_score': 0, 'games': []},
            'sets': [],
            'metadata': MATCH_METADATA.copy()
        }, 1
    ),
    (
        {
            'current_set': {'p1_gm_score': 2, 'p2_gm_score': 2, 'games': []},
            'sets': [],
            'metadata': MATCH_METADATA.copy()
        }, 2
    ),
    (
        {
            'current_set': {'p1_gm_score': 3, 'p2_gm_score': 3, 'games': []},
            'sets': [],
            'metadata': MATCH_METADATA.copy()
        }, 1
    ),
    (
        {
            'current_set': {'p1_gm_score': 3, 'p2_gm_score': 4, 'games': []},
            'sets': [],
            'metadata': MATCH_METADATA.copy()
        }, 1
    ),
]

GAME_ENDS_TESTCASES = [
    (
        {
            'current_set': {'p1_gm_score': 3, 'p2_gm_score': 0, 'games': []},
            'sets': [],
            'metadata': MATCH_METADATA.copy()
        }, 1
    ),
    (
        {
            'current_set': {'p1_gm_score': 3, 'p2_gm_score': 4, 'games': []},
            'sets': [],
            'metadata': MATCH_METADATA.copy()
        }, 2
    ),
]


class MatchScoreCalculationServiceTest(unittest.TestCase):

    def test_gameDoesntEnd(self):
        for testcase in GAME_DOESNT_END_TESTCASES:
            mscore, point_winner = testcase
            p1_score, p2_score = mscore["current_set"]['p1_gm_score'], mscore["current_set"]['p2_gm_score']
            games_list = mscore['current_set']['games']
            games_played = len(games_list)
            with self.subTest(
                    game_score=f'{p1_score}:{p2_score}', sets=f'{", ".join(g["winner"] for g in games_list)}'
            ):
                score_calculator.calculate(mscore, point_winner)
                self.assertEqual(len(games_list), games_played)

    def test_gameEnds(self):
        for testcase in GAME_ENDS_TESTCASES:
            mscore, point_winner = testcase
            p1_score, p2_score = mscore["current_set"]['p1_gm_score'], mscore["current_set"]['p2_gm_score']
            games_list = mscore['current_set']['games']
            games_played = len(games_list)
            with self.subTest(
                    game_score=f'{p1_score}:{p2_score}', sets=f'{", ".join(g["winner"] for g in games_list)}'
            ):
                score_calculator.calculate(mscore, point_winner)
                self.assertEqual(len(games_list), games_played+1)
