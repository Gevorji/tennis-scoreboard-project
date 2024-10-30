# service receives: dictionary that represents match score
from services.singleton import singleton


@singleton
class MatchScoreCalculationService:

    _valid_player_specs = {'1': 1, '2': 2, 1: 1, 2: 2, 'player1': 1, 'player2': 2}

    def calculate(self, ms: dict, point_won_by):
        if ms.get('winner'):
            return
        self._start_calculation(ms, point_won_by)
        score_record = {1: 'p1_gm_score', 2: 'p2_gm_score'}[self._point_won_by]
        self._current_set[score_record] += 1

        if self._is_finished_game():
            self._wrap_up_game(self._point_won_by)
            self._start_new_game()
        elif self._is_deuce_condition():
            self._start_deuce()
        elif self._is_advantage_condition():
            self._start_advantage()

        if self._is_finished_set():
            self._wrap_up_set(self._point_won_by)
            if self._is_match_ended():
                self._wrap_up_match(self._point_won_by)
            else:
                self._start_new_set()
        elif self._is_tiebreak_start_condition():
            self._start_tiebreak()
        self._define_serve()

    def _start_calculation(self, ms: dict, point_won_by: str | int):
        self._calc_ms = ms

        if point_won_by not in self._valid_player_specs:
            raise AssertionError(
                f'Player was specified inappropriately (valid: {", ".join(repr(i) for i in self._valid_player_specs)}'
            )

        self._point_won_by = self._valid_player_specs[point_won_by]

        if 'current_set' not in self._calc_ms:
            self._start_new_set()
        else:
            self._current_set = self._calc_ms['current_set']

    def _start_new_set(self):
        self._current_set = self._calc_ms['current_set'] = {
            'p1_gm_score': 0,
            'p2_gm_score': 0,
            'deuce': False,
            'games': [],
            'tiebreak': False
        }

    def _start_new_game(self):
        self._current_set.update(
            {
                'p1_gm_score': 0,
                'p2_gm_score': 0,
                'deuce': False
            }
        )

    def _start_deuce(self):
        self._current_set['deuce'] = True

    def _start_advantage(self):
        self._current_set['deuce'] = False

    def _start_tiebreak(self):
        self._current_set.update(
            {
                'p1_gm_score': 0,
                'p2_gm_score': 0,
                'deuce': False,
                'tiebreak': True
            }
        )

    def _is_finished_game(self):
        if self._current_set.get('tiebreak'):
            return False
        p1, p2 = self._current_set['p1_gm_score'], self._current_set['p2_gm_score']
        pw_score = {1: p1, 2: p2}[self._point_won_by]

        if abs(p1-p2) >= 2:
            if self._current_set.get('deuce') or pw_score > 3:
                return True
        else:
            return False

    def _is_deuce_condition(self):
        curr_set = self._current_set
        if curr_set['p1_gm_score'] == curr_set['p2_gm_score'] >= 3 and not curr_set.get('tiebreak'):
            return True
        return False

    def _is_advantage_condition(self):
        p1, p2 = self._current_set['p1_gm_score'], self._current_set['p2_gm_score']
        if p1 >= 3 and p2 >= 3 and abs(p1-p2) == 1:
            return True
        return False

    def _is_finished_set(self):
        p1w, p2w = self._count_games_won(self._current_set)
        if p1w == p2w == 0:
            return False

        if self._current_set.get('tiebreak'):
            p1, p2 = self._current_set['p1_gm_score'], self._current_set['p2_gm_score']
            pw_score = {1: p1, 2: p2}[self._point_won_by]
            if abs(p1-p2) >= 2 and pw_score >= 7:
                return True

        if abs(p1w-p2w) >= 2 and (p1w >= 6 or p2w >= 6):
            return True
        else:
            return False

    def _is_tiebreak_start_condition(self):
        if self._current_set.get('tiebreak'):
            return False
        p1w, p2w = self._count_games_won(self._current_set)
        if p1w == p2w == 6:
            return True

    def _is_match_ended(self):
        p1sw, p2sw = self._count_sets_won(self._calc_ms)
        sets_left = self._calc_ms['metadata']['n_sets'] - p1sw - p2sw
        if sets_left == 0 or abs(p1sw - p2sw) > sets_left:
            return True
        return False

    def _wrap_up_game(self, winner):
        self._current_set['games'].append({'winner': winner})

    def _wrap_up_set(self, winner):
        self._calc_ms['sets'].append({'winner': winner, 'games': self._current_set['games']})

    def _wrap_up_match(self, winner):
        self._calc_ms['winner'] = winner

    def _define_serve(self):
        cs = self._calc_ms['current_set']
        game_sum = cs['p1_gm_score'] + cs['p2_gm_score']
        if cs.get('tiebreak'):
            if game_sum in [0, 1] or game_sum % 2 != 0:
                self._swap_serve()
        else:
            self._swap_serve()

    def _swap_serve(self):
        if self._calc_ms['serve'] == 1:
            self._calc_ms['serve'] = 2
        else:
            self._calc_ms['serve'] = 1

    @staticmethod
    def _count_games_won(_set):
        games = _set['games']
        wins = [g['winner'] for g in games]
        return wins.count(1), wins.count(2)

    @staticmethod
    def _count_sets_won(match):
        sets = match['sets']
        wins = [s['winner'] for s in sets]
        return wins.count(1), wins.count(2)

