from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from .basemodel import BaseModel


class Match(BaseModel):
    __tablename__ = 'match'

    match_id: Mapped[int] = mapped_column(primary_key=True)
    player1_id: Mapped[int] = mapped_column(ForeignKey('player.player_id'))
    player2_id: Mapped[int] = mapped_column(ForeignKey('player.player_id'))
    winner_id: Mapped[int | None] = mapped_column(ForeignKey('player.player_id'))

    player1 = relationship('Player', foreign_keys=[player1_id])
    player2 = relationship('Player', foreign_keys=[player2_id])
    winner = relationship('Player', foreign_keys=[winner_id])
