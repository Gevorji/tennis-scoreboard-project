"""Initial state

Revision ID: 30021dbfa880
Revises: 
Create Date: 2024-09-15 16:12:01.210864

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from models import uuidtype, jsonencodedtype

# revision identifiers, used by Alembic.
revision: str = '30021dbfa880'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('player',
    sa.Column('player_id', sa.Integer(), nullable=False),
    sa.Column('name', mysql.VARCHAR(length=64), nullable=False),
    sa.PrimaryKeyConstraint('player_id')
    )
    op.create_index(op.f('ix_player_name'), 'player', ['name'], unique=True)
    op.create_table('match',
    sa.Column('match_id', uuidtype.UUIDBin(length=16), nullable=False),
    sa.Column('player1_id', sa.Integer(), nullable=False),
    sa.Column('player2_id', sa.Integer(), nullable=False),
    sa.Column('winner_id', sa.Integer(), nullable=True),
    sa.Column('match_score', jsonencodedtype.JSONEncodedStruct(), nullable=True),
    sa.ForeignKeyConstraint(['player1_id'], ['player.player_id'], ),
    sa.ForeignKeyConstraint(['player2_id'], ['player.player_id'], ),
    sa.ForeignKeyConstraint(['winner_id'], ['player.player_id'], ),
    sa.PrimaryKeyConstraint('match_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('match')
    op.drop_index(op.f('ix_player_name'), table_name='player')
    op.drop_table('player')
    # ### end Alembic commands ###