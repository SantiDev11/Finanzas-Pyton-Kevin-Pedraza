from fastapi.testclient import TestClient


# =============================================================================
# PRUEBAS DE CREACIÓN DE MOVIMIENTOS
# =============================================================================

def test_api_crear_ingreso_valido(client: TestClient):
    """1. Crear ingreso válido (Status 201)."""
    payload = {
        "id_categoria": 1,  # 'Salario' (ingreso)
        "tipo": "ingreso",
        "monto": "2500000.00",
        "fecha": "2026-06-01",
        "descripcion": "Nómina mensual",
    }
    response = client.post("/api/movimientos", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["id_movimiento"] > 0
    assert data["id_usuario"] == 1
    assert data["id_categoria"] == 1
    assert data["categoria"] == "Salario"
    assert data["tipo"] == "ingreso"
    assert float(data["monto"]) == 2500000.00
    assert data["fecha"] == "2026-06-01"
    assert data["descripcion"] == "Nómina mensual"


def test_api_crear_gasto_valido(client: TestClient):
    """2. Crear gasto válido (Status 201)."""
    payload = {
        "id_categoria": 2,  # 'Alimentación' (gasto)
        "tipo": "gasto",
        "monto": "320000.50",
        "fecha": "2026-06-05",
        "descripcion": "Mercado quincenal",
    }
    response = client.post("/api/movimientos", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["id_movimiento"] > 0
    assert data["categoria"] == "Alimentación"
    assert data["tipo"] == "gasto"
    assert float(data["monto"]) == 320000.50


def test_api_crear_movimiento_rechazar_tipo_invalido(client: TestClient):
    """3. Rechazar tipo inválido (Status 422)."""
    payload = {
        "id_categoria": 1,
        "tipo": "prestamo_invalido",
        "monto": "1000.00",
        "fecha": "2026-06-01",
    }
    response = client.post("/api/movimientos", json=payload)
    assert response.status_code == 422


def test_api_crear_movimiento_rechazar_monto_cero(client: TestClient):
    """4. Rechazar monto cero (Status 422)."""
    payload = {
        "id_categoria": 1,
        "tipo": "ingreso",
        "monto": "0.00",
        "fecha": "2026-06-01",
    }
    response = client.post("/api/movimientos", json=payload)
    assert response.status_code == 422


def test_api_crear_movimiento_rechazar_monto_negativo(client: TestClient):
    """5. Rechazar monto negativo (Status 422)."""
    payload = {
        "id_categoria": 1,
        "tipo": "ingreso",
        "monto": "-5000.00",
        "fecha": "2026-06-01",
    }
    response = client.post("/api/movimientos", json=payload)
    assert response.status_code == 422


def test_api_crear_movimiento_ignora_id_usuario_del_cuerpo(client: TestClient):
    """
    6. Enviar `id_usuario` en el cuerpo no cambia el propietario.

    Sustituye a la antigua prueba de "usuario inexistente": el usuario ya no lo
    elige el cliente sino el token, así que ese caso no puede darse. Lo que hay
    que comprobar ahora es que un `id_usuario` inyectado en el JSON se ignora y
    el movimiento se registra en la cuenta autenticada.
    """
    payload = {
        "id_usuario": 9999,
        "id_categoria": 1,
        "tipo": "ingreso",
        "monto": "50000.00",
        "fecha": "2026-06-01",
    }
    response = client.post("/api/movimientos", json=payload)
    assert response.status_code == 201
    assert response.json()["id_usuario"] == 1


def test_api_crear_movimiento_categoria_inexistente(client: TestClient):
    """7. Rechazar categoría inexistente (Status 404)."""
    payload = {
        "id_categoria": 9999,
        "tipo": "ingreso",
        "monto": "50000.00",
        "fecha": "2026-06-01",
    }
    response = client.post("/api/movimientos", json=payload)
    assert response.status_code == 404
    assert "no existe" in response.json()["detail"]


def test_api_crear_movimiento_categoria_otro_usuario(
    client: TestClient, client_usuario_2: TestClient
):
    """8. Rechazar categoría perteneciente a otro usuario (Status 400)."""
    # El usuario 2 crea una categoría en su propia cuenta.
    r_cat = client_usuario_2.post("/api/categorias", json={
        "nombre": "Freelance U2",
        "tipo": "ingreso"
    })
    cat_u2_id = r_cat.json()["id_categoria"]

    # El usuario 1 intenta usar esa categoría ajena.
    payload = {
        "id_categoria": cat_u2_id,
        "tipo": "ingreso",
        "monto": "150000.00",
        "fecha": "2026-06-01",
    }
    response = client.post("/api/movimientos", json=payload)
    assert response.status_code == 400
    assert "no pertenece al usuario" in response.json()["detail"]


def test_api_crear_movimiento_incoherencia_tipo_categoria(client: TestClient):
    """9. Rechazar incoherencia entre tipo de movimiento y tipo de categoría (Status 400)."""
    # Categoría 2 es de tipo 'gasto' (Alimentación). Intentamos registrarla como 'ingreso'
    payload = {
        "id_categoria": 2,
        "tipo": "ingreso",  # Mismatch!
        "monto": "70000.00",
        "fecha": "2026-06-01",
    }
    response = client.post("/api/movimientos", json=payload)
    assert response.status_code == 400
    assert "Incoherencia de tipo" in response.json()["detail"]


# =============================================================================
# PRUEBAS DE CONSULTA Y FILTROS
# =============================================================================

def test_api_listar_movimientos_usuario(client: TestClient):
    """10. Listar movimientos de un usuario (Status 200)."""
    client.post("/api/movimientos", json={
        "id_categoria": 1, "tipo": "ingreso", "monto": "1000.00", "fecha": "2026-01-10"
    })
    client.post("/api/movimientos", json={
        "id_categoria": 2, "tipo": "gasto", "monto": "200.00", "fecha": "2026-01-15"
    })

    response = client.get("/api/movimientos")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    # Comprobar orden descendente por fecha
    assert data[0]["fecha"] >= data[1]["fecha"]


def test_api_listar_movimientos_no_devuelve_otros_usuarios(
    client: TestClient, client_usuario_2: TestClient
):
    """11. No devolver movimientos de otro usuario (Status 200)."""
    # El usuario 2 crea su categoría y su movimiento.
    r_cat = client_usuario_2.post("/api/categorias", json={
        "nombre": "Gasto U2", "tipo": "gasto"
    })
    cat_u2_id = r_cat.json()["id_categoria"]
    client_usuario_2.post("/api/movimientos", json={
        "id_categoria": cat_u2_id, "tipo": "gasto", "monto": "999.00", "fecha": "2026-01-20"
    })

    # El listado del usuario 1 no contiene nada del usuario 2.
    r_u1 = client.get("/api/movimientos")
    for mov in r_u1.json():
        assert mov["id_usuario"] == 1
    assert all(float(m["monto"]) != 999.00 for m in r_u1.json())


def test_api_filtrar_movimientos_por_fecha(client: TestClient):
    """12-14. Filtrar por fecha inicial, final y rango (Status 200)."""
    client.post("/api/movimientos", json={
        "id_categoria": 1, "tipo": "ingreso", "monto": "1000.00", "fecha": "2026-01-05"
    })
    client.post("/api/movimientos", json={
        "id_categoria": 2, "tipo": "gasto", "monto": "500.00", "fecha": "2026-02-15"
    })
    client.post("/api/movimientos", json={
        "id_categoria": 2, "tipo": "gasto", "monto": "700.00", "fecha": "2026-03-25"
    })

    # Filtro 'desde'
    r_desde = client.get("/api/movimientos?desde=2026-02-01")
    assert r_desde.status_code == 200
    for m in r_desde.json():
        assert m["fecha"] >= "2026-02-01"

    # Filtro 'hasta'
    r_hasta = client.get("/api/movimientos?hasta=2026-02-28")
    assert r_hasta.status_code == 200
    for m in r_hasta.json():
        assert m["fecha"] <= "2026-02-28"

    # Filtro rango 'desde' y 'hasta'
    r_rango = client.get("/api/movimientos?desde=2026-02-01&hasta=2026-02-28")
    assert r_rango.status_code == 200
    assert len(r_rango.json()) == 1
    assert r_rango.json()[0]["fecha"] == "2026-02-15"


def test_api_filtrar_movimientos_por_categoria(client: TestClient):
    """15. Filtrar por categoría (Status 200)."""
    client.post("/api/movimientos", json={
        "id_categoria": 1, "tipo": "ingreso", "monto": "1000.00", "fecha": "2026-01-10"
    })
    client.post("/api/movimientos", json={
        "id_categoria": 2, "tipo": "gasto", "monto": "200.00", "fecha": "2026-01-15"
    })

    r_cat = client.get("/api/movimientos?categoria=2")
    assert r_cat.status_code == 200
    for m in r_cat.json():
        assert m["id_categoria"] == 2


def test_api_filtrar_movimientos_rango_fechas_invalido(client: TestClient):
    """16. Rechazar rango de fechas inválido (Status 400)."""
    response = client.get("/api/movimientos?desde=2026-05-01&hasta=2026-01-01")
    assert response.status_code == 400
    assert "rango de fechas es inválido" in response.json()["detail"]


# =============================================================================
# PRUEBAS DE ACTUALIZACIÓN
# =============================================================================

def test_api_actualizar_movimiento_exitoso(client: TestClient):
    """17. Actualizar movimiento existente (Status 200)."""
    r_crear = client.post("/api/movimientos", json={
        "id_categoria": 2, "tipo": "gasto", "monto": "150.00", "fecha": "2026-06-01"
    })
    mov_id = r_crear.json()["id_movimiento"]

    # Actualización
    payload_update = {
        "id_categoria": 2,
        "tipo": "gasto",
        "monto": "200.00",
        "fecha": "2026-06-02",
        "descripcion": "Gasto corregido",
    }
    r_update = client.put(f"/api/movimientos/{mov_id}", json=payload_update)
    assert r_update.status_code == 200

    data = r_update.json()
    assert float(data["monto"]) == 200.00
    assert data["fecha"] == "2026-06-02"
    assert data["descripcion"] == "Gasto corregido"


def test_api_actualizar_movimiento_inexistente(client: TestClient):
    """18. Rechazar actualización de movimiento inexistente (Status 404)."""
    payload_update = {
        "id_categoria": 2,
        "tipo": "gasto",
        "monto": "200.00",
        "fecha": "2026-06-02",
    }
    response = client.put("/api/movimientos/99999", json=payload_update)
    assert response.status_code == 404


def test_api_actualizar_movimiento_otro_usuario(
    client: TestClient, client_usuario_2: TestClient
):
    """19. Impedir modificación de movimiento de otro usuario (Status 400)."""
    # El usuario 1 crea un movimiento.
    r_crear = client.post("/api/movimientos", json={
        "id_categoria": 1, "tipo": "ingreso", "monto": "5000.00", "fecha": "2026-06-01"
    })
    mov_id = r_crear.json()["id_movimiento"]

    # El usuario 2 crea su propia categoría.
    r_c2 = client_usuario_2.post("/api/categorias", json={
        "nombre": "Cat Intruso", "tipo": "ingreso"
    })
    c2_id = r_c2.json()["id_categoria"]

    # El usuario 2, con su token, intenta modificar el movimiento del usuario 1.
    payload_update = {
        "id_categoria": c2_id,
        "tipo": "ingreso",
        "monto": "9999.00",
        "fecha": "2026-06-01",
    }
    response = client_usuario_2.put(f"/api/movimientos/{mov_id}", json=payload_update)
    assert response.status_code == 400
    assert "No tiene permisos para modificar un movimiento que pertenece a otro usuario" in response.json()["detail"]

    # El movimiento del usuario 1 no ha cambiado.
    r_original = client.get("/api/movimientos")
    conservado = [m for m in r_original.json() if m["id_movimiento"] == mov_id]
    assert conservado and conservado[0]["monto"] == "5000.00"


def test_api_actualizar_movimiento_validaciones(client: TestClient):
    """20. Validar nuevamente categoría/tipo/monto en actualización."""
    r_crear = client.post("/api/movimientos", json={
        "id_categoria": 2, "tipo": "gasto", "monto": "150.00", "fecha": "2026-06-01"
    })
    mov_id = r_crear.json()["id_movimiento"]

    # Monto inválido
    r_monto_cero = client.put(f"/api/movimientos/{mov_id}", json={
        "id_categoria": 2, "tipo": "gasto", "monto": "0.00", "fecha": "2026-06-01"
    })
    assert r_monto_cero.status_code == 422

    # Incoherencia de tipo en update (categoría 2 es gasto, se envía ingreso)
    r_incoherente = client.put(f"/api/movimientos/{mov_id}", json={
        "id_categoria": 2, "tipo": "ingreso", "monto": "100.00", "fecha": "2026-06-01"
    })
    assert r_incoherente.status_code == 400
    assert "Incoherencia de tipo" in r_incoherente.json()["detail"]


# =============================================================================
# PRUEBAS DE ELIMINACIÓN
# =============================================================================

def test_api_eliminar_movimiento_exitoso(client: TestClient):
    """21. Eliminar movimiento existente (Status 200)."""
    r_crear = client.post("/api/movimientos", json={
        "id_categoria": 1, "tipo": "ingreso", "monto": "3000.00", "fecha": "2026-06-01"
    })
    mov_id = r_crear.json()["id_movimiento"]

    response = client.delete(f"/api/movimientos/{mov_id}")
    assert response.status_code == 200
    assert "eliminado con éxito" in response.json()["mensaje"]

    # Verificar que ya no existe
    r_del_again = client.delete(f"/api/movimientos/{mov_id}")
    assert r_del_again.status_code == 404


def test_api_eliminar_movimiento_inexistente(client: TestClient):
    """22. Rechazar eliminación de movimiento inexistente (Status 404)."""
    response = client.delete("/api/movimientos/88888")
    assert response.status_code == 404
    assert "no existe" in response.json()["detail"]


def test_api_eliminar_movimiento_propio(client: TestClient):
    """23. El propietario puede eliminar su movimiento (Status 200)."""
    r_crear = client.post("/api/movimientos", json={
        "id_categoria": 1, "tipo": "ingreso", "monto": "1200.00", "fecha": "2026-06-02"
    })
    mov_id = r_crear.json()["id_movimiento"]

    response = client.delete(f"/api/movimientos/{mov_id}")
    assert response.status_code == 200
    assert "eliminado con éxito" in response.json()["mensaje"]


def test_api_eliminar_movimiento_de_otro_usuario_rechazado(
    client: TestClient, client_usuario_2: TestClient
):
    """24. Un usuario no puede eliminar el movimiento de otro (Status 400)."""
    # Movimiento perteneciente al usuario 1
    r_crear = client.post("/api/movimientos", json={
        "id_categoria": 2, "tipo": "gasto", "monto": "450.00", "fecha": "2026-06-03"
    })
    mov_id = r_crear.json()["id_movimiento"]

    # El usuario 2, con su propio token, intenta borrarlo.
    response = client_usuario_2.delete(f"/api/movimientos/{mov_id}")
    assert response.status_code == 400
    assert "no tiene permisos" in response.json()["detail"].lower()

    # El movimiento del usuario 1 sigue existiendo
    r_lista = client.get("/api/movimientos")
    assert any(m["id_movimiento"] == mov_id for m in r_lista.json())
