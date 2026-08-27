import pytest
from app.core.exceptions import EntityNotFoundException, DuplicateEntityException
from app.schemas.categoria import CategoriaCreate
from app.services.categoria_service import CategoriaService


def test_service_crear_categoria_ingreso_y_gasto(categoria_service: CategoriaService):
    # Crear categoría ingreso
    cat_ingreso = categoria_service.crear_categoria(
        CategoriaCreate(nombre="Salario", tipo="ingreso"), id_usuario=1
    )
    assert cat_ingreso.id_categoria > 0
    assert cat_ingreso.nombre == "Salario"
    assert cat_ingreso.tipo == "ingreso"
    assert cat_ingreso.id_usuario == 1

    # Crear categoría gasto
    cat_gasto = categoria_service.crear_categoria(
        CategoriaCreate(nombre="Alimentación", tipo="gasto"), id_usuario=1
    )
    assert cat_gasto.id_categoria > 0
    assert cat_gasto.nombre == "Alimentación"
    assert cat_gasto.tipo == "gasto"
    assert cat_gasto.id_usuario == 1


def test_service_crear_categoria_usuario_inexistente(categoria_service: CategoriaService):
    with pytest.raises(EntityNotFoundException) as exc_info:
        categoria_service.crear_categoria(
            CategoriaCreate(nombre="Transporte", tipo="gasto"), id_usuario=999
        )
    assert "no existe" in str(exc_info.value.message)


def test_service_crear_categoria_duplicada_mismo_tipo(categoria_service: CategoriaService):
    categoria_service.crear_categoria(
        CategoriaCreate(nombre="Salud", tipo="gasto"), id_usuario=1
    )

    with pytest.raises(DuplicateEntityException) as exc_info:
        categoria_service.crear_categoria(
            CategoriaCreate(nombre="Salud", tipo="gasto"), id_usuario=1
        )
    assert "Ya existe una categoría" in str(exc_info.value.message)


def test_service_listar_categorias_usuario(categoria_service: CategoriaService):
    categoria_service.crear_categoria(CategoriaCreate(nombre="Alimentación", tipo="gasto"), id_usuario=1)
    categoria_service.crear_categoria(CategoriaCreate(nombre="Salario", tipo="ingreso"), id_usuario=1)

    categorias = categoria_service.listar_por_usuario(1)
    assert len(categorias) == 2
    nombres = [c.nombre for c in categorias]
    assert "Alimentación" in nombres
    assert "Salario" in nombres


def test_service_listar_categorias_usuario_inexistente(categoria_service: CategoriaService):
    with pytest.raises(EntityNotFoundException):
        categoria_service.listar_por_usuario(888)


def test_service_actualizar_categoria_exitoso(categoria_service: CategoriaService):
    from app.schemas.categoria import CategoriaUpdate
    cat = categoria_service.crear_categoria(
        CategoriaCreate(nombre="Comida", tipo="gasto"), id_usuario=1
    )
    actualizada = categoria_service.actualizar_categoria(
        cat.id_categoria,
        CategoriaUpdate(nombre="Supermercado", tipo="gasto"),
        id_usuario=1,
    )
    assert actualizada.id_categoria == cat.id_categoria
    assert actualizada.nombre == "Supermercado"
    assert actualizada.tipo == "gasto"


def test_service_actualizar_categoria_inexistente(categoria_service: CategoriaService):
    from app.schemas.categoria import CategoriaUpdate
    with pytest.raises(EntityNotFoundException):
        categoria_service.actualizar_categoria(
            999, CategoriaUpdate(nombre="Inexistente", tipo="gasto"), id_usuario=1
        )


def test_service_actualizar_categoria_otro_usuario(categoria_service: CategoriaService):
    from app.schemas.categoria import CategoriaUpdate
    from app.core.exceptions import ValidationException
    cat = categoria_service.crear_categoria(
        CategoriaCreate(nombre="Privada", tipo="gasto"), id_usuario=2
    )
    with pytest.raises(ValidationException):
        categoria_service.actualizar_categoria(
            cat.id_categoria, CategoriaUpdate(nombre="Hack", tipo="gasto"), id_usuario=1
        )


def test_service_actualizar_categoria_nombre_duplicado(categoria_service: CategoriaService):
    from app.schemas.categoria import CategoriaUpdate
    categoria_service.crear_categoria(
        CategoriaCreate(nombre="Vivienda", tipo="gasto"), id_usuario=1
    )
    cat2 = categoria_service.crear_categoria(
        CategoriaCreate(nombre="Educación", tipo="gasto"), id_usuario=1
    )
    with pytest.raises(DuplicateEntityException):
        categoria_service.actualizar_categoria(
            cat2.id_categoria, CategoriaUpdate(nombre="Vivienda", tipo="gasto"), id_usuario=1
        )


def test_service_eliminar_categoria_exitoso(categoria_service: CategoriaService):
    cat = categoria_service.crear_categoria(
        CategoriaCreate(nombre="Temporal", tipo="ingreso"), id_usuario=1
    )
    categoria_service.eliminar_categoria(cat.id_categoria, id_usuario=1)
    categorias = categoria_service.listar_por_usuario(1)
    assert not any(c.id_categoria == cat.id_categoria for c in categorias)


def test_service_eliminar_categoria_inexistente(categoria_service: CategoriaService):
    with pytest.raises(EntityNotFoundException):
        categoria_service.eliminar_categoria(999, id_usuario=1)


def test_service_eliminar_categoria_otro_usuario(categoria_service: CategoriaService):
    from app.core.exceptions import ValidationException
    cat = categoria_service.crear_categoria(
        CategoriaCreate(nombre="De Otro", tipo="gasto"), id_usuario=2
    )
    with pytest.raises(ValidationException):
        categoria_service.eliminar_categoria(cat.id_categoria, id_usuario=1)


def test_service_eliminar_categoria_con_movimientos_bloqueada(
    categoria_service: CategoriaService, fake_categoria_repo, fake_movimiento_repo
):
    from decimal import Decimal
    from datetime import date
    from app.core.exceptions import ValidationException

    cat = categoria_service.crear_categoria(
        CategoriaCreate(nombre="Con Movs", tipo="gasto"), id_usuario=1
    )
    fake_movimiento_repo.create(
        id_usuario=1,
        id_categoria=cat.id_categoria,
        tipo="gasto",
        monto=Decimal("50000.00"),
        fecha=date(2026, 8, 15),
        descripcion="Compra",
    )
    with pytest.raises(ValidationException) as exc_info:
        categoria_service.eliminar_categoria(cat.id_categoria, id_usuario=1)
    assert "movimientos" in str(exc_info.value.message)

