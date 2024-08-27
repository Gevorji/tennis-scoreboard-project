from sqlalchemy.orm import Mapped, mapped_column, relationship


from .basemodel import BaseModel


class Match(BaseModel):
    __tablename__ = 'match'

    match_id: Mapped[int] = mapped_column(primary_key=True)
    player1: Mapped[str] = relationship('player')
    player2: Mapped[str] = relationship('player')
    winner: Mapped[str] = relationship('player')
