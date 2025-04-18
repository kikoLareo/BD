"""add id pk and adjust assignments

Revision ID: 66ec44cfdc60
Revises: 0df7f324b3ca
Create Date: 2025-03-12 22:54:24.095575

"""
from alembic import op
import sqlalchemy as sa

# Identificadores de la migración
revision = '66ec44cfdc60'
down_revision = '0df7f324b3ca'  # Usa el ID correcto de la migración anterior
branch_labels = None
depends_on = None
def upgrade():
    # 1. Añadir la columna como nullable
    op.add_column('championship_assignments', sa.Column('id', sa.Integer(), nullable=True))

    # 2. Asignar ids a los registros existentes
    op.execute("""
        UPDATE championship_assignments
        SET id = subquery.rn
        FROM (
            SELECT ctid, row_number() OVER (ORDER BY user_id, championship_id) AS rn
            FROM championship_assignments
        ) AS subquery
        WHERE championship_assignments.ctid = subquery.ctid;
    """)

    # 3. Hacer la columna NOT NULL
    op.alter_column('championship_assignments', 'id', nullable=False)

    # 4. Eliminar la PK anterior (importante antes de crear la nueva)
    op.drop_constraint('championship_assignments_pkey', 'championship_assignments', type_='primary')

    # 5. Crear la nueva Primary Key con el campo id
    op.create_primary_key('pk_championship_assignments', 'championship_assignments', ['id'])

    # 6. Crear la secuencia y establecer el default para futuros inserts
    op.execute("""
        CREATE SEQUENCE championship_assignments_id_seq OWNED BY championship_assignments.id;
    """)
    op.execute("""
        ALTER TABLE championship_assignments ALTER COLUMN id SET DEFAULT nextval('championship_assignments_id_seq');
    """)
    op.execute("""
        SELECT setval('championship_assignments_id_seq', (SELECT MAX(id) FROM championship_assignments));
    """)


def downgrade():
    # Para revertir: quita la primary key y elimina la columna id
    op.drop_constraint("pk_championship_assignments", "championship_assignments", type_="primary")
    op.drop_column('championship_assignments', 'id')
    op.execute("DROP SEQUENCE IF EXISTS championship_assignments_id_seq CASCADE;")
