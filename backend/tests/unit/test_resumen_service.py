from datetime import date
from decimal import Decimal
import pytest

from app.core.exceptions import EntityNotFoundException, ValidationException
from app.services.resumen_service import ResumenService


def _sembrar(repo, tipo: str, monto: str, fecha: date, id_usuario: int = 1):
    """Inserta un movimiento directamente en el repositorio en memoria."""
    return repo.create(
        id_usuario=id_usuario,
        id_categoria=1 if tipo == "ingreso" else 2,
        tipo=tipo,
        monto=Decimal(monto),
        fecha=fecha,
        descripcion=None,
    )


# =============================================================================
# CÁLCULO DEL RESUMEN
# =============================================================================

def test_resumen_con_ingresos_y_gastos(resumen_service: ResumenService, fake_movimiento_repo):
    """1. Resumen de un usuario con ingresos y gastos en el mes."""
    _sembrar(fake_movimiento_repo, "ingreso", "3500000.00", date(2026, 8, 1))
    _sembrar(fake_movimiento_repo, "gasto", "1200000.00", date(2026, 8, 10))
    _sembrar(fake_movimiento_repo, "gasto", "900000.00", date(2026, 8, 25))

    res = resumen_service.obtener_resumen_mensual(id_usuario=1, mes="2026-08")

    assert res.id_usuario == 1
    assert res.mes == "2026-08"
    assert res.total_ingresos == Decimal("3500000.00")
    assert res.total_gastos == Decimal("2100000.00")


def test_resumen_calcula_balance_correctamente(resumen_service: ResumenService, fake_movimiento_repo):
    """2. El balance es exactamente ingresos - gastos."""
    _sembrar(fake_movimiento_repo, "ingreso", "3500000.00", date(2026, 8, 1))
    _sembrar(fake_movimiento_repo, "gasto", "2100000.00", date(2026, 8, 10))

    res = resumen_service.obtener_resumen_mensual(id_usuario=1, mes="2026-08")

    assert res.balance == Decimal("1400000.00")
    assert res.balance == res.total_ingresos - res.total_gastos


def test_resumen_solo_ingresos(resumen_service: ResumenService, fake_movimiento_repo):
    """8. Usuario con ingresos pero sin gastos en el mes."""
    _sembrar(fake_movimiento_repo, "ingreso", "1500000.00", date(2026, 8, 5))
    _sembrar(fake_movimiento_repo, "ingreso", "500000.00", date(2026, 8, 20))

    res = resumen_service.obtener_resumen_mensual(id_usuario=1, mes="2026-08")

    assert res.total_ingresos == Decimal("2000000.00")
    assert res.total_gastos == Decimal("0.00")
    assert res.balance == Decimal("2000000.00")


def test_resumen_solo_gastos(resumen_service: ResumenService, fake_movimiento_repo):
    """9. Usuario con gastos pero sin ingresos en el mes: balance negativo."""
    _sembrar(fake_movimiento_repo, "gasto", "450000.00", date(2026, 8, 5))
    _sembrar(fake_movimiento_repo, "gasto", "150000.00", date(2026, 8, 18))

    res = resumen_service.obtener_resumen_mensual(id_usuario=1, mes="2026-08")

    assert res.total_ingresos == Decimal("0.00")
    assert res.total_gastos == Decimal("600000.00")
    assert res.balance == Decimal("-600000.00")


def test_resumen_balance_negativo_es_valido(resumen_service: ResumenService, fake_movimiento_repo):
    """10. Un balance negativo (gastos > ingresos) es un resultado válido, no un error."""
    _sembrar(fake_movimiento_repo, "ingreso", "1000000.00", date(2026, 8, 1))
    _sembrar(fake_movimiento_repo, "gasto", "1750000.50", date(2026, 8, 15))

    res = resumen_service.obtener_resumen_mensual(id_usuario=1, mes="2026-08")

    assert res.balance == Decimal("-750000.50")
    assert res.balance < 0


def test_resumen_precision_decimal_sin_error_de_float(
    resumen_service: ResumenService, fake_movimiento_repo
):
    """11. Los importes se suman con Decimal exacto, sin arrastrar error binario."""
    for monto in ("1000.10", "2000.20", "3000.30"):
        _sembrar(fake_movimiento_repo, "ingreso", monto, date(2026, 8, 3))
    for monto in ("0.10", "0.20"):
        _sembrar(fake_movimiento_repo, "gasto", monto, date(2026, 8, 4))

    res = resumen_service.obtener_resumen_mensual(id_usuario=1, mes="2026-08")

    # Con float, 1000.10 + 2000.20 + 3000.30 daría 6000.599999999999.
    assert res.total_ingresos == Decimal("6000.60")
    assert res.total_gastos == Decimal("0.30")
    assert res.balance == Decimal("6000.30")
    # Representación consistente con dos decimales.
    assert str(res.total_ingresos) == "6000.60"
    assert str(res.balance) == "6000.30"


# =============================================================================
# CASOS SIN MOVIMIENTOS
# =============================================================================

def test_resumen_usuario_sin_movimientos(resumen_service: ResumenService):
    """6. Un usuario sin ningún movimiento devuelve ceros, no un error."""
    res = resumen_service.obtener_resumen_mensual(id_usuario=1, mes="2026-08")

    assert res.total_ingresos == Decimal("0.00")
    assert res.total_gastos == Decimal("0.00")
    assert res.balance == Decimal("0.00")


def test_resumen_mes_sin_movimientos(resumen_service: ResumenService, fake_movimiento_repo):
    """7. Un mes sin movimientos devuelve ceros aunque el usuario tenga historial."""
    _sembrar(fake_movimiento_repo, "ingreso", "3000000.00", date(2026, 7, 15))

    res = resumen_service.obtener_resumen_mensual(id_usuario=1, mes="2026-08")

    assert res.total_ingresos == Decimal("0.00")
    assert res.total_gastos == Decimal("0.00")
    assert res.balance == Decimal("0.00")


# =============================================================================
# AISLAMIENTO DEL PERIODO Y DEL USUARIO
# =============================================================================

def test_resumen_incluye_extremos_del_mes(resumen_service: ResumenService, fake_movimiento_repo):
    """El primer y el último día del mes entran en el cálculo."""
    _sembrar(fake_movimiento_repo, "ingreso", "100.00", date(2026, 8, 1))
    _sembrar(fake_movimiento_repo, "ingreso", "200.00", date(2026, 8, 31))

    res = resumen_service.obtener_resumen_mensual(id_usuario=1, mes="2026-08")

    assert res.total_ingresos == Decimal("300.00")


def test_resumen_excluye_meses_adyacentes(resumen_service: ResumenService, fake_movimiento_repo):
    """Los movimientos del mes anterior y del siguiente quedan fuera del periodo."""
    _sembrar(fake_movimiento_repo, "ingreso", "999.00", date(2026, 7, 31))
    _sembrar(fake_movimiento_repo, "ingreso", "888.00", date(2026, 9, 1))
    _sembrar(fake_movimiento_repo, "ingreso", "100.00", date(2026, 8, 15))

    res = resumen_service.obtener_resumen_mensual(id_usuario=1, mes="2026-08")

    assert res.total_ingresos == Decimal("100.00")


def test_resumen_aisla_movimientos_de_otro_usuario(
    resumen_service: ResumenService, fake_movimiento_repo, fake_usuario_repo
):
    """Los movimientos de otro usuario no contaminan el resumen."""
    fake_usuario_repo.create(nombre="Otro", correo="otro@example.com", contrasena_hash="hash")
    _sembrar(fake_movimiento_repo, "ingreso", "100.00", date(2026, 8, 10), id_usuario=1)
    _sembrar(fake_movimiento_repo, "ingreso", "5000.00", date(2026, 8, 10), id_usuario=2)

    res = resumen_service.obtener_resumen_mensual(id_usuario=1, mes="2026-08")

    assert res.total_ingresos == Decimal("100.00")


# =============================================================================
# VALIDACIONES
# =============================================================================

def test_resumen_usuario_inexistente(resumen_service: ResumenService):
    """3. Un usuario inexistente produce 404."""
    with pytest.raises(EntityNotFoundException) as exc:
        resumen_service.obtener_resumen_mensual(id_usuario=999, mes="2026-08")
    assert exc.value.status_code == 404
    assert "El usuario con ID 999 no existe" in exc.value.message


@pytest.mark.parametrize("mes_invalido", ["2026-8", "agosto", "2026/08", "", "2026"])
def test_resumen_mes_con_formato_invalido(resumen_service: ResumenService, mes_invalido):
    """4. Un mes con formato incorrecto produce 400."""
    with pytest.raises(ValidationException) as exc:
        resumen_service.obtener_resumen_mensual(id_usuario=1, mes=mes_invalido)
    assert exc.value.status_code == 400


@pytest.mark.parametrize("mes_inexistente", ["2026-13", "2026-00"])
def test_resumen_mes_inexistente(resumen_service: ResumenService, mes_inexistente):
    """5. Un número de mes fuera de 01-12 produce 400."""
    with pytest.raises(ValidationException) as exc:
        resumen_service.obtener_resumen_mensual(id_usuario=1, mes=mes_inexistente)
    assert exc.value.status_code == 400


def test_resumen_valida_mes_antes_de_consultar_usuario(resumen_service: ResumenService):
    """El periodo se valida antes de tocar la base de datos, incluso con usuario inexistente."""
    with pytest.raises(ValidationException):
        resumen_service.obtener_resumen_mensual(id_usuario=999, mes="2026-13")
