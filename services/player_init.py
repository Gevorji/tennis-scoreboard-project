import re

from models import Player
from services.singleton import singleton
from services.errors import NameIsNotValidError, NameIsTooLongError


@singleton
class PlayerInitializationService:
    _valid_name_pattern = re.compile(r'( ?\w+ ?)+')
    _name_len = 25

    def create_new_player(self, name: str):
        name = self._process_name(name)
        if not self._is_valid_name(name):
            raise NameIsNotValidError(
                'Invalid player name. Name can contain only letters (a-z), digits (0-9) and an underscore'
            )
        if not self._is_approp_namelen(name):
            raise NameIsTooLongError(f'Player name is too long. Required length is {self._name_len} characters')
        new_player = Player(name=name)
        return new_player

    def _is_valid_name(self, name: str):
        if re.fullmatch(self._valid_name_pattern, name):
            return True
        return False

    def _is_approp_namelen(self, name):
        if len(name) <= self._name_len:
            return True

    @staticmethod
    def _process_name(name):
        return ' '.join(name.split())
