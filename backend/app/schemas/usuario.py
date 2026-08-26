from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class UsuarioCreate(BaseModel):
    """Esquema para la solicitud de creación de usuario."""
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre completo del usuario")
    correo: EmailStr = Field(..., description="Dirección de correo electrónico única")
    contrasena: str = Field(..., min_length=8, max_length=128, description="Contraseña en texto plano")

    @field_validator("nombre")
    @classmethod
    def validate_nombre_trim(cls, v: str) -> str:
        trimmed = v.strip()
        if len(trimmed) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres no vacíos.")
        return trimmed

    model_config = {
        "json_schema_extra": {
            "example": {
                "nombre": "Ana Torres",
                "correo": "ana@example.com",
                "contrasena": "Password123*"
            }
        }
    }


class UsuarioResponse(BaseModel):
    """Esquema de respuesta pública de usuario (excluye hashes y contraseñas)."""
    id_usuario: int
    nombre: str
    correo: str
    fecha_registro: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id_usuario": 1,
                "nombre": "Ana Torres",
                "correo": "ana@example.com",
                "fecha_registro": "2026-08-26T17:00:00"
            }
        }
    }
