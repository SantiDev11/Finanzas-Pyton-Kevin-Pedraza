"""
Módulo de detección de anomalías en gastos utilizando Z-Score por categoría.

Flujo de procesamiento Pandas:
1. Recibe los registros de gastos como lista de diccionarios.
2. Construye un DataFrame con columnas: id_movimiento, fecha, monto, id_categoria, descripcion.
3. Agrupa por categoría para calcular media y desviación estándar por grupo.
4. Realiza merge para asociar las estadísticas a cada gasto individual.
5. Calcula el Z-Score: z = (monto - media) / desviación_estándar.
6. Filtra los gastos cuyo |Z-Score| supera el umbral (por defecto 1.5, según el
   repositorio del instructor).
7. Devuelve la lista de anomalías con información útil.

Manejo de bordes:
- desviación estándar = 0 → z_score = 0 (no es anomalía).
- Sin gastos → lista vacía (no es un error).
- Insuficientes datos → lista vacía.
"""

from typing import Any, Dict, List

import numpy as np
import pandas as pd


# Umbral Z-Score definido por el repositorio del instructor (analitica.py línea 54).
UMBRAL_Z_SCORE = 1.5


def detectar_anomalias(
    gastos: List[Dict[str, Any]],
    umbral: float = UMBRAL_Z_SCORE,
) -> List[Dict[str, Any]]:
    """
    Detecta gastos atípicos usando Z-Score agrupado por categoría.

    Parámetros
    ----------
    gastos : list[dict]
        Registros de gastos con claves: id_movimiento, fecha, monto, id_categoria, descripcion.
    umbral : float
        Umbral de |Z-Score| para considerar un gasto como anomalía (default: 1.5).

    Retorna
    -------
    list[dict] con cada anomalía conteniendo:
        - id_movimiento (int)
        - fecha (str, YYYY-MM-DD)
        - monto (float)
        - id_categoria (int)
        - promedio_categoria (float)
        - z_score (float)
        - descripcion (str | None)
    """
    if not gastos:
        return []

    # ── Paso 1: Construir DataFrame ──────────────────────────────────────
    df = pd.DataFrame(gastos)

    # ── Paso 2: Convertir tipos ──────────────────────────────────────────
    df["monto"] = df["monto"].astype(float)
    df["fecha"] = pd.to_datetime(df["fecha"])

    # ── Paso 3: Estadísticas agrupadas por categoría ─────────────────────
    # groupby + agg calcula media y desviación estándar por categoría.
    # std con ddof=0 (desviación poblacional) para ser coherente con el
    # cálculo Z-Score manual: no se resta 1 grado de libertad.
    stats = (
        df.groupby("id_categoria")["monto"]
        .agg(["mean", "std"])
        .reset_index()
    )
    # Categorías con un solo gasto producen std=NaN. Se reemplazan por 0.
    stats["std"] = stats["std"].fillna(0)

    # ── Paso 4: Merge estadísticas al DataFrame de gastos ────────────────
    df = df.merge(stats, on="id_categoria", suffixes=("", "_stat"))

    # ── Paso 5: Calcular Z-Score ─────────────────────────────────────────
    # np.where evita la división por cero cuando std == 0.
    df["z_score"] = np.where(
        df["std"] > 0,
        (df["monto"] - df["mean"]) / df["std"],
        0.0,
    )

    # ── Paso 6: Filtrar por umbral ───────────────────────────────────────
    anomalias = df[df["z_score"].abs() > umbral]

    # ── Paso 7: Construir resultado serializable ─────────────────────────
    resultado: List[Dict[str, Any]] = []
    for _, row in anomalias.iterrows():
        resultado.append({
            "id_movimiento": int(row["id_movimiento"]),
            "fecha": row["fecha"].strftime("%Y-%m-%d"),
            "monto": round(float(row["monto"]), 2),
            "id_categoria": int(row["id_categoria"]),
            "promedio_categoria": round(float(row["mean"]), 2),
            "z_score": round(float(row["z_score"]), 2),
            "descripcion": row.get("descripcion"),
        })

    return resultado
