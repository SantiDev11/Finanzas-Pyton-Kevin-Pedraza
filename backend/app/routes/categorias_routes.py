from typing import List, Dict
from fastapi import APIRouter, Depends, Path, status

from app.core.dependencies import get_categoria_service, get_current_user
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate, CategoriaResponse
from app.schemas.usuario import UsuarioResponse
from app.services.categoria_service import CategoriaService

router = APIRouter(
    prefix="/api/categorias",
    tags=["Categorías"],
    responses={401: {"description": "Token ausente, inválido o expirado"}},
)


@router.post(
    "",
    response_model=CategoriaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva categoría",
    description=(
        "Registra una nueva categoría de tipo 'ingreso' o 'gasto' en la cuenta "
        "del usuario autenticado. El propietario se toma del token: el cuerpo "
        "de la petición no admite `id_usuario`."
    )
)
def crear_categoria(
    payload: CategoriaCreate,
    usuario: UsuarioResponse = Depends(get_current_user),
    service: CategoriaService = Depends(get_categoria_service)
) -> CategoriaResponse:
    """
    Endpoint para la creación de categorías (RF02), restringido al usuario autenticado.
    """
    return service.crear_categoria(payload, id_usuario=usuario.id_usuario)


@router.get(
    "",
    response_model=List[CategoriaResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar las categorías propias",
    description=(
        "Obtiene las categorías del usuario autenticado. No existe forma de "
        "consultar las categorías de otra cuenta."
    )
)
def listar_categorias(
    usuario: UsuarioResponse = Depends(get_current_user),
    service: CategoriaService = Depends(get_categoria_service)
) -> List[CategoriaResponse]:
    """
    Endpoint para consultar las categorías del usuario autenticado.
    """
    return service.listar_por_usuario(usuario.id_usuario)


@router.put(
    "/{id_categoria}",
    response_model=CategoriaResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar una categoría propia",
    description=(
        "Modifica el nombre o tipo de una categoría existente del usuario autenticado. "
        "Rechaza modificaciones sobre categorías ajenas o nombres duplicados."
    )
)
def actualizar_categoria(
    id_categoria: int = Path(..., description="ID de la categoría a actualizar", ge=1),
    payload: CategoriaUpdate = ...,
    usuario: UsuarioResponse = Depends(get_current_user),
    service: CategoriaService = Depends(get_categoria_service)
) -> CategoriaResponse:
    """
    Endpoint para editar una categoría existente.
    """
    return service.actualizar_categoria(
        id_categoria=id_categoria,
        data=payload,
        id_usuario=usuario.id_usuario
    )


@router.delete(
    "/{id_categoria}",
    response_model=Dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Eliminar una categoría propia",
    description=(
        "Elimina una categoría del usuario autenticado si no tiene movimientos "
        "asociados (integridad referencial)."
    )
)
def eliminar_categoria(
    id_categoria: int = Path(..., description="ID de la categoría a eliminar", ge=1),
    usuario: UsuarioResponse = Depends(get_current_user),
    service: CategoriaService = Depends(get_categoria_service)
) -> Dict[str, str]:
    """
    Endpoint para eliminar una categoría propia.
    """
    service.eliminar_categoria(id_categoria=id_categoria, id_usuario=usuario.id_usuario)
    return {"mensaje": f"Categoría con ID {id_categoria} eliminada exitosamente."}

