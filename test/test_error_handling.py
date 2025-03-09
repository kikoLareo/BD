import pytest
from fastapi.testclient import TestClient
from main import app
from sqlalchemy.exc import IntegrityError, OperationalError
from unittest.mock import patch, MagicMock
from utils.error_handling import (
    ErrorCode,
    handle_sqlalchemy_error,
    handle_not_found_error,
    handle_validation_error,
    handle_auth_error
)

client = TestClient(app)

# Tests para verificar que los errores se manejan correctamente
class TestErrorHandling:
    
    def test_not_found_error(self):
        """Verifica que los errores 404 devuelven el formato correcto"""
        response = client.get("/users/9999")  # ID que no existe
        assert response.status_code == 404
        data = response.json()
        
        # Verificar estructura del error
        assert "detail" in data
        assert "error" in data["detail"]
        assert "code" in data["detail"]["error"]
        assert "message" in data["detail"]["error"]
        
        # Verificar código de error
        assert data["detail"]["error"]["code"] == ErrorCode.RESOURCE_NOT_FOUND
    
    @patch("db.database.get_db")
    def test_db_connection_error(self, mock_get_db):
        """Verifica que los errores de conexión a la BD se manejan correctamente"""
        # Simular error de conexión a la BD
        mock_session = MagicMock()
        mock_session.query.side_effect = OperationalError("connection error", None, None)
        mock_get_db.return_value = mock_session
        
        response = client.get("/users")
        assert response.status_code == 503  # Service Unavailable
        data = response.json()
        
        # Verificar estructura del error
        assert "detail" in data
        assert "error" in data["detail"]
        assert data["detail"]["error"]["code"] == ErrorCode.DB_CONNECTION_ERROR
    
    @patch("db.database.get_db")
    def test_integrity_error(self, mock_get_db):
        """Verifica que los errores de integridad se manejan correctamente"""
        # Simular error de integridad (ej. violación de restricción única)
        mock_session = MagicMock()
        mock_session.add.side_effect = IntegrityError("unique constraint violation", None, None)
        mock_session.commit.side_effect = IntegrityError("unique constraint violation", None, None)
        mock_get_db.return_value = mock_session
        
        response = client.post("/users/create", json={
            "username": "test_user",
            "email": "test@example.com",
            "password": "password123"
        })
        
        assert response.status_code == 409  # Conflict
        data = response.json()
        
        # Verificar estructura del error
        assert "detail" in data
        assert "error" in data["detail"]
        assert data["detail"]["error"]["code"] == ErrorCode.DB_CONSTRAINT_ERROR
    
    def test_validation_error(self):
        """Verifica que los errores de validación se manejan correctamente"""
        # Enviar datos inválidos
        response = client.post("/users/create", json={
            "username": "test_user",
            # Falta el email y la contraseña
        })
        
        assert response.status_code == 422  # Unprocessable Entity
        data = response.json()
        
        # Verificar que contiene detalles de validación
        assert "detail" in data
    
    def test_auth_error(self):
        """Verifica que los errores de autenticación se manejan correctamente"""
        response = client.post("/auth/login", json={
            "username": "usuario_inexistente",
            "password": "contraseña_incorrecta"
        })
        
        assert response.status_code == 401  # Unauthorized
        data = response.json()
        
        # Verificar estructura del error
        assert "detail" in data
        assert "error" in data["detail"]
        assert data["detail"]["error"]["code"] == ErrorCode.INVALID_CREDENTIALS
