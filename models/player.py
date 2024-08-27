from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


from .basemodel import BaseModel


class Player(BaseModel):
    __tablename__ = 'player'

    player_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()


