from main import app
from test.conftest import setup_database, client

# Prueba para asignar rol a un usuario
def test_assign_role_to_user(client,setup_database):
    # Crear usuario y rol
    user_response = client.post("/users/create", json={"name": "test_user", "email": "test@example.com"})
    print("Usuario creado: ", user_response.json())
    user_id = user_response.json()["id"]
    role_response = client.post("/roles/create", json={"name": "moderator", "description": "Moderator role"})
    role_id = role_response.json()["id"]

    # Asignar rol
    assign_response = client.post(f"/users/{user_id}/assign-role/{role_id}")
    assert assign_response.status_code == 200
    assert assign_response.json() == {"message": "Rol asignado exitosamente"}

# Prueba para eliminar rol de un usuario
def test_remove_role_from_user(client,setup_database):
    # Crear usuario y rol
    user_response = client.post("/users/create", json={"name": "test_user2", "email": "test2@example.com"})
    user_id = user_response.json()["id"]
    role_response = client.post("/roles/create", json={"name": "viewer", "description": "Viewer role"})
    role_id = role_response.json()["id"]

    # Asignar rol
    client.post(f"/users/{user_id}/assign-role/{role_id}")

    # Eliminar rol
    remove_response = client.delete(f"/users/{user_id}/remove-role/{role_id}")
    assert remove_response.status_code == 200
    assert remove_response.json() == {"message": "Rol eliminado del usuario"}
