import unittest
import os
import uuid
from copy import deepcopy

from sqlalchemy import create_engine, URL, select, delete, and_, or_, bindparam
from sqlalchemy.orm import Session, sessionmaker, aliased
from dotenv import dotenv_values

env_path = os.path.join(os.path.dirname(__file__), '.env')
os.environ.update(dotenv_values(env_path))

from models import Player, Match
from services.data_storage import DataStorageService
from tools import get_player_id_by_name, get_db_url

service = DataStorageService(sql_echo=True)

engine = create_engine(get_db_url(), echo=True, isolation_level='READ COMMITTED')

session = Session(engine)


class DataStorageTest(unittest.TestCase):

    def test_getPlayerByName(self):
        player = service.get_player_by_name('Carlos Alcaraz')
        self.assertEquals(player.name, 'Carlos Alcaraz')

    def test_getMatchesByPlayerName(self):
        matches = service.get_matches_by_player_name('Manuel Alonso')
        self.assertIsNotNone(matches)

    def test_getMatchByUuid(self):
        p1, p2 = aliased(Player), aliased(Player)
        _id = session.execute(
            select(Match.match_id)
            .join(p1, Match.player1)
            .join(p2, Match.player2)
            .where(and_(p1.name == 'Carlos Alcaraz', p2.name == 'Manuel Alonso'))
        ).scalars().first()
        self.assertIsNotNone(service.get_match_by_uuid(_id))

    def test_getAllPlayers(self):
        self.assertIsNotNone(service.get_all_players())

    def test_getAllMatches(self):
        self.assertIsNotNone(service.get_all_matches())

    def test_putMatch(self):
        player1_id = session.get(Player, get_player_id_by_name(session, 'Manuel Alonso')).player_id
        player2_id = session.get(Player, get_player_id_by_name(session, 'Felicisimo Ampon')).player_id
        _id = uuid.uuid4()
        new_match = Match(match_id=_id, player1_id=player1_id, player2_id=player2_id)

        service.put_match(new_match)

        self.assertIsNotNone(session.execute(select(Match).where(Match.match_id == _id)).scalars().one_or_none())

        session.execute(delete(Match).where(Match.match_id == _id))
        session.commit()

    def test_putPlayer(self):
        new_player = Player(name='Playful Player')

        service.put_player(new_player)

        self.assertIsNotNone(session.execute(
            select(Player)
            .where(Player.name == new_player.name)
        ).scalars().one_or_none())

        session.execute(delete(Player).where(Player.player_id == new_player.player_id))
        session.commit()

    def test_deleteMatch(self):
        player1 = session.get(Player, get_player_id_by_name(session, 'Manuel Alonso'))
        player2 = session.get(Player, get_player_id_by_name(session, 'Felicisimo Ampon'))
        id_for_deletion = uuid.uuid4()
        new_match = Match(match_id=id_for_deletion, player1=player1, player2=player2)
        session.add(new_match)
        session.commit()

        self.assertIsNotNone(session.get(Match, id_for_deletion))

        service.delete_match(id_for_deletion)

        self.assertIsNone(
            session.execute(select(Match).where(Match.match_id == id_for_deletion)).scalars().one_or_none()
        )

    def test_deletePlayer(self):
        new_player = Player(name='Playful Player')

        session.execute(delete(Player).where(Player.name == new_player.name))

        session.add(new_player)
        session.commit()

        self.assertIsNotNone(new_player.player_id)

        id_for_deletion = new_player.player_id

        service.delete_player(id_for_deletion)

        self.assertIsNone(
            session.execute(select(Player).where(Player.player_id == id_for_deletion)).scalars().one_or_none()
        )

    def test_updateMatchScore(self):
        match = session.execute(select(Match).limit(1)).scalar_one()
        session.expunge(match)

        old_score = deepcopy(match.match_score)
        match.match_score['current_set']['p1_gm_score'] += 1

        service.update_match_score(match.match_id, match.match_score)

        match = session.get(Match, match.match_id)

        self.assertEqual(
            match.match_score['current_set']['p1_gm_score'], old_score['current_set']['p1_gm_score'] + 1
        )

        match.match_score = old_score
        session.commit()
