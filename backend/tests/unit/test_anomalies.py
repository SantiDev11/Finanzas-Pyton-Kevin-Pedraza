"""
Pruebas unitarias del módulo analytics/anomalies.py.

Cubren:
1. Detectar un gasto atípico.
2. No marcar gastos normales innecesariamente.
3. Z-Score calculado correctamente.
4. Umbral aplicado correctamente.
5. Sin anomalías (todos los gastos normales).
6. Desviación estándar igual a cero (un solo gasto por categoría).
7. Sin datos (lista vacía).
8. Múltiples categorías con anomalías independientes.
"""

from datetime import date
from decimal import Decimal

from app.analytics.anomalies import UMBRAL_Z_SCORE, detectar_anomalias


def test_anomalias_lista_vacia():
    """Sin gastos → lista vacía (no es error)."""
    resultado = detectar_anomalias([])
    assert resultado == []


def test_anomalias_sin_gastos_atipicos():
    """Gastos similares en una categoría → sin anomalías."""
    gastos = [
        {"id_movimiento": 1, "fecha": date(2026, 1, 5), "monto": Decimal("100000"), "id_categoria": 1, "descripcion": "Gasto 1"},
        {"id_movimiento": 2, "fecha": date(2026, 2, 5), "monto": Decimal("105000"), "id_categoria": 1, "descripcion": "Gasto 2"},
        {"id_movimiento": 3, "fecha": date(2026, 3, 5), "monto": Decimal("98000"), "id_categoria": 1, "descripcion": "Gasto 3"},
        {"id_movimiento": 4, "fecha": date(2026, 4, 5), "monto": Decimal("102000"), "id_categoria": 1, "descripcion": "Gasto 4"},
    ]
    resultado = detectar_anomalias(gastos)
    assert len(resultado) == 0


def test_anomalias_detecta_gasto_atipico():
    """Un gasto significativamente mayor debería ser detectado."""
    gastos = [
        {"id_movimiento": 1, "fecha": date(2026, 1, 5), "monto": Decimal("100000"), "id_categoria": 1, "descripcion": "Normal 1"},
        {"id_movimiento": 2, "fecha": date(2026, 2, 5), "monto": Decimal("100000"), "id_categoria": 1, "descripcion": "Normal 2"},
        {"id_movimiento": 3, "fecha": date(2026, 3, 5), "monto": Decimal("100000"), "id_categoria": 1, "descripcion": "Normal 3"},
        {"id_movimiento": 4, "fecha": date(2026, 4, 5), "monto": Decimal("100000"), "id_categoria": 1, "descripcion": "Normal 4"},
        {"id_movimiento": 5, "fecha": date(2026, 5, 5), "monto": Decimal("5000000"), "id_categoria": 1, "descripcion": "Gasto extraordinario"},
    ]
    resultado = detectar_anomalias(gastos)
    assert len(resultado) >= 1
    anomalia = resultado[0]
    assert anomalia["id_movimiento"] == 5
    assert anomalia["monto"] == 5000000.0
    assert abs(anomalia["z_score"]) > UMBRAL_Z_SCORE


def test_anomalias_z_score_correcto():
    """Verificar que el Z-Score se calcula correctamente para un caso con outlier claro."""
    # 5 valores normales ~100 + 1 outlier extremo de 5000.
    # Con ddof=1 (pandas default), el outlier debe superar |z| > 1.5.
    gastos = [
        {"id_movimiento": 1, "fecha": date(2026, 1, 1), "monto": Decimal("100"), "id_categoria": 1, "descripcion": None},
        {"id_movimiento": 2, "fecha": date(2026, 2, 1), "monto": Decimal("100"), "id_categoria": 1, "descripcion": None},
        {"id_movimiento": 3, "fecha": date(2026, 3, 1), "monto": Decimal("100"), "id_categoria": 1, "descripcion": None},
        {"id_movimiento": 4, "fecha": date(2026, 4, 1), "monto": Decimal("100"), "id_categoria": 1, "descripcion": None},
        {"id_movimiento": 5, "fecha": date(2026, 5, 1), "monto": Decimal("100"), "id_categoria": 1, "descripcion": None},
        {"id_movimiento": 6, "fecha": date(2026, 6, 1), "monto": Decimal("5000"), "id_categoria": 1, "descripcion": "Atípico"},
    ]
    resultado = detectar_anomalias(gastos)
    # El gasto de 5000 debería tener un z_score alto positivo
    assert len(resultado) >= 1
    atipico = [a for a in resultado if a["id_movimiento"] == 6]
    assert len(atipico) == 1
    assert atipico[0]["z_score"] > UMBRAL_Z_SCORE


def test_anomalias_umbral_respetado():
    """Con un umbral personalizado más alto, se detectan menos anomalías."""
    gastos = [
        {"id_movimiento": 1, "fecha": date(2026, 1, 1), "monto": Decimal("100"), "id_categoria": 1, "descripcion": None},
        {"id_movimiento": 2, "fecha": date(2026, 2, 1), "monto": Decimal("100"), "id_categoria": 1, "descripcion": None},
        {"id_movimiento": 3, "fecha": date(2026, 3, 1), "monto": Decimal("100"), "id_categoria": 1, "descripcion": None},
        {"id_movimiento": 4, "fecha": date(2026, 4, 1), "monto": Decimal("300"), "id_categoria": 1, "descripcion": "Medio atípico"},
    ]
    # Con umbral bajo (1.0), podría detectarse
    resultado_bajo = detectar_anomalias(gastos, umbral=1.0)
    # Con umbral alto (5.0), no debería detectarse
    resultado_alto = detectar_anomalias(gastos, umbral=5.0)
    assert len(resultado_bajo) >= len(resultado_alto)


def test_anomalias_desviacion_estandar_cero():
    """Con un solo gasto por categoría, std=0, z_score=0, no es anomalía."""
    gastos = [
        {"id_movimiento": 1, "fecha": date(2026, 1, 5), "monto": Decimal("100000"), "id_categoria": 1, "descripcion": "Único gasto"},
    ]
    resultado = detectar_anomalias(gastos)
    assert len(resultado) == 0  # z_score = 0, no supera el umbral


def test_anomalias_multiples_categorias():
    """Anomalías detectadas de forma independiente por categoría."""
    gastos = [
        # Categoría 1: 5 valores normales + 1 outlier extremo
        {"id_movimiento": 1, "fecha": date(2026, 1, 1), "monto": Decimal("100"), "id_categoria": 1, "descripcion": None},
        {"id_movimiento": 2, "fecha": date(2026, 2, 1), "monto": Decimal("100"), "id_categoria": 1, "descripcion": None},
        {"id_movimiento": 3, "fecha": date(2026, 3, 1), "monto": Decimal("100"), "id_categoria": 1, "descripcion": None},
        {"id_movimiento": 8, "fecha": date(2026, 5, 1), "monto": Decimal("100"), "id_categoria": 1, "descripcion": None},
        {"id_movimiento": 9, "fecha": date(2026, 6, 1), "monto": Decimal("100"), "id_categoria": 1, "descripcion": None},
        {"id_movimiento": 4, "fecha": date(2026, 4, 1), "monto": Decimal("5000"), "id_categoria": 1, "descripcion": "Atípico cat 1"},
        # Categoría 2: valores normales
        {"id_movimiento": 5, "fecha": date(2026, 1, 5), "monto": Decimal("50"), "id_categoria": 2, "descripcion": None},
        {"id_movimiento": 6, "fecha": date(2026, 2, 5), "monto": Decimal("55"), "id_categoria": 2, "descripcion": None},
        {"id_movimiento": 7, "fecha": date(2026, 3, 5), "monto": Decimal("48"), "id_categoria": 2, "descripcion": None},
    ]
    resultado = detectar_anomalias(gastos)
    # Solo debería detectar anomalía en categoría 1
    ids_detectados = [a["id_movimiento"] for a in resultado]
    assert 4 in ids_detectados
    # Categoría 2 no debería tener anomalías
    assert not any(a["id_categoria"] == 2 for a in resultado)


def test_anomalias_gastos_iguales_sin_anomalias():
    """Gastos exactamente iguales → std = 0 → z_score = 0 → sin anomalías."""
    gastos = [
        {"id_movimiento": i, "fecha": date(2026, i, 1), "monto": Decimal("200000"), "id_categoria": 1, "descripcion": None}
        for i in range(1, 6)
    ]
    resultado = detectar_anomalias(gastos)
    assert len(resultado) == 0


def test_anomalias_estructura_respuesta():
    """Verificar que cada anomalía devuelve todos los campos requeridos."""
    gastos = [
        {"id_movimiento": 1, "fecha": date(2026, 1, 1), "monto": Decimal("100"), "id_categoria": 1, "descripcion": "Desc 1"},
        {"id_movimiento": 2, "fecha": date(2026, 2, 1), "monto": Decimal("100"), "id_categoria": 1, "descripcion": "Desc 2"},
        {"id_movimiento": 3, "fecha": date(2026, 3, 1), "monto": Decimal("100"), "id_categoria": 1, "descripcion": "Desc 3"},
        {"id_movimiento": 4, "fecha": date(2026, 4, 1), "monto": Decimal("100"), "id_categoria": 1, "descripcion": "Desc 4"},
        {"id_movimiento": 5, "fecha": date(2026, 5, 1), "monto": Decimal("100"), "id_categoria": 1, "descripcion": "Desc 5"},
        {"id_movimiento": 6, "fecha": date(2026, 6, 1), "monto": Decimal("10000"), "id_categoria": 1, "descripcion": "Compra grande"},
    ]
    resultado = detectar_anomalias(gastos)
    assert len(resultado) >= 1
    anomalia = resultado[0]
    assert "id_movimiento" in anomalia
    assert "fecha" in anomalia
    assert "monto" in anomalia
    assert "id_categoria" in anomalia
    assert "promedio_categoria" in anomalia
    assert "z_score" in anomalia
    assert "descripcion" in anomalia
