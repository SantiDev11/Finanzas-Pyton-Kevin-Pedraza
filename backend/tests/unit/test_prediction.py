"""
Pruebas unitarias del módulo analytics/prediction.py.

Cubren:
1. Predicción con datos suficientes (≥2 meses).
2. Datos insuficientes (<2 meses).
3. Sin datos (lista vacía).
4. Solo utilizar gastos (verificado por diseño: la función solo recibe gastos).
5. Resultado numérico válido (no negativo).
6. Próximo mes calculado correctamente.
7. Modelo entrenado correctamente (tendencia ascendente → predicción mayor).
"""

from datetime import date
from decimal import Decimal

from app.analytics.prediction import predecir_gasto_proximo_mes


def test_prediccion_sin_datos():
    """Sin datos de gastos → gasto_estimado = 0, confianza baja, mes_predicho None."""
    resultado = predecir_gasto_proximo_mes([])
    assert resultado["gasto_estimado"] == 0.0
    assert resultado["confianza"] == "baja"
    assert resultado["mes_predicho"] is None
    assert resultado["meses_procesados"] == 0


def test_prediccion_un_mes_usa_promedio():
    """Con un solo mes → promedio simple, confianza baja."""
    gastos = [
        {"fecha": date(2026, 3, 5), "monto": Decimal("200000.00")},
        {"fecha": date(2026, 3, 15), "monto": Decimal("100000.00")},
    ]
    resultado = predecir_gasto_proximo_mes(gastos)
    assert resultado["confianza"] == "baja"
    assert resultado["meses_procesados"] == 1
    assert resultado["mes_predicho"] == "2026-04"
    assert resultado["gasto_estimado"] == 300000.00  # 200k + 100k = 300k promedio


def test_prediccion_dos_meses_usa_regresion():
    """Con 2 meses → regresión lineal, confianza media."""
    gastos = [
        {"fecha": date(2026, 1, 10), "monto": Decimal("500000.00")},
        {"fecha": date(2026, 2, 10), "monto": Decimal("600000.00")},
    ]
    resultado = predecir_gasto_proximo_mes(gastos)
    assert resultado["confianza"] == "media"
    assert resultado["meses_procesados"] == 2
    assert resultado["mes_predicho"] == "2026-03"
    assert resultado["gasto_estimado"] > 0
    assert "Regresión Lineal" in resultado["razon"]


def test_prediccion_seis_meses_confianza_alta():
    """Con ≥6 meses → confianza alta."""
    gastos = []
    for i in range(1, 7):
        gastos.append({"fecha": date(2026, i, 15), "monto": Decimal(str(100000 * i))})
    resultado = predecir_gasto_proximo_mes(gastos)
    assert resultado["confianza"] == "alta"
    assert resultado["meses_procesados"] == 6
    assert resultado["mes_predicho"] == "2026-07"


def test_prediccion_tendencia_ascendente():
    """Una tendencia ascendente debería producir una predicción mayor al último mes."""
    gastos = [
        {"fecha": date(2026, 1, 1), "monto": Decimal("100000")},
        {"fecha": date(2026, 2, 1), "monto": Decimal("200000")},
        {"fecha": date(2026, 3, 1), "monto": Decimal("300000")},
        {"fecha": date(2026, 4, 1), "monto": Decimal("400000")},
    ]
    resultado = predecir_gasto_proximo_mes(gastos)
    # La regresión lineal perfecta debería predecir ~500000
    assert resultado["gasto_estimado"] >= 400000  # Mayor que el último mes
    assert resultado["mes_predicho"] == "2026-05"


def test_prediccion_nunca_negativa():
    """Una tendencia descendente no debería producir predicción negativa."""
    gastos = [
        {"fecha": date(2026, 1, 1), "monto": Decimal("500000")},
        {"fecha": date(2026, 2, 1), "monto": Decimal("300000")},
        {"fecha": date(2026, 3, 1), "monto": Decimal("100000")},
        {"fecha": date(2026, 4, 1), "monto": Decimal("10000")},
        {"fecha": date(2026, 5, 1), "monto": Decimal("1000")},
    ]
    resultado = predecir_gasto_proximo_mes(gastos)
    assert resultado["gasto_estimado"] >= 0.0


def test_prediccion_multiples_gastos_mismo_mes():
    """Varios gastos en un mismo mes se suman correctamente."""
    gastos = [
        {"fecha": date(2026, 1, 5), "monto": Decimal("100000")},
        {"fecha": date(2026, 1, 15), "monto": Decimal("50000")},
        {"fecha": date(2026, 1, 25), "monto": Decimal("30000")},
        {"fecha": date(2026, 2, 10), "monto": Decimal("200000")},
    ]
    resultado = predecir_gasto_proximo_mes(gastos)
    # Mes 1: 180000, Mes 2: 200000 → serie creciente
    assert resultado["meses_procesados"] == 2
    assert resultado["mes_predicho"] == "2026-03"
    assert resultado["gasto_estimado"] > 0


def test_prediccion_orden_cronologico():
    """Los datos desordenados deben producir la misma predicción que los ordenados."""
    gastos_desorden = [
        {"fecha": date(2026, 3, 1), "monto": Decimal("300000")},
        {"fecha": date(2026, 1, 1), "monto": Decimal("100000")},
        {"fecha": date(2026, 2, 1), "monto": Decimal("200000")},
    ]
    gastos_orden = [
        {"fecha": date(2026, 1, 1), "monto": Decimal("100000")},
        {"fecha": date(2026, 2, 1), "monto": Decimal("200000")},
        {"fecha": date(2026, 3, 1), "monto": Decimal("300000")},
    ]
    r_desorden = predecir_gasto_proximo_mes(gastos_desorden)
    r_orden = predecir_gasto_proximo_mes(gastos_orden)
    assert r_desorden["gasto_estimado"] == r_orden["gasto_estimado"]
    assert r_desorden["mes_predicho"] == r_orden["mes_predicho"]
