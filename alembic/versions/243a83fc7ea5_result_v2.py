"""Result v2

Revision ID: 243a83fc7ea5
Revises: 9f7d03e9490d
Create Date: 2023-06-08 18:12:53.737687

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '243a83fc7ea5'
down_revision = 'c6a66cb6844c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stat',
    sa.Column('type', sa.String(length=15), nullable=False),
    sa.Column('value', sa.Integer(), nullable=False),
    sa.Column('result_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['result_id'], ['result.id'], ),
    sa.PrimaryKeyConstraint('type', 'result_id')
    )
    op.drop_column('result', 'exp_percent')
    op.drop_column('result', 'gold_percent')
    op.drop_column('result', 'deaths')
    op.drop_column('result', 'winner')
    op.drop_column('result', 'kills')
    op.drop_column('result', 'towers')
    op.drop_column('result', 'assists')
    op.drop_column('result', 'barons')
    op.drop_column('result', 'elders')
    op.drop_column('result', 'heralds')
    op.drop_column('result', 'inhibitors')
    op.drop_column('result', 'drakes')
    op.drop_column('user', 'privileges')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('privileges', sa.VARCHAR(length=3), server_default=sa.text("''::character varying"), autoincrement=False, nullable=False))
    op.add_column('result', sa.Column('drakes', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('result', sa.Column('inhibitors', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('result', sa.Column('heralds', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('result', sa.Column('elders', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('result', sa.Column('barons', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('result', sa.Column('assists', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('result', sa.Column('towers', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('result', sa.Column('kills', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('result', sa.Column('winner', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('result', sa.Column('deaths', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('result', sa.Column('gold_percent', sa.REAL(), autoincrement=False, nullable=True))
    op.add_column('result', sa.Column('exp_percent', sa.REAL(), autoincrement=False, nullable=True))
    op.drop_table('stat')
    # ### end Alembic commands ###
