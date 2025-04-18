"""Initial migration

Revision ID: 83e8362dc9fc
Revises: 
Create Date: 2024-11-25 21:57:36.782205

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '83e8362dc9fc'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('disciplines',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('category', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_disciplines_id'), 'disciplines', ['id'], unique=False)
    op.create_index(op.f('ix_disciplines_name'), 'disciplines', ['name'], unique=True)
    op.create_table('job_positions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_job_positions_id'), 'job_positions', ['id'], unique=False)
    op.create_index(op.f('ix_job_positions_title'), 'job_positions', ['title'], unique=True)
    op.create_table('organizers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organizers_id'), 'organizers', ['id'], unique=False)
    op.create_index(op.f('ix_organizers_name'), 'organizers', ['name'], unique=True)
    op.create_table('permissions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_permissions_id'), 'permissions', ['id'], unique=False)
    op.create_index(op.f('ix_permissions_name'), 'permissions', ['name'], unique=True)
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=False)
    op.create_index(op.f('ix_roles_name'), 'roles', ['name'], unique=True)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('password_hash', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('championships',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('location', sa.String(), nullable=True),
    sa.Column('start_date', sa.DateTime(), nullable=True),
    sa.Column('end_date', sa.DateTime(), nullable=True),
    sa.Column('organizer_id', sa.Integer(), nullable=True),
    sa.Column('discipline_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['discipline_id'], ['disciplines.id'], ),
    sa.ForeignKeyConstraint(['organizer_id'], ['organizers.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_championships_id'), 'championships', ['id'], unique=False)
    op.create_index(op.f('ix_championships_name'), 'championships', ['name'], unique=True)
    op.create_table('role_permission_association',
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('permission_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )
    op.create_table('user_roles',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'role_id')
    )
    op.create_table('championship_assignments',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('championship_id', sa.Integer(), nullable=False),
    sa.Column('job_position_id', sa.Integer(), nullable=True),
    sa.Column('hours_worked', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['championship_id'], ['championships.id'], ),
    sa.ForeignKeyConstraint(['job_position_id'], ['job_positions.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'championship_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('championship_assignments')
    op.drop_table('user_roles')
    op.drop_table('role_permission_association')
    op.drop_index(op.f('ix_championships_name'), table_name='championships')
    op.drop_index(op.f('ix_championships_id'), table_name='championships')
    op.drop_table('championships')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_roles_name'), table_name='roles')
    op.drop_index(op.f('ix_roles_id'), table_name='roles')
    op.drop_table('roles')
    op.drop_index(op.f('ix_permissions_name'), table_name='permissions')
    op.drop_index(op.f('ix_permissions_id'), table_name='permissions')
    op.drop_table('permissions')
    op.drop_index(op.f('ix_organizers_name'), table_name='organizers')
    op.drop_index(op.f('ix_organizers_id'), table_name='organizers')
    op.drop_table('organizers')
    op.drop_index(op.f('ix_job_positions_title'), table_name='job_positions')
    op.drop_index(op.f('ix_job_positions_id'), table_name='job_positions')
    op.drop_table('job_positions')
    op.drop_index(op.f('ix_disciplines_name'), table_name='disciplines')
    op.drop_index(op.f('ix_disciplines_id'), table_name='disciplines')
    op.drop_table('disciplines')
    # ### end Alembic commands ###
