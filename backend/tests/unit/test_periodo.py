from datetime import date
import pytest

from app.core.exceptions import ValidationException
from app.core.periodo import parse_periodo_mensual


def test_periodo_mes_valido_normal():
    """Un mes intermedio produce el rango semiabierto correcto."""
    periodo = parse_periodo_mensual("2026-08")
    assert periodo.mes == "2026-08"
    assert periodo.anio == 2026
    assert periodo.numero_mes == 8
    assert periodo.inicio == date(2026, 8, 1)
    assert periodo.fin_exclusivo == date(2026, 9, 1)


def test_periodo_diciembre_cambia_de_anio():
    """Diciembre debe avanzar al 1 de enero del año siguiente."""
    periodo = parse_periodo_mensual("2026-12")
    assert periodo.inicio == date(2026, 12, 1)
    assert periodo.fin_exclusivo == date(2027, 1, 1)


def test_periodo_febrero_bisiesto():
    """Febrero de un año bisiesto no requiere tratamiento especial con rango semiabierto."""
    periodo = parse_periodo_mensual("2028-02")
    assert periodo.inicio == date(2028, 2, 1)
    assert periodo.fin_exclusivo == date(2028, 3, 1)


def test_periodo_admite_espacios_alrededor():
    """Los espacios sobrantes no invalidan el periodo."""
    assert parse_periodo_mensual("  2026-08  ").mes == "2026-08"


@pytest.mark.parametrize(
    "mes_invalido",
    ["2026-13", "2026-00", "2026-99"],
)
def test_periodo_rechaza_meses_inexistentes(mes_invalido):
    """El número de mes fuera de 01-12 se rechaza."""
    with pytest.raises(ValidationException) as exc:
        parse_periodo_mensual(mes_invalido)
    assert exc.value.status_code == 400


@pytest.mark.parametrize(
    "mes_invalido",
    ["2026-8", "26-08", "2026/08", "agosto", "2026", "", "2026-08-01", "abcd-ef"],
)
def test_periodo_rechaza_formatos_invalidos(mes_invalido):
    """Cualquier cadena que no siga YYYY-MM se rechaza con 400."""
    with pytest.raises(ValidationException) as exc:
        parse_periodo_mensual(mes_invalido)
    assert exc.value.status_code == 400


def test_periodo_rechaza_none():
    """Un valor nulo se rechaza con un mensaje explícito."""
    with pytest.raises(ValidationException):
        parse_periodo_mensual(None)


@pytest.mark.parametrize("mes_fuera_de_rango", ["1999-12", "3000-01"])
def test_periodo_rechaza_anios_fuera_de_rango(mes_fuera_de_rango):
    """El año debe permanecer dentro del rango admitido por el esquema."""
    with pytest.raises(ValidationException):
        parse_periodo_mensual(mes_fuera_de_rango)
