import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime

from .basemodel import BaseModel
from .jsonencodedtype import JSONEncodedStruct
from .uuidtype import UUIDBin


class Match(BaseModel):
    __tablename__ = 'match'

    match_id = mapped_column(UUIDBin, primary_key=True)
    player1_id: Mapped[int] = mapped_column(ForeignKey('player.player_id', ondelete='CASCADE'))
    player2_id: Mapped[int] = mapped_column(ForeignKey('player.player_id', ondelete='CASCADE'))
    winner_id: Mapped[int | None] = mapped_column(ForeignKey('player.player_id', ondelete='CASCADE'))
    match_score = mapped_column(JSONEncodedStruct)
    creation_date = mapped_column(DateTime, default=datetime.datetime.now)

    player1 = relationship('Player', foreign_keys=[player1_id])
    player2 = relationship('Player', foreign_keys=[player2_id])
    winner = relationship('Player', foreign_keys=[winner_id])
