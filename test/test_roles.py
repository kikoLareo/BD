from main import app
from test.conftest import setup_database, client, engine


# Prueba de creación de rol
def test_create_role(client, setup_database):
    response = client.post("/roles/create", json={"name": "admin", "description": "Admin role"})
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["name"] == "admin"

# Prueba de actualización de rol
def test_update_role(client,setup_database):
    # Crear rol inicial
    create_response = client.post("/roles/create", json={"name": "user", "description": "User role"})
    role_id = create_response.json()["id"]

    # Actualizar rol
    response = client.put(f"/roles/update/{role_id}", json={"description": "Updated User role"})    
    assert response.status_code == 200
    assert response.json()["id"] == role_id
    assert response.json()["description"] == "Updated User role"

# Prueba de eliminación de rol
def test_delete_role(client, setup_database):
    # Crear rol inicial
    create_response = client.post("/roles/create", json={"name": "editor", "description": "Editor role"})
    role_id = create_response.json()["id"]

    # Eliminar rol
    response = client.delete(f"/roles/delete/{role_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Rol eliminado exitosamente"}
