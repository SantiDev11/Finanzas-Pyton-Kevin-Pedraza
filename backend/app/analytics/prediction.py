"""
Módulo de predicción de gastos futuros utilizando Regresión Lineal.

Flujo de procesamiento Pandas:
1. Recibe los registros de gastos como lista de diccionarios (del repositorio).
2. Construye un DataFrame con columnas: fecha, monto.
3. Convierte `fecha` a datetime con pd.to_datetime().
4. Agrupa por periodo mensual con dt.to_period('M') + groupby().
5. Calcula el gasto total mensual con .sum().
6. Genera una variable temporal numérica (índice ordinal 0, 1, 2, …) como feature X.
7. Entrena LinearRegression con X = índice temporal, y = gasto mensual.
8. Predice el gasto del siguiente mes cronológico.

Requisito mínimo: 2 meses de historial para entrenar la regresión.
Con 1 solo mes se devuelve el promedio simple con confianza 'baja'.
Con 0 meses se indica que no existen datos.
"""

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


# Mínimo de meses para regresión lineal (con < 2 puntos no hay pendiente).
MESES_MINIMOS_REGRESION = 2


def predecir_gasto_proximo_mes(gastos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Predice el gasto total del próximo mes a partir de los gastos históricos.

    Parámetros
    ----------
    gastos : list[dict]
        Lista de registros de gastos con claves 'fecha' (date) y 'monto' (Decimal/float).

    Retorna
    -------
    dict con:
        - mes_predicho (str): periodo YYYY-MM del mes predicho.
        - gasto_estimado (float): valor numérico positivo predicho.
        - confianza (str): 'alta' (≥6 meses), 'media' (2-5 meses), 'baja' (<2 meses).
        - razon (str): explicación del método empleado.
        - meses_procesados (int): cantidad de meses con los que se entrenó.
    """
    if not gastos:
        return {
            "mes_predicho": None,
            "gasto_estimado": 0.0,
            "confianza": "baja",
            "razon": "Sin registros de gastos para este usuario.",
            "meses_procesados": 0,
        }

    # ── Paso 1: Construir DataFrame ──────────────────────────────────────
    df = pd.DataFrame(gastos)

    # ── Paso 2: Convertir fechas a datetime ──────────────────────────────
    df["fecha"] = pd.to_datetime(df["fecha"])

    # ── Paso 3: Convertir montos a float (vienen como Decimal) ───────────
    df["monto"] = df["monto"].astype(float)

    # ── Paso 4: Agrupar por mes y sumar gastos ───────────────────────────
    # .to_period('M') agrupa por mes calendario, .sum() agrega los montos.
    df["mes"] = df["fecha"].dt.to_period("M")
    serie_mensual = df.groupby("mes")["monto"].sum().reset_index()

    # Ordenar cronológicamente (crucial para la regresión temporal).
    serie_mensual = serie_mensual.sort_values("mes").reset_index(drop=True)
    cant_meses = len(serie_mensual)

    # ── Calcular el siguiente mes ────────────────────────────────────────
    ultimo_periodo = serie_mensual["mes"].iloc[-1]
    siguiente_periodo = ultimo_periodo + 1  # pd.Period aritmética
    mes_predicho = str(siguiente_periodo)  # "YYYY-MM"

    # ── Caso borde: menos de 2 meses → promedio simple ──────────────────
    if cant_meses < MESES_MINIMOS_REGRESION:
        promedio = float(serie_mensual["monto"].mean())
        return {
            "mes_predicho": mes_predicho,
            "gasto_estimado": round(max(0.0, promedio), 2),
            "confianza": "baja",
            "razon": f"Datos insuficientes (<{MESES_MINIMOS_REGRESION} meses). Se usó promedio simple.",
            "meses_procesados": cant_meses,
        }

    # ── Paso 5: Variable independiente numérica ──────────────────────────
    serie_mensual["n_mes"] = range(cant_meses)
    X = serie_mensual[["n_mes"]].values  # shape (n, 1)
    y = serie_mensual["monto"].values    # shape (n,)

    # ── Paso 6: Entrenar LinearRegression ────────────────────────────────
    modelo = LinearRegression()
    modelo.fit(X, y)

    # ── Paso 7: Predecir siguiente mes ───────────────────────────────────
    siguiente_idx = np.array([[cant_meses]])
    prediccion = modelo.predict(siguiente_idx)[0]

    # Evitar predicciones negativas (no tiene sentido económico).
    prediccion_final = max(0.0, float(prediccion))

    # Nivel de confianza basado en la cantidad de datos históricos.
    confianza = "alta" if cant_meses >= 6 else "media"

    return {
        "mes_predicho": mes_predicho,
        "gasto_estimado": round(prediccion_final, 2),
        "confianza": confianza,
        "razon": f"Calculado con Regresión Lineal ({cant_meses} meses procesados).",
        "meses_procesados": cant_meses,
    }
