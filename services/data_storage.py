import os
import uuid
from typing import Collection, List

from jinja2.nodes import Tuple
from sqlalchemy import create_engine, URL, select, delete, or_, update, bindparam, literal_column
from sqlalchemy.orm import aliased, sessionmaker, selectinload
from sqlalchemy import func as safunc

from models import Player, Match
from services.singleton import singleton


@singleton
class DataStorageService:

    def __init__(self, *, sql_echo=False):
        connection_url = URL.create(
            drivername='+'.join(filter(None, (os.getenv("DB_DBMS_NAME"), os.getenv('DB_DRIVER')))),
            username=os.environ.get('DB_USERNAME'),
            password=os.environ.get('DB_USER_PASSWORD'),
            host=os.environ.get('DB_HOST'),
            port=int(os.environ.get('DB_PORT')),
            database=os.getenv('DB_DB_NAME'),
        )
        self._sa_engine = create_engine(connection_url.render_as_string(hide_password=False), echo=sql_echo)
        self._sessionmaker = sessionmaker(self._sa_engine, expire_on_commit=False)

    def commit(self):  # ensures that commit statement is emitted
        self._sa_session.commit()

    def get_player_by_name(self, name: str):
        with self._sessionmaker() as session:
            return session.execute(select(Player).where(Player.name == name)).scalars().one_or_none()

    def get_matches_by_player_name(self, name: str):
        p1, p2 = aliased(Player), aliased(Player)
        with self._sessionmaker() as session:
            return session.execute(
                select(Match)
                .join(p1, Match.player1)
                .join(p2, Match.player2)
                .where(or_(p1.name == name, p2.name == name))
            ).scalars().all()

    def get_match_by_uuid(self, _uuid: uuid.UUID):
        with self._sessionmaker() as session:
            return session.execute(select(Match)
                                   .options(
                selectinload(Match.player1), selectinload(Match.player2), selectinload(Match.winner)
            )
                                   .where(Match.match_id == _uuid)).scalars().one_or_none()

    def get_all_players(self):
        with self._sessionmaker() as session:
            return session.execute(select(Player)).scalars().all()

    def get_all_matches(self):
        with self._sessionmaker() as session:
            return session.execute(
                select(Match)
                .options(selectinload(Match.player1), selectinload(Match.player2), selectinload(Match.winner))
            ).scalars().all()

    def get_all_players_names(self):
        with self._sessionmaker() as session:
            return session.execute(select(Player.name)).scalars().all()

    def put_match(self, match: Match):
        with self._sessionmaker.begin() as session:
            session.merge(match)

    def put_player(self, player: Player):
        with self._sessionmaker.begin() as session:
            session.merge(player)

    def delete_match(self, match_uuid: uuid.UUID):
        with self._sessionmaker.begin() as session:
            session.execute(delete(Match).where(Match.match_id == match_uuid))

    def delete_player(self, player_id: int):
        with self._sessionmaker.begin() as session:
            session.execute(delete(Player).where(Player.player_id == player_id))

    def update_match_score(self, match_id: uuid.UUID, score: dict):
        with self._sessionmaker.begin() as session:
            session.execute(
                update(Match).where(Match.match_id == bindparam('id')).values(match_score=score),
                {'id': match_id}
            )

    def count_matches(self, player_name_filter: str = None, *, finished: bool = False, ongoing=False):

        p1, p2 = aliased(Player), aliased(Player)
        stmt = select(safunc.count('*')) \
            .select_from(Match).join(p1, Match.player1_id == p1.player_id) \
            .join(p2, Match.player2_id == p2.player_id)
        if player_name_filter:
            stmt = stmt.where(or_(p1.name == player_name_filter, p2.name == player_name_filter))

        if finished != ongoing:  # either both state filters set to true or false, it counts all objects
            if finished:
                stmt = stmt.where(Match.winner != None)
            if ongoing:
                stmt = stmt.where(Match.winner == None)

        with self._sessionmaker() as session:
            return session.execute(stmt).scalar_one()

    def get_matches_in_creation_ord(
            self, player_name_filter: str | Collection = None,
            *, slboundaries: List | Tuple = None, order: str = 'ascending', enumed=False,
            finished: bool = False, ongoing=False
    ):
        assert order in ['ascending', 'descending'], 'Proper values for order parameter is ascending/descending'

        bot_boundary = top_boundary = None
        if slboundaries:
            assert len(slboundaries) <= 2, 'Given more than 2 boundaries'
            assert not bool(list(filter(lambda itm: itm < 0 or not type(itm) is int,
                                        slboundaries))), 'Boundaries should be positive integers'
            bot_boundary = slboundaries[0]
            if len(slboundaries) == 2:
                top_boundary = slboundaries[1]

        order_by = {'ascending': Match.creation_date.asc(), 'descending': Match.creation_date.desc()}[order]
        p1, p2 = aliased(Player), aliased(Player)
        stmt = select(safunc.row_number().over(order_by=order_by).label('no'), Match.match_id) \
               .join(p1, p1.player_id == Match.player1_id) \
               .join(p2, p2.player_id == Match.player2_id)
        if player_name_filter:
            stmt = stmt.where(or_(p1.name == player_name_filter, p2.name == player_name_filter))
        if finished != ongoing: # either both state filters set to true or false, it fetches all objects
            if finished:
                stmt = stmt.where(Match.winner != None)
            if ongoing:
                stmt = stmt.where(Match.winner == None)
        cte = stmt.cte()
        cte = aliased(Match, cte)

        stmt = select(literal_column('no'), Match)\
            .options(selectinload(Match.player1), selectinload(Match.player2), selectinload(Match.winner))\
            .join_from(Match, cte, Match.match_id == cte.match_id)

        if bot_boundary:
            stmt = stmt.where(literal_column('no') >= bindparam('bb'))
        if top_boundary:
            stmt = stmt.where(literal_column('no') <= bindparam('tb'))

        with self._sessionmaker() as session:
            res = session.execute(stmt, {'bb': bot_boundary, 'tb': top_boundary}).fetchall()

        if enumed:
            return res
        return [row[1] for row in res]

