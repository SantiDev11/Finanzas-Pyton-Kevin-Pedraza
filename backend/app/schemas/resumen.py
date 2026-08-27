from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class ResumenFinancieroResponse(BaseModel):
    """
    Esquema de respuesta del resumen financiero mensual.

    Es un DTO de salida: no expone ninguna entidad de base de datos, solo los
    totales agregados y métricas que el cliente necesita. Los importes son Decimal,
    igual que en MovimientoResponse, para conservar la precisión monetaria.
    """
    id_usuario: int = Field(..., description="Identificador del usuario consultado")
    mes: str = Field(..., description="Periodo consultado, normalizado a YYYY-MM")
    total_ingresos: Decimal = Field(..., description="Suma de los movimientos de tipo 'ingreso' del periodo")
    total_gastos: Decimal = Field(..., description="Suma de los movimientos de tipo 'gasto' del periodo")
    balance: Decimal = Field(..., description="Ahorro del periodo: total_ingresos - total_gastos")
    porcentaje_ahorro: float = Field(default=0.0, description="Porcentaje de ahorro mensual: (ingresos - gastos) / ingresos * 100")
    categoria_mas_costosa_mes: Optional[str] = Field(default=None, description="Categoría con mayor gasto en el mes consultado")
    categoria_mas_costosa_historico: Optional[str] = Field(default=None, description="Categoría con mayor gasto acumulado en el histórico")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id_usuario": 1,
                "mes": "2026-08",
                "total_ingresos": "3500000.00",
                "total_gastos": "2100000.00",
                "balance": "1400000.00",
                "porcentaje_ahorro": 40.0,
                "categoria_mas_costosa_mes": "Vivienda",
                "categoria_mas_costosa_historico": "Alimentación"
            }
        }
    }

