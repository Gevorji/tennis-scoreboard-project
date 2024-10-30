import argparse
import random
import sys
from uuid import uuid4
import os.path
import os

from sqlalchemy import create_engine, URL, select
from sqlalchemy.orm import sessionmaker
from dotenv import dotenv_values

from models import Player, Match
from services.tests.tools import get_player_id_by_name, get_db_url

os.environ.update(
    dotenv_values(os.path.abspath(os.path.join(os.path.dirname(__file__), '..\.env')))
)

engine = create_engine(get_db_url())
Session = sessionmaker(engine)

players = [
    Player(name='Carlos Alcaraz'),
    Player(name='Manuel Alonso'),
    Player(name='Felicisimo Ampon'),
]

match_score_fields = {
    'metadata': {'n_sets': 3},
    'current_set': {
        'p1_gm_score': 0,
        'p2_gm_score': 0,
        'games': []
    },
    'serve': 1,
    'sets': [],
    'winner': None
}

match_score_fields = {
    'metadata': {'n_sets': 3},
    'current_set': {
        'p1_gm_score': 0,
        'p2_gm_score': 0,
        'games': []
    },
    'serve': 1,
    'sets': [],
    'winner': None
}


def get_rand_players_pair():
    with Session() as session:
        pl_ids = session.execute(select(Player.player_id)).scalars().all()
    return random.sample(pl_ids, 2)


def generate_match():
    pl_1_id, pl_2_id = get_rand_players_pair()
    return Match(
        match_id=uuid4(),
        player1_id=pl_1_id,
        player2_id=pl_2_id,
        winner_id=None,
        match_score=match_score_fields.copy()
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-matchesn', default=0, type=int)
    parser.add_argument('--insert-players', '-inspl', default=False, type=bool)
    args = parser.parse_args(sys.argv[1:])

    with Session.begin() as session:
        if args.insert_players:
            session.add_all(players)

        for i in range(args.matchesn):
            session.add(generate_match())
