from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import or_, UniqueConstraint

from typing import List

from .basemodel import BaseModel
from .match import Match


class Player(BaseModel):
    __tablename__ = 'player'

    player_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    matches: Mapped[List[Match]] = relationship(
        Match, primaryjoin=or_(Match.player1_id == player_id, Match.player2_id == player_id), viewonly=True
    )

