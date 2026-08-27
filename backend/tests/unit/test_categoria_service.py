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
