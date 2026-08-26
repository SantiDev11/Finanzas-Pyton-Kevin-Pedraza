from fastapi.testclient import TestClient


def test_api_crear_categoria_ingreso(client: TestClient):
    """1. Crear categoría de ingreso (Status 201)."""
    payload = {
        "nombre": "Salario Principal",
        "tipo": "ingreso",
        "id_usuario": 1
    }
    response = client.post("/api/categorias", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["id_categoria"] > 0
    assert data["nombre"] == "Salario Principal"
    assert data["tipo"] == "ingreso"
    assert data["id_usuario"] == 1


def test_api_crear_categoria_gasto(client: TestClient):
    """2. Crear categoría de gasto (Status 201)."""
    payload = {
        "nombre": "Mercado Mensual",
        "tipo": "gasto",
        "id_usuario": 1
    }
    response = client.post("/api/categorias", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["id_categoria"] > 0
    assert data["nombre"] == "Mercado Mensual"
    assert data["tipo"] == "gasto"
    assert data["id_usuario"] == 1


def test_api_listar_categorias_usuario(client: TestClient):
    """3. Listar categorías de un usuario (Status 200)."""
    # Crear dos categorías
    client.post("/api/categorias", json={"nombre": "Freelance", "tipo": "ingreso", "id_usuario": 1})
    client.post("/api/categorias", json={"nombre": "Transporte", "tipo": "gasto", "id_usuario": 1})

    response = client.get("/api/categorias?id_usuario=1")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    nombres = [item["nombre"] for item in data]
    assert "Freelance" in nombres
    assert "Transporte" in nombres


def test_api_crear_categoria_rechazar_tipo_invalido(client: TestClient):
    """4. Rechazar tipo inválido (Status 422)."""
    payload = {
        "nombre": "Inversiones",
        "tipo": "otro_tipo_invalido",
        "id_usuario": 1
    }
    response = client.post("/api/categorias", json=payload)
    assert response.status_code == 422


def test_api_crear_categoria_usuario_inexistente(client: TestClient):
    """5. Rechazar usuario inexistente (Status 404)."""
    payload = {
        "nombre": "Educación",
        "tipo": "gasto",
        "id_usuario": 99999
    }
    response = client.post("/api/categorias", json=payload)
    assert response.status_code == 404
    assert "no existe" in response.json()["detail"]


def test_api_categoria_pertenece_al_usuario_correcto(client: TestClient):
    """6. Verificar que las categorías pertenecen al usuario consultado."""
    # Crear usuario 2
    res_usr = client.post("/api/usuarios", json={
        "nombre": "Usuario Dos",
        "correo": "usuario2@example.com",
        "contrasena": "Password123*"
    })
    user2_id = res_usr.json()["id_usuario"]

    # Crear categoría para usuario 1 y para usuario 2
    client.post("/api/categorias", json={"nombre": "Cat User 1", "tipo": "gasto", "id_usuario": 1})
    client.post("/api/categorias", json={"nombre": "Cat User 2", "tipo": "gasto", "id_usuario": user2_id})

    # Consultar usuario 2
    r_user2 = client.get(f"/api/categorias?id_usuario={user2_id}")
    assert r_user2.status_code == 200
    cats_user2 = r_user2.json()
    assert len(cats_user2) == 1
    assert cats_user2[0]["nombre"] == "Cat User 2"
    assert cats_user2[0]["id_usuario"] == user2_id


def test_api_crear_categoria_duplicada_mismo_tipo_y_usuario(client: TestClient):
    """7. Rechazar categoría duplicada para el mismo usuario y tipo (Status 409 Conflict)."""
    payload = {
        "nombre": "Gimnasio",
        "tipo": "gasto",
        "id_usuario": 1
    }
    r1 = client.post("/api/categorias", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/api/categorias", json=payload)
    assert r2.status_code == 409
    assert "Ya existe una categoría" in r2.json()["detail"]
