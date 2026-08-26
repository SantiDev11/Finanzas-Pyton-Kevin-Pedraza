from decimal import Decimal
from pydantic import BaseModel, Field


class ResumenFinancieroResponse(BaseModel):
    """
    Esquema de respuesta del resumen financiero mensual.

    Es un DTO de salida: no expone ninguna entidad de base de datos, solo los
    totales agregados que el cliente necesita. Los importes son Decimal, igual
    que en MovimientoResponse, para conservar la precisión monetaria y una
    representación consistente en toda la API.
    """
    id_usuario: int = Field(..., description="Identificador del usuario consultado")
    mes: str = Field(..., description="Periodo consultado, normalizado a YYYY-MM")
    total_ingresos: Decimal = Field(..., description="Suma de los movimientos de tipo 'ingreso' del periodo")
    total_gastos: Decimal = Field(..., description="Suma de los movimientos de tipo 'gasto' del periodo")
    balance: Decimal = Field(..., description="Ahorro del periodo: total_ingresos - total_gastos")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id_usuario": 1,
                "mes": "2026-08",
                "total_ingresos": "3500000.00",
                "total_gastos": "2100000.00",
                "balance": "1400000.00"
            }
        }
    }
