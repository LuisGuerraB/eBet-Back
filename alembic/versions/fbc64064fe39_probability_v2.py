"""Probability v2

Revision ID: fbc64064fe39
Revises: 243a83fc7ea5
Create Date: 2023-06-08 20:57:48.849063

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fbc64064fe39'
down_revision = '243a83fc7ea5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('prob_unit',
    sa.Column('type', sa.String(length=15), nullable=False),
    sa.Column('probs', sa.JSON(), nullable=True),
    sa.Column('probability_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['probability_id'], ['probability.id'], ),
    sa.PrimaryKeyConstraint('type', 'probability_id')
    )
    op.drop_column('probability', 'prob_drakes')
    op.drop_column('probability', 'prob_kills')
    op.drop_column('probability', 'prob_towers')
    op.drop_column('probability', 'prob_elders')
    op.drop_column('probability', 'prob_exp')
    op.drop_column('probability', 'prob_gold')
    op.drop_column('probability', 'prob_barons')
    op.drop_column('probability', 'prob_assists')
    op.drop_column('probability', 'prob_deaths')
    op.drop_column('probability', 'prob_inhibitors')
    op.drop_column('probability', 'prob_win')
    op.drop_column('probability', 'prob_heralds')
    op.add_column('probability', sa.Column('prob_finish_early', sa.Float(), server_default='0', nullable=False))
    op.add_column('probability', sa.Column('updated', sa.Boolean(), server_default='0', nullable=False))
    op.add_column('user', sa.Column('privileges', sa.String(length=3), server_default='', nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'privileges')
    op.drop_column('probability', 'prob_finish_early')
    op.drop_column('probability', 'updated')
    op.add_column('probability', sa.Column('prob_heralds', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.add_column('probability', sa.Column('prob_win', sa.REAL(), autoincrement=False, nullable=True))
    op.add_column('probability', sa.Column('prob_inhibitors', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.add_column('probability', sa.Column('prob_deaths', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.add_column('probability', sa.Column('prob_assists', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.add_column('probability', sa.Column('prob_barons', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.add_column('probability', sa.Column('prob_gold', sa.REAL(), autoincrement=False, nullable=True))
    op.add_column('probability', sa.Column('prob_exp', sa.REAL(), autoincrement=False, nullable=True))
    op.add_column('probability', sa.Column('prob_elders', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.add_column('probability', sa.Column('prob_towers', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.add_column('probability', sa.Column('prob_kills', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.add_column('probability', sa.Column('prob_drakes', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.drop_table('prob_unit')
    # ### end Alembic commands ###