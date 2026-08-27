from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Path, Query, status

from app.core.dependencies import get_movimiento_service
from app.schemas.movimiento import (
    MensajeResponse,
    MovimientoCreate,
    MovimientoResponse,
    MovimientoUpdate,
)
from app.services.movimiento_service import MovimientoService

router = APIRouter(
    prefix="/api/movimientos",
    tags=["Movimientos"]
)


@router.post(
    "",
    response_model=MovimientoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo movimiento",
    description="Registra un nuevo ingreso o gasto tras validar usuario, categoría, pertenencia y coherencia de tipo."
)
def registrar_movimiento(
    payload: MovimientoCreate,
    service: MovimientoService = Depends(get_movimiento_service)
) -> MovimientoResponse:
    """
    Endpoint para el registro de movimientos financieros (RF03).
    """
    return service.crear_movimiento(payload)


@router.get(
    "",
    response_model=List[MovimientoResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar movimientos con filtros opcionales",
    description="Consulta el historial de movimientos de un usuario ordenados por fecha DESC, con soporte de filtrado por rango de fechas y categoría."
)
def listar_movimientos(
    id_usuario: int = Query(..., gt=0, description="Identificador del usuario"),
    desde: Optional[date] = Query(None, description="Fecha inicial del filtro (YYYY-MM-DD)"),
    hasta: Optional[date] = Query(None, description="Fecha final del filtro (YYYY-MM-DD)"),
    categoria: Optional[int] = Query(None, gt=0, description="Filtrar por ID de categoría"),
    service: MovimientoService = Depends(get_movimiento_service)
) -> List[MovimientoResponse]:
    """
    Endpoint para consultar movimientos con filtros (RF04).
    """
    return service.listar_movimientos(
        id_usuario=id_usuario,
        desde=desde,
        hasta=hasta,
        id_categoria=categoria
    )


@router.put(
    "/{id}",
    response_model=MovimientoResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un movimiento existente",
    description="Actualiza los datos de un movimiento tras validar existencia y pertenencia."
)
def actualizar_movimiento(
    id: int = Path(..., gt=0, description="Identificador del movimiento a actualizar"),
    payload: MovimientoUpdate = ...,
    service: MovimientoService = Depends(get_movimiento_service)
) -> MovimientoResponse:
    """
    Endpoint para editar un movimiento existente.
    """
    return service.actualizar_movimiento(id_movimiento=id, data=payload)


@router.delete(
    "/{id}",
    response_model=MensajeResponse,
    status_code=status.HTTP_200_OK,
    summary="Eliminar un movimiento por ID",
    description=(
        "Elimina de forma permanente un movimiento tras validar su existencia. "
        "Si se indica `id_usuario`, se comprueba además que el movimiento le "
        "pertenezca y se rechaza el borrado en caso contrario."
    )
)
def eliminar_movimiento(
    id: int = Path(..., gt=0, description="Identificador del movimiento a eliminar"),
    id_usuario: Optional[int] = Query(
        None, gt=0, description="Identificador del usuario propietario; valida la pertenencia"
    ),
    service: MovimientoService = Depends(get_movimiento_service)
) -> MensajeResponse:
    """
    Endpoint para eliminar un movimiento por ID.
    """
    return service.eliminar_movimiento(id_movimiento=id, id_usuario=id_usuario)
