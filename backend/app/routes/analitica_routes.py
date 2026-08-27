from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_analitica_service, get_current_user
from app.schemas.analitica import AnomaliasResponse, PrediccionResponse
from app.schemas.usuario import UsuarioResponse
from app.services.analitica_service import AnaliticaService

router = APIRouter(
    prefix="/api/analitica",
    tags=["Analítica"],
    responses={401: {"description": "Token ausente, inválido o expirado"}},
)


@router.get(
    "/prediccion",
    response_model=PrediccionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predicción de gastos del próximo mes",
    description=(
        "Predice el gasto total del próximo mes utilizando Regresión Lineal "
        "(LinearRegression de scikit-learn) sobre la serie temporal mensual de "
        "gastos del usuario autenticado. Requiere al menos 2 meses de historial; "
        "con menos datos devuelve un promedio simple con confianza 'baja'."
    ),
)
def obtener_prediccion(
    usuario: UsuarioResponse = Depends(get_current_user),
    service: AnaliticaService = Depends(get_analitica_service),
) -> PrediccionResponse:
    """
    Endpoint de predicción de gastos (Módulo Analítico).
    """
    return service.obtener_prediccion(usuario.id_usuario)


@router.get(
    "/anomalias",
    response_model=AnomaliasResponse,
    status_code=status.HTTP_200_OK,
    summary="Detección de anomalías en gastos",
    description=(
        "Detecta gastos atípicos del usuario autenticado con Z-Score agrupado por "
        "categoría. El umbral por defecto es |Z| > 1.5 (definido por el ejercicio "
        "del instructor). Devuelve lista vacía si no existen anomalías."
    ),
)
def obtener_anomalias(
    usuario: UsuarioResponse = Depends(get_current_user),
    service: AnaliticaService = Depends(get_analitica_service),
) -> AnomaliasResponse:
    """
    Endpoint de detección de anomalías (Módulo Analítico).
    """
    return service.obtener_anomalias(usuario.id_usuario)
