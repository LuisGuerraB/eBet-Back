"""Prize

Revision ID: c6a66cb6844c
Revises: 9f7d03e9490d
Create Date: 2023-06-07 20:19:49.200850

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c6a66cb6844c'
down_revision = '9f7d03e9490d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('prize',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('img', sa.String(), nullable=False),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('prize')
    # ### end Alembic commands ###
