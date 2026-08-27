from fastapi.testclient import TestClient


def test_api_crear_categoria_ingreso(client: TestClient):
    """1. Crear categoría de ingreso (Status 201)."""
    payload = {
        "nombre": "Salario Principal",
        "tipo": "ingreso"
    }
    response = client.post("/api/categorias", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["id_categoria"] > 0
    assert data["nombre"] == "Salario Principal"
    assert data["tipo"] == "ingreso"
    # El propietario sale del token, no del cuerpo de la petición.
    assert data["id_usuario"] == 1


def test_api_crear_categoria_gasto(client: TestClient):
    """2. Crear categoría de gasto (Status 201)."""
    payload = {
        "nombre": "Mercado Mensual",
        "tipo": "gasto"
    }
    response = client.post("/api/categorias", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["id_categoria"] > 0
    assert data["nombre"] == "Mercado Mensual"
    assert data["tipo"] == "gasto"
    assert data["id_usuario"] == 1


def test_api_listar_categorias_usuario(client: TestClient):
    """3. Listar las categorías del usuario autenticado (Status 200)."""
    client.post("/api/categorias", json={"nombre": "Freelance", "tipo": "ingreso"})
    client.post("/api/categorias", json={"nombre": "Transporte", "tipo": "gasto"})

    response = client.get("/api/categorias")
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
        "tipo": "otro_tipo_invalido"
    }
    response = client.post("/api/categorias", json=payload)
    assert response.status_code == 422


def test_api_crear_categoria_ignora_id_usuario_del_cuerpo(client: TestClient):
    """
    5. Enviar `id_usuario` en el cuerpo no cambia el propietario.

    Sustituye a la antigua prueba de "usuario inexistente": ese caso ya no puede
    darse porque el usuario no lo elige el cliente, sino el token. Lo que sí
    debe comprobarse es que un `id_usuario` inyectado en el JSON se ignora por
    completo y la categoría se crea en la cuenta autenticada.
    """
    payload = {
        "nombre": "Educación",
        "tipo": "gasto",
        "id_usuario": 99999
    }
    response = client.post("/api/categorias", json=payload)
    assert response.status_code == 201
    assert response.json()["id_usuario"] == 1


def test_api_categoria_pertenece_al_usuario_correcto(
    client: TestClient, client_usuario_2: TestClient
):
    """6. Cada usuario solo ve sus propias categorías."""
    client.post("/api/categorias", json={"nombre": "Cat User 1", "tipo": "gasto"})
    client_usuario_2.post("/api/categorias", json={"nombre": "Cat User 2", "tipo": "gasto"})

    r_user2 = client_usuario_2.get("/api/categorias")
    assert r_user2.status_code == 200
    cats_user2 = r_user2.json()
    assert len(cats_user2) == 1
    assert cats_user2[0]["nombre"] == "Cat User 2"
    assert cats_user2[0]["id_usuario"] == 2

    r_user1 = client.get("/api/categorias")
    assert r_user1.status_code == 200
    nombres_user1 = [c["nombre"] for c in r_user1.json()]
    assert "Cat User 1" in nombres_user1
    assert "Cat User 2" not in nombres_user1


def test_api_crear_categoria_duplicada_mismo_tipo_y_usuario(client: TestClient):
    """7. Rechazar categoría duplicada para el mismo usuario y tipo (Status 409 Conflict)."""
    payload = {
        "nombre": "Gimnasio",
        "tipo": "gasto"
    }
    r1 = client.post("/api/categorias", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/api/categorias", json=payload)
    assert r2.status_code == 409
    assert "Ya existe una categoría" in r2.json()["detail"]


def test_api_categorias_requiere_autenticacion(client_anonimo: TestClient):
    """8. Sin token, los endpoints de categorías responden 401."""
    assert client_anonimo.get("/api/categorias").status_code == 401
    assert client_anonimo.post(
        "/api/categorias", json={"nombre": "Sin token", "tipo": "gasto"}
    ).status_code == 401
    assert client_anonimo.put(
        "/api/categorias/1", json={"nombre": "Sin token", "tipo": "gasto"}
    ).status_code == 401
    assert client_anonimo.delete("/api/categorias/1").status_code == 401


def test_api_actualizar_categoria_exitoso(client: TestClient):
    """9. Actualizar una categoría existente propia (Status 200)."""
    creada = client.post("/api/categorias", json={"nombre": "Ocio", "tipo": "gasto"}).json()
    id_cat = creada["id_categoria"]

    response = client.put(
        f"/api/categorias/{id_cat}",
        json={"nombre": "Entretenimiento", "tipo": "gasto"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id_categoria"] == id_cat
    assert data["nombre"] == "Entretenimiento"
    assert data["tipo"] == "gasto"


def test_api_actualizar_categoria_inexistente(client: TestClient):
    """10. Actualizar una categoría inexistente (Status 404)."""
    response = client.put(
        "/api/categorias/9999",
        json={"nombre": "Fantasma", "tipo": "gasto"}
    )
    assert response.status_code == 404


def test_api_actualizar_categoria_otro_usuario(
    client: TestClient, client_usuario_2: TestClient
):
    """11. Un usuario no puede modificar la categoría de otro usuario (Status 400)."""
    creada_user2 = client_usuario_2.post(
        "/api/categorias", json={"nombre": "Privada User2", "tipo": "gasto"}
    ).json()
    id_cat = creada_user2["id_categoria"]

    # Usuario 1 intenta editarla
    response = client.put(
        f"/api/categorias/{id_cat}",
        json={"nombre": "Modificada por U1", "tipo": "gasto"}
    )
    assert response.status_code == 400
    assert "No tiene permisos" in response.json()["detail"]


def test_api_actualizar_categoria_tipo_invalido(client: TestClient):
    """12. Rechazar actualización con tipo inválido (Status 422)."""
    creada = client.post("/api/categorias", json={"nombre": "Salud", "tipo": "gasto"}).json()
    id_cat = creada["id_categoria"]

    response = client.put(
        f"/api/categorias/{id_cat}",
        json={"nombre": "Salud", "tipo": "invalido"}
    )
    assert response.status_code == 422


def test_api_eliminar_categoria_exitoso(client: TestClient):
    """13. Eliminar una categoría propia sin movimientos (Status 200)."""
    creada = client.post("/api/categorias", json={"nombre": "Borrable", "tipo": "ingreso"}).json()
    id_cat = creada["id_categoria"]

    response = client.delete(f"/api/categorias/{id_cat}")
    assert response.status_code == 200
    assert "eliminada exitosamente" in response.json()["mensaje"]

    # Verificar que ya no aparece en la lista
    cats = client.get("/api/categorias").json()
    assert not any(c["id_categoria"] == id_cat for c in cats)


def test_api_eliminar_categoria_inexistente(client: TestClient):
    """14. Eliminar una categoría inexistente (Status 404)."""
    response = client.delete("/api/categorias/9999")
    assert response.status_code == 404


def test_api_eliminar_categoria_otro_usuario(
    client: TestClient, client_usuario_2: TestClient
):
    """15. Un usuario no puede eliminar la categoría de otro usuario (Status 400)."""
    creada_user2 = client_usuario_2.post(
        "/api/categorias", json={"nombre": "Intocable User2", "tipo": "gasto"}
    ).json()
    id_cat = creada_user2["id_categoria"]

    # Usuario 1 intenta borrarla
    response = client.delete(f"/api/categorias/{id_cat}")
    assert response.status_code == 400
    assert "No tiene permisos" in response.json()["detail"]


def test_api_eliminar_categoria_con_movimientos_bloqueada(client: TestClient):
    """16. Eliminar categoría con movimientos asociados es rechazado (Status 400)."""
    creada = client.post("/api/categorias", json={"nombre": "Con Uso", "tipo": "gasto"}).json()
    id_cat = creada["id_categoria"]

    client.post("/api/movimientos", json={
        "id_categoria": id_cat,
        "tipo": "gasto",
        "monto": "25000.00",
        "fecha": "2026-08-10",
        "descripcion": "Gasto prueba"
    })

    response = client.delete(f"/api/categorias/{id_cat}")
    assert response.status_code == 400
    assert "movimientos" in response.json()["detail"]

