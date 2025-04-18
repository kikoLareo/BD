from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from logging_config import logger
from dotenv import load_dotenv

load_dotenv()


Base = declarative_base()

# Construir la URL de conexión a partir de variables de entorno
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'wavestudio_db')
DB_USER = os.getenv('DB_USER', 'kiko')
DB_PASSWORD = os.getenv('DB_PASSWORD', '.,Franlareo1701_.,')
DB_PORT = os.getenv('DB_PORT', '5432')

DATABASE_URL = os.getenv('DATABASE_URL', f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
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
