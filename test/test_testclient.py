from test.conftest import client
# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "¡Hola, mundo!"}

def test_check_endpoint_access(client):
    response = client.get("/")  # Asumiendo que tienes un endpoint en "/"
    print(response.json())  # Imprime la respuesta para verificar
    assert response.status_code == 200  # Cambia esto según lo que esperes


    