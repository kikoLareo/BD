from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from logging_config import logger

Base = declarative_base()
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://waveshub_user:WavesHub@localhost:5432/waveshub_db')
logger.info(f"DATABASE_URL: {DATABASE_URL}")

engine = create_engine(DATABASE_URL,    echo=True )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

metadata = MetaData()
metadata.reflect(bind=engine)

logger.info("Tablas disponibles:")
for table in metadata.tables.keys():
    logger.info(table)

# Dependencia de base de datos para usar en los endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
