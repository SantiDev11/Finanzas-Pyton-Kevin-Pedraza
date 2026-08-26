from typing import List
from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import get_categoria_service
from app.schemas.categoria import CategoriaCreate, CategoriaResponse
from app.services.categoria_service import CategoriaService

router = APIRouter(
    prefix="/api/categorias",
    tags=["Categorías"]
)


@router.post(
    "",
    response_model=CategoriaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva categoría",
    description="Registra una nueva categoría de tipo 'ingreso' o 'gasto' asociada a un usuario."
)
def crear_categoria(
    payload: CategoriaCreate,
    service: CategoriaService = Depends(get_categoria_service)
) -> CategoriaResponse:
    """
    Endpoint para la creación de categorías (RF02).
    """
    return service.crear_categoria(payload)


@router.get(
    "",
    response_model=List[CategoriaResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar categorías de un usuario",
    description="Obtiene todas las categorías asociadas al usuario especificado mediante el parámetro de consulta."
)
def listar_categorias(
    id_usuario: int = Query(..., gt=0, description="Identificador del usuario"),
    service: CategoriaService = Depends(get_categoria_service)
) -> List[CategoriaResponse]:
    """
    Endpoint para consultar las categorías pertenecientes a un usuario.
    """
    return service.listar_por_usuario(id_usuario)
