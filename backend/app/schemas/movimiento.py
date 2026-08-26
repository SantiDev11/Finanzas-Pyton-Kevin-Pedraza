from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator


class MovimientoCreate(BaseModel):
    """Esquema para la creación de un nuevo movimiento financiero."""
    id_usuario: int = Field(..., gt=0, description="Identificador del usuario")
    id_categoria: int = Field(..., gt=0, description="Identificador de la categoría")
    tipo: Literal["ingreso", "gasto"] = Field(..., description="Tipo de movimiento ('ingreso' o 'gasto')")
    monto: Decimal = Field(..., gt=Decimal("0.00"), decimal_places=2, max_digits=12, description="Monto del movimiento (positivo)")
    fecha: date = Field(..., description="Fecha contable del movimiento (YYYY-MM-DD)")
    descripcion: Optional[str] = Field(None, max_length=255, description="Descripción opcional")

    @field_validator("descripcion")
    @classmethod
    def trim_descripcion(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            trimmed = v.strip()
            return trimmed if trimmed else None
        return None

    model_config = {
        "json_schema_extra": {
            "example": {
                "id_usuario": 1,
                "id_categoria": 3,
                "tipo": "gasto",
                "monto": "85000.00",
                "fecha": "2026-08-20",
                "descripcion": "Mercado quincenal"
            }
        }
    }


class MovimientoUpdate(BaseModel):
    """Esquema para la actualización completa de un movimiento existente."""
    id_usuario: int = Field(..., gt=0, description="Identificador del usuario propietario")
    id_categoria: int = Field(..., gt=0, description="Identificador de la categoría")
    tipo: Literal["ingreso", "gasto"] = Field(..., description="Tipo de movimiento ('ingreso' o 'gasto')")
    monto: Decimal = Field(..., gt=Decimal("0.00"), decimal_places=2, max_digits=12, description="Monto del movimiento")
    fecha: date = Field(..., description="Fecha contable del movimiento (YYYY-MM-DD)")
    descripcion: Optional[str] = Field(None, max_length=255, description="Descripción opcional")

    @field_validator("descripcion")
    @classmethod
    def trim_descripcion(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            trimmed = v.strip()
            return trimmed if trimmed else None
        return None

    model_config = {
        "json_schema_extra": {
            "example": {
                "id_usuario": 1,
                "id_categoria": 3,
                "tipo": "gasto",
                "monto": "95000.00",
                "fecha": "2026-08-21",
                "descripcion": "Mercado quincenal ajustado"
            }
        }
    }


class MovimientoResponse(BaseModel):
    """Esquema de respuesta de un movimiento financiero."""
    id_movimiento: int
    id_usuario: int
    id_categoria: int
    categoria: str
    tipo: str
    monto: Decimal
    fecha: date
    descripcion: Optional[str] = None
    fecha_creacion: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id_movimiento": 1,
                "id_usuario": 1,
                "id_categoria": 3,
                "categoria": "Alimentación",
                "tipo": "gasto",
                "monto": "85000.00",
                "fecha": "2026-08-20",
                "descripcion": "Mercado quincenal",
                "fecha_creacion": "2026-08-20T14:30:00"
            }
        }
    }


class MensajeResponse(BaseModel):
    """Esquema genérico para confirmaciones de acción (p. ej. eliminación)."""
    mensaje: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "mensaje": "Movimiento eliminado con éxito"
            }
        }
    }
