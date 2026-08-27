from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Path, Query, status

from app.core.dependencies import get_current_user, get_movimiento_service
from app.schemas.movimiento import (
    MensajeResponse,
    MovimientoCreate,
    MovimientoResponse,
    MovimientoUpdate,
)
from app.schemas.usuario import UsuarioResponse
from app.services.movimiento_service import MovimientoService

router = APIRouter(
    prefix="/api/movimientos",
    tags=["Movimientos"],
    responses={401: {"description": "Token ausente, inválido o expirado"}},
)


@router.post(
    "",
    response_model=MovimientoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo movimiento",
    description=(
        "Registra un ingreso o gasto en la cuenta del usuario autenticado tras "
        "validar la categoría, su pertenencia y la coherencia de tipo. El "
        "propietario procede del token, no del cuerpo de la petición."
    )
)
def registrar_movimiento(
    payload: MovimientoCreate,
    usuario: UsuarioResponse = Depends(get_current_user),
    service: MovimientoService = Depends(get_movimiento_service)
) -> MovimientoResponse:
    """
    Endpoint para el registro de movimientos financieros (RF03).
    """
    return service.crear_movimiento(payload, id_usuario=usuario.id_usuario)


@router.get(
    "",
    response_model=List[MovimientoResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar los movimientos propios con filtros opcionales",
    description=(
        "Consulta el historial de movimientos del usuario autenticado, "
        "ordenados por fecha DESC, con filtrado opcional por rango de fechas y "
        "categoría. Solo devuelve movimientos de la propia cuenta."
    )
)
def listar_movimientos(
    desde: Optional[date] = Query(None, description="Fecha inicial del filtro (YYYY-MM-DD)"),
    hasta: Optional[date] = Query(None, description="Fecha final del filtro (YYYY-MM-DD)"),
    categoria: Optional[int] = Query(None, gt=0, description="Filtrar por ID de categoría"),
    usuario: UsuarioResponse = Depends(get_current_user),
    service: MovimientoService = Depends(get_movimiento_service)
) -> List[MovimientoResponse]:
    """
    Endpoint para consultar movimientos con filtros (RF04).
    """
    return service.listar_movimientos(
        id_usuario=usuario.id_usuario,
        desde=desde,
        hasta=hasta,
        id_categoria=categoria
    )


@router.put(
    "/{id}",
    response_model=MovimientoResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un movimiento propio",
    description=(
        "Actualiza un movimiento tras comprobar que pertenece al usuario "
        "autenticado. Modificar el movimiento de otra cuenta devuelve 400."
    )
)
def actualizar_movimiento(
    id: int = Path(..., gt=0, description="Identificador del movimiento a actualizar"),
    payload: MovimientoUpdate = ...,
    usuario: UsuarioResponse = Depends(get_current_user),
    service: MovimientoService = Depends(get_movimiento_service)
) -> MovimientoResponse:
    """
    Endpoint para editar un movimiento existente del usuario autenticado.
    """
    return service.actualizar_movimiento(
        id_movimiento=id, data=payload, id_usuario=usuario.id_usuario
    )


@router.delete(
    "/{id}",
    response_model=MensajeResponse,
    status_code=status.HTTP_200_OK,
    summary="Eliminar un movimiento propio",
    description=(
        "Elimina de forma permanente un movimiento tras comprobar que pertenece "
        "al usuario autenticado. Eliminar el movimiento de otra cuenta devuelve 400."
    )
)
def eliminar_movimiento(
    id: int = Path(..., gt=0, description="Identificador del movimiento a eliminar"),
    usuario: UsuarioResponse = Depends(get_current_user),
    service: MovimientoService = Depends(get_movimiento_service)
) -> MensajeResponse:
    """
    Endpoint para eliminar un movimiento del usuario autenticado.
    """
    return service.eliminar_movimiento(id_movimiento=id, id_usuario=usuario.id_usuario)
