import os

from sqlalchemy import create_engine, URL, select
from sqlalchemy.orm import Session

from models import Player, Match

def get_player_id_by_name(session: Session, name: str):
   return session.execute(select(Player.player_id).where(Player.name == name)).scalar_one()

def get_db_url():
    return URL.create(
    drivername='+'.join(filter(None, (os.getenv("DB_DBMS_NAME"), os.getenv('DB_DRIVER')))),
    username=os.environ.get('DB_USERNAME'),
    password=os.environ.get('DB_USER_PASSWORD'),
    host=os.environ.get('DB_HOST'),
    port=int(os.environ.get('DB_PORT')),
    database=os.environ.get('DB_DB_NAME'),
).render_as_string(hide_password=False)
