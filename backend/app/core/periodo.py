"""
Utilidades de interpretación de periodos mensuales (formato YYYY-MM).

Se aísla aquí porque la conversión de un mes a un rango de fechas es una regla
de dominio pura, sin dependencias de HTTP ni de base de datos: puede probarse
de forma independiente y evita duplicar la validación en cada servicio que
trabaje con periodos mensuales.
"""

import re
from dataclasses import dataclass
from datetime import date

from app.core.exceptions import ValidationException

# Formato aceptado para el parámetro `mes`.
FORMATO_MES = "YYYY-MM"

# Rango de años admitido. El límite inferior es coherente con la restricción
# chk_mov_fecha del esquema, que rechaza movimientos anteriores al año 2000.
ANIO_MINIMO = 2000
ANIO_MAXIMO = 2999

_PATRON_MES = re.compile(r"^(\d{4})-(\d{2})$")


@dataclass(frozen=True)
class PeriodoMensual:
    """
    Periodo mensual normalizado, expresado como rango semiabierto de fechas.

    El rango es [inicio, fin_exclusivo): incluye el primer día del mes y excluye
    el primer día del mes siguiente. Esta forma evita tener que calcular el
    último día de cada mes y permite comparar la columna `fecha` sin envolverla
    en ninguna función SQL, de modo que el índice idx_mov_usuario_fecha sigue
    siendo utilizable.
    """
    mes: str
    anio: int
    numero_mes: int
    inicio: date
    fin_exclusivo: date


def parse_periodo_mensual(mes: str) -> PeriodoMensual:
    """
    Convierte una cadena 'YYYY-MM' en un PeriodoMensual validado.

    Lanza ValidationException (HTTP 400) si el formato no es correcto, si el mes
    está fuera del rango 01-12 o si el año queda fuera del rango admitido.
    """
    if mes is None:
        raise ValidationException(
            f"El parámetro 'mes' es obligatorio y debe tener el formato {FORMATO_MES}."
        )

    valor = mes.strip()
    coincidencia = _PATRON_MES.match(valor)
    if not coincidencia:
        raise ValidationException(
            f"El mes '{mes}' no tiene un formato válido. Se espera {FORMATO_MES}, por ejemplo '2026-08'."
        )

    anio = int(coincidencia.group(1))
    numero_mes = int(coincidencia.group(2))

    if not 1 <= numero_mes <= 12:
        raise ValidationException(
            f"El mes '{mes}' no existe: el número de mes debe estar entre 01 y 12."
        )

    if not ANIO_MINIMO <= anio <= ANIO_MAXIMO:
        raise ValidationException(
            f"El año del periodo '{mes}' debe estar entre {ANIO_MINIMO} y {ANIO_MAXIMO}."
        )

    return PeriodoMensual(
        mes=f"{anio:04d}-{numero_mes:02d}",
        anio=anio,
        numero_mes=numero_mes,
        inicio=date(anio, numero_mes, 1),
        fin_exclusivo=_primer_dia_mes_siguiente(anio, numero_mes),
    )


def _primer_dia_mes_siguiente(anio: int, numero_mes: int) -> date:
    """Calcula el primer día del mes siguiente, gestionando el cambio de año."""
    if numero_mes == 12:
        return date(anio + 1, 1, 1)
    return date(anio, numero_mes + 1, 1)
