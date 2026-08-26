from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check_endpoint():
    """
    Verifica que el endpoint raíz GET / responde con status 200 y mensaje válido.
    """
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"
    assert "message" in data
    assert data["message"] == "API de Finanzas Personales funcionando correctamente"
