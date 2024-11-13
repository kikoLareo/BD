"""Initial migration

Revision ID: 4b9bedb9afa4
Revises: 
Create Date: 2024-10-23 20:16:16.207022

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b9bedb9afa4'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_championships_id', table_name='championships')
    op.drop_index('ix_championships_name', table_name='championships')
    op.drop_table('championships')
    op.drop_index('ix_position_rates_id', table_name='position_rates')
    op.drop_table('position_rates')
    op.drop_index('ix_payment_records_judge_id', table_name='payment_records')
    op.create_foreign_key(None, 'payment_records', 'judges', ['judge_id'], ['id'])
    op.drop_column('payment_records', 'bonus')
    op.drop_column('payment_records', 'hourly_rate')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('payment_records', sa.Column('hourly_rate', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.add_column('payment_records', sa.Column('bonus', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'payment_records', type_='foreignkey')
    op.create_index('ix_payment_records_judge_id', 'payment_records', ['judge_id'], unique=False)
    op.create_table('position_rates',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('position', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('daily_rate', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='position_rates_pkey'),
    sa.UniqueConstraint('position', name='position_rates_position_key')
    )
    op.create_index('ix_position_rates_id', 'position_rates', ['id'], unique=False)
    op.create_table('championships',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('location', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('date', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='championships_pkey')
    )
    op.create_index('ix_championships_name', 'championships', ['name'], unique=False)
    op.create_index('ix_championships_id', 'championships', ['id'], unique=False)
    # ### end Alembic commands ###
