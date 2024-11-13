from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os

# Importa el `Base` y los modelos
from app.models.Base import Base  # Asegúrate de que este es el camino correcto a tus modelos

# Cargar configuración de logging
config = context.config
fileConfig(config.config_file_name)

# Configurar URL de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://wavesHub_user:WavesHub@localhost:5432/wavesHub_db")
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Apuntar al `metadata` de `Base` para que Alembic lo reconozca
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
