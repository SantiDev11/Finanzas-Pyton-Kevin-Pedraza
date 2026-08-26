from datetime import date
from decimal import Decimal
import pytest

from app.core.exceptions import EntityNotFoundException, ValidationException
from app.schemas.movimiento import MovimientoCreate, MovimientoUpdate
from app.services.movimiento_service import MovimientoService


def test_service_crear_ingreso_valido(movimiento_service: MovimientoService):
    """1. Crear ingreso válido."""
    payload = MovimientoCreate(
        id_usuario=1,
        id_categoria=1,  # Categoría 'Salario' (ingreso)
        tipo="ingreso",
        monto=Decimal("2500000.00"),
        fecha=date(2026, 6, 1),
        descripcion="Pago mensual nómina",
    )
    res = movimiento_service.crear_movimiento(payload)
    assert res.id_movimiento > 0
    assert res.id_usuario == 1
    assert res.id_categoria == 1
    assert res.categoria == "Salario"
    assert res.tipo == "ingreso"
    assert res.monto == Decimal("2500000.00")
    assert res.fecha == date(2026, 6, 1)


def test_service_crear_gasto_valido(movimiento_service: MovimientoService):
    """2. Crear gasto válido."""
    payload = MovimientoCreate(
        id_usuario=1,
        id_categoria=2,  # Categoría 'Alimentación' (gasto)
        tipo="gasto",
        monto=Decimal("320000.00"),
        fecha=date(2026, 6, 5),
        descripcion="Mercado quincenal",
    )
    res = movimiento_service.crear_movimiento(payload)
    assert res.id_movimiento > 0
    assert res.categoria == "Alimentación"
    assert res.tipo == "gasto"
    assert res.monto == Decimal("320000.00")


def test_service_crear_movimiento_usuario_inexistente(movimiento_service: MovimientoService):
    """6. Rechazar usuario inexistente (404)."""
    payload = MovimientoCreate(
        id_usuario=999,
        id_categoria=1,
        tipo="ingreso",
        monto=Decimal("100000.00"),
        fecha=date(2026, 6, 1),
    )
    with pytest.raises(EntityNotFoundException) as exc:
        movimiento_service.crear_movimiento(payload)
    assert "El usuario con ID 999 no existe" in str(exc.value.message)


def test_service_crear_movimiento_categoria_inexistente(movimiento_service: MovimientoService):
    """7. Rechazar categoría inexistente (404)."""
    payload = MovimientoCreate(
        id_usuario=1,
        id_categoria=999,
        tipo="ingreso",
        monto=Decimal("100000.00"),
        fecha=date(2026, 6, 1),
    )
    with pytest.raises(EntityNotFoundException) as exc:
        movimiento_service.crear_movimiento(payload)
    assert "La categoría con ID 999 no existe" in str(exc.value.message)


def test_service_crear_movimiento_categoria_otro_usuario(
    movimiento_service: MovimientoService, fake_categoria_repo, fake_usuario_repo
):
    """8. Rechazar categoría perteneciente a otro usuario."""
    # Crear usuario 2 y su categoría
    fake_usuario_repo.create(nombre="User 2", correo="u2@example.com", contrasena_hash="hash")
    cat_u2 = fake_categoria_repo.create(nombre="Consultoría U2", tipo="ingreso", id_usuario=2)

    # Intentar que usuario 1 use la categoría de usuario 2
    payload = MovimientoCreate(
        id_usuario=1,
        id_categoria=cat_u2["id_categoria"],
        tipo="ingreso",
        monto=Decimal("50000.00"),
        fecha=date(2026, 6, 1),
    )
    with pytest.raises(ValidationException) as exc:
        movimiento_service.crear_movimiento(payload)
    assert "no pertenece al usuario" in str(exc.value.message)


def test_service_crear_movimiento_incoherencia_tipo_categoria(movimiento_service: MovimientoService):
    """9. Rechazar incoherencia entre tipo de movimiento y tipo de categoría."""
    # Categoría 2 es 'Alimentación' (gasto). Intentar registrarla como 'ingreso'
    payload = MovimientoCreate(
        id_usuario=1,
        id_categoria=2,
        tipo="ingreso",  # Mismatch con gasto
        monto=Decimal("50000.00"),
        fecha=date(2026, 6, 1),
    )
    with pytest.raises(ValidationException) as exc:
        movimiento_service.crear_movimiento(payload)
    assert "Incoherencia de tipo" in str(exc.value.message)


def test_service_listar_movimientos_y_filtros(movimiento_service: MovimientoService):
    """10-15. Listado y filtros de movimientos."""
    # Insertar 3 movimientos con fechas distintas
    movimiento_service.crear_movimiento(MovimientoCreate(
        id_usuario=1, id_categoria=1, tipo="ingreso", monto=Decimal("1000.00"), fecha=date(2026, 1, 10)
    ))
    movimiento_service.crear_movimiento(MovimientoCreate(
        id_usuario=1, id_categoria=2, tipo="gasto", monto=Decimal("200.00"), fecha=date(2026, 2, 15)
    ))
    movimiento_service.crear_movimiento(MovimientoCreate(
        id_usuario=1, id_categoria=2, tipo="gasto", monto=Decimal("300.00"), fecha=date(2026, 3, 20)
    ))

    # Listar todos
    todos = movimiento_service.listar_movimientos(1)
    assert len(todos) == 3

    # Filtrar por rango
    filtrados_rango = movimiento_service.listar_movimientos(
        id_usuario=1, desde=date(2026, 2, 1), hasta=date(2026, 2, 28)
    )
    assert len(filtrados_rango) == 1
    assert filtrados_rango[0].fecha == date(2026, 2, 15)

    # Filtrar por categoría
    filtrados_cat = movimiento_service.listar_movimientos(id_usuario=1, id_categoria=2)
    assert len(filtrados_cat) == 2


def test_service_listar_movimientos_rango_invalido(movimiento_service: MovimientoService):
    """16. Rechazar rango de fechas inválido (desde > hasta)."""
    with pytest.raises(ValidationException) as exc:
        movimiento_service.listar_movimientos(
            id_usuario=1,
            desde=date(2026, 5, 1),
            hasta=date(2026, 1, 1),
        )
    assert "rango de fechas es inválido" in str(exc.value.message)


def test_service_actualizar_movimiento(movimiento_service: MovimientoService):
    """17-20. Actualizar movimiento existente y rechazar ajenos o inexistentes."""
    creado = movimiento_service.crear_movimiento(MovimientoCreate(
        id_usuario=1, id_categoria=2, tipo="gasto", monto=Decimal("150.00"), fecha=date(2026, 6, 1)
    ))

    # Actualizar monto y fecha
    act = movimiento_service.actualizar_movimiento(
        id_movimiento=creado.id_movimiento,
        data=MovimientoUpdate(
            id_usuario=1,
            id_categoria=2,
            tipo="gasto",
            monto=Decimal("180.00"),
            fecha=date(2026, 6, 2),
            descripcion="Ajuste de compra",
        )
    )
    assert act.monto == Decimal("180.00")
    assert act.fecha == date(2026, 6, 2)
    assert act.descripcion == "Ajuste de compra"

    # Rechazar inexistente
    with pytest.raises(EntityNotFoundException):
        movimiento_service.actualizar_movimiento(
            id_movimiento=9999,
            data=MovimientoUpdate(id_usuario=1, id_categoria=2, tipo="gasto", monto=Decimal("100.00"), fecha=date(2026, 6, 1))
        )


def test_service_eliminar_movimiento(movimiento_service: MovimientoService):
    """21-22. Eliminar movimiento existente y rechazar inexistente."""
    creado = movimiento_service.crear_movimiento(MovimientoCreate(
        id_usuario=1, id_categoria=1, tipo="ingreso", monto=Decimal("500.00"), fecha=date(2026, 6, 1)
    ))

    res = movimiento_service.eliminar_movimiento(creado.id_movimiento)
    assert "eliminado con éxito" in res.mensaje

    # Verificar que ya no existe
    with pytest.raises(EntityNotFoundException):
        movimiento_service.eliminar_movimiento(creado.id_movimiento)
