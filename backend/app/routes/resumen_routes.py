from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import get_current_user, get_resumen_service
from app.core.periodo import FORMATO_MES
from app.schemas.resumen import ResumenFinancieroResponse
from app.schemas.usuario import UsuarioResponse
from app.services.resumen_service import ResumenService

router = APIRouter(
    prefix="/api/resumen",
    tags=["Resumen Financiero"],
    responses={401: {"description": "Token ausente, inválido o expirado"}},
)


@router.get(
    "",
    response_model=ResumenFinancieroResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener el resumen financiero de un mes",
    description=(
        "Calcula el total de ingresos, el total de gastos y el balance (ahorro) "
        "del usuario autenticado para un periodo mensual. Un periodo sin "
        "movimientos devuelve 200 con los tres importes en 0.00."
    )
)
def obtener_resumen_financiero(
    mes: str = Query(
        ...,
        description=f"Periodo mensual en formato {FORMATO_MES}, por ejemplo '2026-08'",
        examples=["2026-08"],
    ),
    usuario: UsuarioResponse = Depends(get_current_user),
    service: ResumenService = Depends(get_resumen_service)
) -> ResumenFinancieroResponse:
    """
    Endpoint de resumen financiero mensual (RF05).

    `mes` se recibe como cadena sin patrón declarado en Query de forma deliberada:
    la validación del periodo pertenece al servicio, que responde 400 Bad Request
    mediante ValidationException. Si el patrón se declarase aquí, FastAPI
    rechazaría el valor antes de llegar al servicio y devolvería 422.
    """
    return service.obtener_resumen_mensual(id_usuario=usuario.id_usuario, mes=mes)
