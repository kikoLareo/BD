# conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.database import Base, get_db
from fastapi.testclient import TestClient
from main import app

# Cambia la conexión para usar PostgreSQL y tu base de datos de prueba
engine = create_engine("postgresql://waveshub_user:WavesHub@localhost:5432/waveshub_db")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fixture para crear y eliminar las tablas en la base de datos de prueba
@pytest.fixture(scope="module")
def setup_database():
    print("setup_database se ejecuta: Creando las tablas en la base de datos de prueba...")
    Base.metadata.create_all(bind=engine)  # Crea las tablas
    yield  # Aquí se ejecutan las pruebas
    print("Eliminando las tablas después de las pruebas...")
    Base.metadata.drop_all(bind=engine)  # Elimina las tablas después de las pruebas

# Sobrescribe la dependencia `get_db` para usar la sesión de prueba
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Configura el client para usarlo en las pruebas
@pytest.fixture(scope="module")
def client():
    return TestClient(app)