"""
Pruebas de integración de los endpoints analíticos.

Cubren:
1. Predicción con datos suficientes.
2. Predicción sin datos.
3. Predicción con usuario inexistente.
4. Anomalías con gasto atípico.
5. Anomalías sin anomalías.
6. Anomalías con usuario inexistente.
7. Anomalías sin movimientos.
"""

from fastapi.testclient import TestClient


def _seed_usuario_y_categorias(client: TestClient) -> dict:
    """Helper: crea un usuario y sus categorías de prueba. Retorna IDs."""
    r_user = client.post("/api/usuarios", json={
        "nombre": "Ana Test", "correo": "ana@test.com", "contrasena": "Password123*"
    })
    u_id = r_user.json()["id_usuario"]

    r_cat_gasto = client.post("/api/categorias", json={
        "nombre": "Alimentacion", "tipo": "gasto", "id_usuario": u_id
    })
    cat_gasto_id = r_cat_gasto.json()["id_categoria"]

    r_cat_ingreso = client.post("/api/categorias", json={
        "nombre": "Salario", "tipo": "ingreso", "id_usuario": u_id
    })
    cat_ingreso_id = r_cat_ingreso.json()["id_categoria"]

    return {
        "id_usuario": u_id,
        "cat_gasto_id": cat_gasto_id,
        "cat_ingreso_id": cat_ingreso_id,
    }


def _seed_gastos_mensuales(client: TestClient, ids: dict, meses: int = 6):
    """Helper: crea gastos mensuales durante `meses` meses para predicción."""
    for i in range(1, meses + 1):
        monto = str(100000 + i * 20000)
        mes = str(i).zfill(2)
        client.post("/api/movimientos", json={
            "id_usuario": ids["id_usuario"],
            "id_categoria": ids["cat_gasto_id"],
            "tipo": "gasto",
            "monto": monto + ".00",
            "fecha": f"2026-{mes}-15",
            "descripcion": f"Gasto mes {i}",
        })


# =============================================================================
# PREDICCIÓN
# =============================================================================

def test_api_prediccion_con_datos_suficientes(client: TestClient):
    """1. Predicción exitosa con ≥2 meses de historial (Status 200)."""
    ids = _seed_usuario_y_categorias(client)
    _seed_gastos_mensuales(client, ids, meses=4)

    response = client.get(f"/api/analitica/prediccion?id_usuario={ids['id_usuario']}")
    assert response.status_code == 200

    data = response.json()
    assert data["id_usuario"] == ids["id_usuario"]
    assert data["mes_predicho"] is not None
    assert data["gasto_estimado"] > 0
    assert data["confianza"] in ("media", "alta")
    assert data["meses_procesados"] == 4
    assert "Regresión Lineal" in data["razon"]


def test_api_prediccion_confianza_alta_con_6_meses(client: TestClient):
    """2. Predicción con ≥6 meses → confianza alta."""
    ids = _seed_usuario_y_categorias(client)
    _seed_gastos_mensuales(client, ids, meses=6)

    response = client.get(f"/api/analitica/prediccion?id_usuario={ids['id_usuario']}")
    assert response.status_code == 200
    assert response.json()["confianza"] == "alta"
    assert response.json()["meses_procesados"] == 6


def test_api_prediccion_sin_datos_gasto_cero(client: TestClient):
    """3. Sin gastos → gasto_estimado = 0, confianza baja."""
    ids = _seed_usuario_y_categorias(client)
    # No crear movimientos

    response = client.get(f"/api/analitica/prediccion?id_usuario={ids['id_usuario']}")
    assert response.status_code == 200

    data = response.json()
    assert data["gasto_estimado"] == 0.0
    assert data["confianza"] == "baja"
    assert data["meses_procesados"] == 0


def test_api_prediccion_solo_ingresos_no_cuenta(client: TestClient):
    """4. Solo ingresos (sin gastos) → gasto_estimado = 0."""
    ids = _seed_usuario_y_categorias(client)
    # Solo crear ingresos
    for i in range(1, 4):
        mes = str(i).zfill(2)
        client.post("/api/movimientos", json={
            "id_usuario": ids["id_usuario"],
            "id_categoria": ids["cat_ingreso_id"],
            "tipo": "ingreso",
            "monto": "3000000.00",
            "fecha": f"2026-{mes}-01",
        })

    response = client.get(f"/api/analitica/prediccion?id_usuario={ids['id_usuario']}")
    assert response.status_code == 200
    assert response.json()["gasto_estimado"] == 0.0


def test_api_prediccion_usuario_inexistente(client: TestClient):
    """5. Usuario inexistente → 404."""
    response = client.get("/api/analitica/prediccion?id_usuario=99999")
    assert response.status_code == 404
    assert "no existe" in response.json()["detail"]


# =============================================================================
# ANOMALÍAS
# =============================================================================

def test_api_anomalias_con_gasto_atipico(client: TestClient):
    """6. Detectar gasto atípico (Status 200)."""
    ids = _seed_usuario_y_categorias(client)

    # Crear gastos normales en la misma categoría
    for i in range(1, 6):
        mes = str(i).zfill(2)
        client.post("/api/movimientos", json={
            "id_usuario": ids["id_usuario"],
            "id_categoria": ids["cat_gasto_id"],
            "tipo": "gasto",
            "monto": "100000.00",
            "fecha": f"2026-{mes}-10",
            "descripcion": f"Gasto normal {i}",
        })

    # Crear un gasto extraordinario
    client.post("/api/movimientos", json={
        "id_usuario": ids["id_usuario"],
        "id_categoria": ids["cat_gasto_id"],
        "tipo": "gasto",
        "monto": "5000000.00",
        "fecha": "2026-06-15",
        "descripcion": "Compra extraordinaria",
    })

    response = client.get(f"/api/analitica/anomalias?id_usuario={ids['id_usuario']}")
    assert response.status_code == 200

    data = response.json()
    assert data["id_usuario"] == ids["id_usuario"]
    assert data["umbral_z_score"] == 1.5
    assert data["total_gastos_analizados"] == 6
    assert data["total_anomalias"] >= 1
    assert len(data["anomalias"]) >= 1

    # El gasto atípico debería estar en la lista
    anomalia = data["anomalias"][0]
    assert anomalia["monto"] == 5000000.0
    assert abs(anomalia["z_score"]) > 1.5
    assert "promedio_categoria" in anomalia


def test_api_anomalias_sin_anomalias(client: TestClient):
    """7. Gastos normales → sin anomalías, lista vacía (Status 200)."""
    ids = _seed_usuario_y_categorias(client)

    # Gastos uniformes
    for i in range(1, 5):
        mes = str(i).zfill(2)
        client.post("/api/movimientos", json={
            "id_usuario": ids["id_usuario"],
            "id_categoria": ids["cat_gasto_id"],
            "tipo": "gasto",
            "monto": "200000.00",
            "fecha": f"2026-{mes}-10",
        })

    response = client.get(f"/api/analitica/anomalias?id_usuario={ids['id_usuario']}")
    assert response.status_code == 200
    assert response.json()["total_anomalias"] == 0
    assert response.json()["anomalias"] == []


def test_api_anomalias_sin_movimientos(client: TestClient):
    """8. Sin movimientos → total_anomalias = 0, lista vacía."""
    ids = _seed_usuario_y_categorias(client)

    response = client.get(f"/api/analitica/anomalias?id_usuario={ids['id_usuario']}")
    assert response.status_code == 200
    assert response.json()["total_gastos_analizados"] == 0
    assert response.json()["total_anomalias"] == 0
    assert response.json()["anomalias"] == []


def test_api_anomalias_usuario_inexistente(client: TestClient):
    """9. Usuario inexistente → 404."""
    response = client.get("/api/analitica/anomalias?id_usuario=99999")
    assert response.status_code == 404
    assert "no existe" in response.json()["detail"]
