from typing import Literal
from pydantic import BaseModel, Field, field_validator


class CategoriaCreate(BaseModel):
    """Esquema para la creación de una nueva categoría."""
    nombre: str = Field(..., min_length=2, max_length=60, description="Nombre de la categoría")
    tipo: Literal["ingreso", "gasto"] = Field(..., description="Tipo de categoría (ingreso o gasto)")
    id_usuario: int = Field(..., gt=0, description="Identificador del usuario propietario")

    @field_validator("nombre")
    @classmethod
    def validate_nombre_trim(cls, v: str) -> str:
        trimmed = v.strip()
        if len(trimmed) < 2:
            raise ValueError("El nombre de la categoría debe tener al menos 2 caracteres no vacíos.")
        return trimmed

    model_config = {
        "json_schema_extra": {
            "example": {
                "nombre": "Alimentación",
                "tipo": "gasto",
                "id_usuario": 1
            }
        }
    }


class CategoriaResponse(BaseModel):
    """Esquema de respuesta de una categoría."""
    id_categoria: int
    nombre: str
    tipo: str
    id_usuario: int

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id_categoria": 1,
                "nombre": "Alimentación",
                "tipo": "gasto",
                "id_usuario": 1
            }
        }
    }
