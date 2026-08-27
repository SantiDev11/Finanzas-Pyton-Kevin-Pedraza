"""
Pruebas de integración de los endpoints analíticos.

Cubren:
1. Predicción con datos suficientes.
2. Predicción sin datos.
3. Predicción sin token y aislamiento por usuario.
4. Anomalías con gasto atípico.
5. Anomalías sin anomalías.
6. Anomalías sin token y aislamiento por usuario.
7. Anomalías sin movimientos.
"""

from fastapi.testclient import TestClient


def _seed_usuario_y_categorias(client: TestClient) -> dict:
    """
    Helper: crea las categorías de prueba en la cuenta autenticada.

    Ya no crea un usuario: la analítica se ejecuta siempre sobre el usuario del
    token, así que las categorías deben pertenecer a ese mismo usuario.
    """
    # Nombres propios de estas pruebas: el usuario 1 ya tiene sembradas
    # "Salario" y "Alimentación" desde conftest, y repetirlas daría 409.
    r_cat_gasto = client.post("/api/categorias", json={
        "nombre": "Analitica Gastos", "tipo": "gasto"
    })
    assert r_cat_gasto.status_code == 201, r_cat_gasto.text
    cat_gasto_id = r_cat_gasto.json()["id_categoria"]

    r_cat_ingreso = client.post("/api/categorias", json={
        "nombre": "Analitica Ingresos", "tipo": "ingreso"
    })
    assert r_cat_ingreso.status_code == 201, r_cat_ingreso.text
    cat_ingreso_id = r_cat_ingreso.json()["id_categoria"]

    return {
        "cat_gasto_id": cat_gasto_id,
        "cat_ingreso_id": cat_ingreso_id,
    }


def _seed_gastos_mensuales(client: TestClient, ids: dict, meses: int = 6):
    """Helper: crea gastos mensuales durante `meses` meses para predicción."""
    for i in range(1, meses + 1):
        monto = str(100000 + i * 20000)
        mes = str(i).zfill(2)
        client.post("/api/movimientos", json={
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

    response = client.get("/api/analitica/prediccion")
    assert response.status_code == 200

    data = response.json()
    assert data["id_usuario"] == 1
    assert data["mes_predicho"] is not None
    assert data["gasto_estimado"] > 0
    assert data["confianza"] in ("media", "alta")
    assert data["meses_procesados"] == 4
    assert "Regresión Lineal" in data["razon"]


def test_api_prediccion_confianza_alta_con_6_meses(client: TestClient):
    """2. Predicción con ≥6 meses → confianza alta."""
    ids = _seed_usuario_y_categorias(client)
    _seed_gastos_mensuales(client, ids, meses=6)

    response = client.get("/api/analitica/prediccion")
    assert response.status_code == 200
    assert response.json()["confianza"] == "alta"
    assert response.json()["meses_procesados"] == 6


def test_api_prediccion_sin_datos_gasto_cero(client: TestClient):
    """3. Sin gastos → gasto_estimado = 0, confianza baja."""
    _seed_usuario_y_categorias(client)  # solo las categorías; sin movimientos

    response = client.get("/api/analitica/prediccion")
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
            "id_categoria": ids["cat_ingreso_id"],
            "tipo": "ingreso",
            "monto": "3000000.00",
            "fecha": f"2026-{mes}-01",
        })

    response = client.get("/api/analitica/prediccion")
    assert response.status_code == 200
    assert response.json()["gasto_estimado"] == 0.0


def test_api_prediccion_sin_token(client_anonimo: TestClient):
    """
    5. Sin token, la predicción responde 401.

    Sustituye a la antigua prueba de "usuario inexistente": ya no se puede
    pedir la predicción de una cuenta arbitraria, así que el caso a cubrir es
    el acceso sin autenticar.
    """
    response = client_anonimo.get("/api/analitica/prediccion")
    assert response.status_code == 401


def test_api_prediccion_aislada_por_usuario(
    client: TestClient, client_usuario_2: TestClient
):
    """5b. La predicción solo usa los gastos del usuario autenticado."""
    ids = _seed_usuario_y_categorias(client)
    _seed_gastos_mensuales(client, ids, meses=6)

    # El usuario 2 no tiene gastos: su predicción no puede verse afectada.
    data_u2 = client_usuario_2.get("/api/analitica/prediccion").json()
    assert data_u2["id_usuario"] == 2
    assert data_u2["meses_procesados"] == 0
    assert data_u2["gasto_estimado"] == 0.0


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
            "id_categoria": ids["cat_gasto_id"],
            "tipo": "gasto",
            "monto": "100000.00",
            "fecha": f"2026-{mes}-10",
            "descripcion": f"Gasto normal {i}",
        })

    # Crear un gasto extraordinario
    client.post("/api/movimientos", json={
        "id_categoria": ids["cat_gasto_id"],
        "tipo": "gasto",
        "monto": "5000000.00",
        "fecha": "2026-06-15",
        "descripcion": "Compra extraordinaria",
    })

    response = client.get("/api/analitica/anomalias")
    assert response.status_code == 200

    data = response.json()
    assert data["id_usuario"] == 1
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
            "id_categoria": ids["cat_gasto_id"],
            "tipo": "gasto",
            "monto": "200000.00",
            "fecha": f"2026-{mes}-10",
        })

    response = client.get("/api/analitica/anomalias")
    assert response.status_code == 200
    assert response.json()["total_anomalias"] == 0
    assert response.json()["anomalias"] == []


def test_api_anomalias_sin_movimientos(client: TestClient):
    """8. Sin movimientos → total_anomalias = 0, lista vacía."""
    _seed_usuario_y_categorias(client)  # solo las categorías; sin movimientos

    response = client.get("/api/analitica/anomalias")
    assert response.status_code == 200
    assert response.json()["total_gastos_analizados"] == 0
    assert response.json()["total_anomalias"] == 0
    assert response.json()["anomalias"] == []


def test_api_anomalias_sin_token(client_anonimo: TestClient):
    """9. Sin token, las anomalías responden 401."""
    response = client_anonimo.get("/api/analitica/anomalias")
    assert response.status_code == 401


def test_api_anomalias_aisladas_por_usuario(
    client: TestClient, client_usuario_2: TestClient
):
    """9b. Las anomalías solo analizan los gastos del usuario autenticado."""
    ids = _seed_usuario_y_categorias(client)
    # Con ddof=1, el |z| máximo posible es (n-1)/raíz(n): con 4 gastos vale
    # exactamente 1.5 y nunca superaría el umbral. Por eso se usan 6.
    for monto, fecha in (("100000.00", "2026-01-05"), ("110000.00", "2026-01-10"),
                         ("105000.00", "2026-01-15"), ("98000.00", "2026-01-18"),
                         ("102000.00", "2026-01-19"), ("5000000.00", "2026-01-20")):
        client.post("/api/movimientos", json={
            "id_categoria": ids["cat_gasto_id"], "tipo": "gasto",
            "monto": monto, "fecha": fecha,
        })

    # El usuario 1 sí tiene una anomalía; el usuario 2 no ve nada.
    data_u1 = client.get("/api/analitica/anomalias").json()
    assert data_u1["total_anomalias"] >= 1

    data_u2 = client_usuario_2.get("/api/analitica/anomalias").json()
    assert data_u2["id_usuario"] == 2
    assert data_u2["total_gastos_analizados"] == 0
    assert data_u2["anomalias"] == []
