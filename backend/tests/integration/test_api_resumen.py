from decimal import Decimal
import pytest
from fastapi.testclient import TestClient


def _crear_movimiento(client: TestClient, tipo: str, monto: str, fecha: str) -> None:
    """Registra un movimiento a través de la API para el usuario 1."""
    payload = {
        "id_usuario": 1,
        "id_categoria": 1 if tipo == "ingreso" else 2,
        "tipo": tipo,
        "monto": monto,
        "fecha": fecha,
    }
    response = client.post("/api/movimientos", json=payload)
    assert response.status_code == 201


# =============================================================================
# CÁLCULO DEL RESUMEN
# =============================================================================

def test_api_resumen_con_ingresos_y_gastos(client: TestClient):
    """1. Resumen con ingresos y gastos (Status 200)."""
    _crear_movimiento(client, "ingreso", "3500000.00", "2026-08-01")
    _crear_movimiento(client, "gasto", "1200000.00", "2026-08-10")
    _crear_movimiento(client, "gasto", "900000.00", "2026-08-25")

    response = client.get("/api/resumen", params={"id_usuario": 1, "mes": "2026-08"})
    assert response.status_code == 200

    data = response.json()
    assert data["id_usuario"] == 1
    assert data["mes"] == "2026-08"
    assert Decimal(data["total_ingresos"]) == Decimal("3500000.00")
    assert Decimal(data["total_gastos"]) == Decimal("2100000.00")
    assert Decimal(data["balance"]) == Decimal("1400000.00")


def test_api_resumen_balance_calculado_por_backend(client: TestClient):
    """2. El balance lo calcula el backend: ingresos - gastos."""
    _crear_movimiento(client, "ingreso", "2000000.00", "2026-08-02")
    _crear_movimiento(client, "gasto", "750000.00", "2026-08-12")

    data = client.get("/api/resumen", params={"id_usuario": 1, "mes": "2026-08"}).json()

    assert Decimal(data["balance"]) == Decimal(data["total_ingresos"]) - Decimal(data["total_gastos"])
    assert Decimal(data["balance"]) == Decimal("1250000.00")


def test_api_resumen_solo_ingresos(client: TestClient):
    """8. Mes únicamente con ingresos."""
    _crear_movimiento(client, "ingreso", "1500000.00", "2026-08-05")
    _crear_movimiento(client, "ingreso", "500000.00", "2026-08-20")

    data = client.get("/api/resumen", params={"id_usuario": 1, "mes": "2026-08"}).json()

    assert Decimal(data["total_ingresos"]) == Decimal("2000000.00")
    assert Decimal(data["total_gastos"]) == Decimal("0.00")
    assert Decimal(data["balance"]) == Decimal("2000000.00")


def test_api_resumen_solo_gastos(client: TestClient):
    """9. Mes únicamente con gastos."""
    _crear_movimiento(client, "gasto", "450000.00", "2026-08-05")
    _crear_movimiento(client, "gasto", "150000.00", "2026-08-18")

    data = client.get("/api/resumen", params={"id_usuario": 1, "mes": "2026-08"}).json()

    assert Decimal(data["total_ingresos"]) == Decimal("0.00")
    assert Decimal(data["total_gastos"]) == Decimal("600000.00")
    assert Decimal(data["balance"]) == Decimal("-600000.00")


def test_api_resumen_balance_negativo(client: TestClient):
    """10. Un balance negativo se devuelve con 200, no como error."""
    _crear_movimiento(client, "ingreso", "1000000.00", "2026-08-01")
    _crear_movimiento(client, "gasto", "1750000.50", "2026-08-15")

    response = client.get("/api/resumen", params={"id_usuario": 1, "mes": "2026-08"})
    assert response.status_code == 200
    assert Decimal(response.json()["balance"]) == Decimal("-750000.50")


def test_api_resumen_precision_monetaria(client: TestClient):
    """11. Los importes conservan dos decimales exactos en el JSON."""
    for monto in ("1000.10", "2000.20", "3000.30"):
        _crear_movimiento(client, "ingreso", monto, "2026-08-03")
    _crear_movimiento(client, "gasto", "0.30", "2026-08-04")

    data = client.get("/api/resumen", params={"id_usuario": 1, "mes": "2026-08"}).json()

    assert Decimal(data["total_ingresos"]) == Decimal("6000.60")
    assert Decimal(data["total_gastos"]) == Decimal("0.30")
    assert Decimal(data["balance"]) == Decimal("6000.30")


def test_api_resumen_solo_incluye_el_mes_solicitado(client: TestClient):
    """El resumen aísla el periodo pedido de los meses adyacentes."""
    _crear_movimiento(client, "ingreso", "999.00", "2026-07-31")
    _crear_movimiento(client, "ingreso", "100.00", "2026-08-15")
    _crear_movimiento(client, "ingreso", "888.00", "2026-09-01")

    data = client.get("/api/resumen", params={"id_usuario": 1, "mes": "2026-08"}).json()

    assert Decimal(data["total_ingresos"]) == Decimal("100.00")


# =============================================================================
# CASOS SIN MOVIMIENTOS
# =============================================================================

def test_api_resumen_usuario_sin_movimientos(client: TestClient):
    """6. Usuario sin movimientos: 200 con totales en cero."""
    response = client.get("/api/resumen", params={"id_usuario": 1, "mes": "2026-08"})
    assert response.status_code == 200

    data = response.json()
    assert Decimal(data["total_ingresos"]) == Decimal("0.00")
    assert Decimal(data["total_gastos"]) == Decimal("0.00")
    assert Decimal(data["balance"]) == Decimal("0.00")


def test_api_resumen_mes_sin_movimientos(client: TestClient):
    """7. Mes sin movimientos aunque el usuario tenga historial: 200 con ceros."""
    _crear_movimiento(client, "ingreso", "3000000.00", "2026-07-15")

    response = client.get("/api/resumen", params={"id_usuario": 1, "mes": "2026-08"})
    assert response.status_code == 200

    data = response.json()
    assert Decimal(data["total_ingresos"]) == Decimal("0.00")
    assert Decimal(data["balance"]) == Decimal("0.00")


# =============================================================================
# VALIDACIONES
# =============================================================================

def test_api_resumen_usuario_inexistente(client: TestClient):
    """3. Usuario inexistente (Status 404)."""
    response = client.get("/api/resumen", params={"id_usuario": 999, "mes": "2026-08"})
    assert response.status_code == 404
    assert "999" in response.json()["detail"]


@pytest.mark.parametrize("mes_invalido", ["2026-8", "agosto", "2026/08", "2026"])
def test_api_resumen_mes_formato_invalido(client: TestClient, mes_invalido):
    """4. Mes con formato inválido (Status 400)."""
    response = client.get("/api/resumen", params={"id_usuario": 1, "mes": mes_invalido})
    assert response.status_code == 400
    assert "detail" in response.json()


@pytest.mark.parametrize("mes_inexistente", ["2026-13", "2026-00"])
def test_api_resumen_mes_inexistente(client: TestClient, mes_inexistente):
    """5. Mes inexistente (Status 400)."""
    response = client.get("/api/resumen", params={"id_usuario": 1, "mes": mes_inexistente})
    assert response.status_code == 400


def test_api_resumen_sin_parametro_mes(client: TestClient):
    """Falta un parámetro obligatorio (Status 422)."""
    response = client.get("/api/resumen", params={"id_usuario": 1})
    assert response.status_code == 422


def test_api_resumen_id_usuario_invalido(client: TestClient):
    """id_usuario debe ser un entero positivo (Status 422)."""
    response = client.get("/api/resumen", params={"id_usuario": 0, "mes": "2026-08"})
    assert response.status_code == 422


def test_api_resumen_normaliza_el_mes_devuelto(client: TestClient):
    """El mes se devuelve normalizado a YYYY-MM."""
    data = client.get("/api/resumen", params={"id_usuario": 1, "mes": " 2026-08 "}).json()
    assert data["mes"] == "2026-08"
