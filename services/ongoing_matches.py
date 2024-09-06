import uuid


class OngoingMatchesManagingService:
    def __init__(self):
        self._ongoing_matches = {}

    def register_match(self, item):
        self._ongoing_matches[uuid.uuid4().int] = item

    def get_match_by_uuid(self, identity: str | int | bytes):
        init_args = {{'str': 'hex', 'int': 'int', 'bytes': 'bytes'}[type(identity).__name__]: identity}
        return self._ongoing_matches[uuid.UUID(**init_args).int]

    def get_all_matches(self):
        return tuple(self._ongoing_matches.values())
