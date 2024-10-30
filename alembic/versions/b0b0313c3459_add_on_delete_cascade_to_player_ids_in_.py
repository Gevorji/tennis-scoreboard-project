"""add on delete cascade to player ids in match table

Revision ID: b0b0313c3459
Revises: 30021dbfa880
Create Date: 2024-10-07 21:00:12.134813

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b0b0313c3459'
down_revision: Union[str, None] = '30021dbfa880'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('match_ibfk_2', 'match', type_='foreignkey')
    op.drop_constraint('match_ibfk_1', 'match', type_='foreignkey')
    op.drop_constraint('match_ibfk_3', 'match', type_='foreignkey')
    op.create_foreign_key(None, 'match', 'player', ['player2_id'], ['player_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'match', 'player', ['player1_id'], ['player_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'match', 'player', ['winner_id'], ['player_id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'match', type_='foreignkey')
    op.drop_constraint(None, 'match', type_='foreignkey')
    op.drop_constraint(None, 'match', type_='foreignkey')
    op.create_foreign_key('match_ibfk_3', 'match', 'player', ['winner_id'], ['player_id'])
    op.create_foreign_key('match_ibfk_1', 'match', 'player', ['player1_id'], ['player_id'])
    op.create_foreign_key('match_ibfk_2', 'match', 'player', ['player2_id'], ['player_id'])
    # ### end Alembic commands ###
