from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Base de datos en memoria para pruebas
#SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
SQLALCHEMY_DATABASE_URL = "postgresql://kiko:.,Franlareo1701_.,@localhost:5432/wavestudio_db"

# Configuración del motor de la base de datos de prueba
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para declarar modelos de SQLAlchemy
Base = declarative_base()

