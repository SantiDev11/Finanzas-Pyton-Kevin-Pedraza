from typing import List, Optional
from pydantic import BaseModel, Field


class PrediccionResponse(BaseModel):
    """
    Esquema de respuesta para la predicción de gastos del próximo mes.

    Los campos reflejan los resultados del modelo LinearRegression entrenado
    con la serie temporal mensual de gastos del usuario.
    """
    id_usuario: int = Field(..., description="Identificador del usuario consultado")
    mes_predicho: Optional[str] = Field(None, description="Periodo predicho en formato YYYY-MM")
    gasto_estimado: float = Field(..., description="Gasto estimado para el próximo mes")
    confianza: str = Field(..., description="Nivel de confianza: 'alta' (≥6 meses), 'media' (2-5 meses), 'baja' (<2 meses)")
    razon: str = Field(..., description="Explicación del método utilizado para la predicción")
    meses_procesados: int = Field(..., ge=0, description="Cantidad de meses históricos procesados")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id_usuario": 1,
                "mes_predicho": "2026-09",
                "gasto_estimado": 1580000.50,
                "confianza": "alta",
                "razon": "Calculado con Regresión Lineal (8 meses procesados).",
                "meses_procesados": 8
            }
        }
    }


class AnomaliaItem(BaseModel):
    """Esquema de un gasto individual detectado como anomalía."""
    id_movimiento: int = Field(..., description="Identificador del movimiento atípico")
    fecha: str = Field(..., description="Fecha del gasto (YYYY-MM-DD)")
    monto: float = Field(..., description="Monto del gasto atípico")
    id_categoria: int = Field(..., description="Categoría del gasto")
    promedio_categoria: float = Field(..., description="Promedio de gastos en esa categoría")
    z_score: float = Field(..., description="Valor Z-Score calculado")
    descripcion: Optional[str] = Field(None, description="Descripción del movimiento")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id_movimiento": 25,
                "fecha": "2026-08-15",
                "monto": 5000000.00,
                "id_categoria": 3,
                "promedio_categoria": 450000.00,
                "z_score": 3.42,
                "descripcion": "Compra extraordinaria"
            }
        }
    }


class AnomaliasResponse(BaseModel):
    """
    Esquema de respuesta para la detección de anomalías en gastos.

    Encapsula la lista de anomalías detectadas junto con metadatos del análisis.
    """
    id_usuario: int = Field(..., description="Identificador del usuario consultado")
    umbral_z_score: float = Field(..., description="Umbral |Z-Score| utilizado para la detección")
    total_gastos_analizados: int = Field(..., ge=0, description="Cantidad de gastos analizados")
    total_anomalias: int = Field(..., ge=0, description="Cantidad de anomalías detectadas")
    anomalias: List[AnomaliaItem] = Field(default_factory=list, description="Lista de gastos atípicos")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id_usuario": 1,
                "umbral_z_score": 1.5,
                "total_gastos_analizados": 45,
                "total_anomalias": 2,
                "anomalias": [
                    {
                        "id_movimiento": 25,
                        "fecha": "2026-08-15",
                        "monto": 5000000.00,
                        "id_categoria": 3,
                        "promedio_categoria": 450000.00,
                        "z_score": 3.42,
                        "descripcion": "Compra extraordinaria"
                    }
                ]
            }
        }
    }
