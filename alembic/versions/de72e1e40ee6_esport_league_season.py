"""Esport-League-Tournament

Revision ID: de72e1e40ee6
Revises: 
Create Date: 2023-04-24 17:20:12.549239

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'de72e1e40ee6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('esport',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('img', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('league',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('acronym', sa.String(), nullable=False),
    sa.Column('img', sa.String(), nullable=False),
    sa.Column('esport_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['esport_id'], ['esport.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('img'),
    sa.UniqueConstraint('name'),
    sa.UniqueConstraint('acronym')
    )
    op.create_table('tournament',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('serie_id', sa.Integer(), nullable=False),
    sa.Column('ini_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('league_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['league_id'], ['league.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tournament')
    op.drop_table('league')
    op.drop_table('esport')
    # ### end Alembic commands ###
