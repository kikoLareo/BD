"""add_missing_columns_to_organizers

Revision ID: 0df7f324b3ca
Revises: 83e8362dc9fc
Create Date: 2025-03-07 14:09:16.309024

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0df7f324b3ca'
down_revision: Union[str, None] = '83e8362dc9fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('championship_assignments', sa.Column('start_date', sa.Date(), nullable=True))
    op.add_column('championship_assignments', sa.Column('end_date', sa.Date(), nullable=True))
    op.add_column('championships', sa.Column('description', sa.String(), nullable=True))
    op.alter_column('championships', 'start_date',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.Date(),
               existing_nullable=True)
    op.alter_column('championships', 'end_date',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.Date(),
               existing_nullable=True)
    op.add_column('organizers', sa.Column('description', sa.String(), nullable=True))
    op.add_column('organizers', sa.Column('placement', sa.String(), nullable=True))
    op.add_column('organizers', sa.Column('phone', sa.String(), nullable=True))
    op.add_column('organizers', sa.Column('email', sa.String(), nullable=True))
    op.add_column('organizers', sa.Column('website', sa.String(), nullable=True))
    op.alter_column('roles', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('roles', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_column('organizers', 'website')
    op.drop_column('organizers', 'email')
    op.drop_column('organizers', 'phone')
    op.drop_column('organizers', 'placement')
    op.drop_column('organizers', 'description')
    op.alter_column('championships', 'end_date',
               existing_type=sa.Date(),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    op.alter_column('championships', 'start_date',
               existing_type=sa.Date(),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    op.drop_column('championships', 'description')
    op.drop_column('championship_assignments', 'end_date')
    op.drop_column('championship_assignments', 'start_date')
    # ### end Alembic commands ###
