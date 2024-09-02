# service receives: dictionary that represents match score


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
        elif self._is_deuce_condition():
            self._start_deuce()

        if self._is_finished_set():
            self._wrap_up_set(self._point_won_by)
            if self._is_match_ended():
                self._wrap_up_match(self._point_won_by)
            else:
                self._start_new_set()
        elif self._is_tiebreak_condition():
            self._start_tiebreak()
        else:
            self._start_new_game()

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
        self._start_new_game()

    def _start_new_game(self):
        self._current_set['games'].append(
            {'winner': None}
        )

    def _start_deuce(self):
        self._current_set['deuce'] = True

    def _start_tiebreak(self):
        self._current_set['tiebreak'] = True

    def _is_finished_game(self):
        if self._current_set.get('tiebreak'):
            return False
        p1, p2 = self._current_set['p1_gm_score'], self._current_set['p1_gm_score']

        if abs(p1-p2) == 2:
            if self._current_set['deuce'] or (p1 > 3 or p2 > 3):
                return True
        else:
            return False

    def _is_deuce_condition(self):
        curr_set = self._current_set
        if curr_set['p1_gm_score'] == curr_set['p1_gm_score'] >= 3 and not curr_set.get('tiebreak'):
            return True

    def _is_finished_set(self):
        p1w, p2w = self._count_games_won(self._current_set)
        if p1w == p2w == 0:
            return False

        if self._current_set.get('tiebreak'):
            p1, p2 = self._current_set['p1_gm_score'], self._current_set['p2_gm_score']
            if abs(p1-p2) == 2 and (p1 >= 7 or p2 >= 7):
                return True

        if abs(p1w-p2w) == 2 and (p1w >= 6 or p2w >= 6):
            return True
        else:
            return False

    def _is_tiebreak_condition(self):
        p1w, p2w = self._count_games_won(self._current_set)
        if p1w == p2w == 6:
            return True

    def _is_match_ended(self):
        if len(self._calc_ms['sets']) == self._calc_ms['metadata']['n_sets']:
            return True
        return False

    def _wrap_up_game(self, winner):
        self._current_set['games'][-1]['winner'] = winner

    def _wrap_up_set(self, winner):
        self._calc_ms['sets'].append({'winner': winner, 'games': self._current_set['games']})

    def _wrap_up_match(self, winner):
        self._calc_ms['winner'] = winner

    @staticmethod
    def _count_games_won(_set):
        games = _set['games'][:-2] if not _set.get('winner') else _set['games']
        wins = [g['winner'] for g in games]
        return wins.count(1), wins.count(2)

    @staticmethod
    def _count_sets_won(match):
        sets = match['sets'][:-2] if not match.get('winner') else match['sets']
        wins = [s['winner'] for s in sets]
        return wins.count(1), wins.count(2)

