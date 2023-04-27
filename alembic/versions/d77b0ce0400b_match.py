"""Match

Revision ID: d77b0ce0400b
Revises: c9c4f56419a2
Create Date: 2023-04-24 18:14:05.956848

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd77b0ce0400b'
down_revision = 'c9c4f56419a2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('match',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.Column('sets',sa.Integer(),nullable=False),
                    sa.Column('plan_date', sa.DateTime(), nullable=False),
                    sa.Column('ini_date', sa.DateTime(), nullable=True),
                    sa.Column('end_date', sa.DateTime(), nullable=True),
                    sa.Column('away_team_id', sa.Integer(), nullable=False),
                    sa.Column('local_team_id', sa.Integer(), nullable=False),
                    sa.Column('season_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['away_team_id'], ['team.id'], ),
                    sa.ForeignKeyConstraint(['local_team_id'], ['team.id'], ),
                    sa.ForeignKeyConstraint(['season_id'], ['season.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('match')
    # ### end Alembic commands ###
