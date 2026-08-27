from pydantic import BaseModel, EmailStr, Field

from app.schemas.usuario import UsuarioResponse


class LoginRequest(BaseModel):
    """
    Credenciales enviadas al endpoint de inicio de sesión.

    La contraseña viaja en el cuerpo de la petición, nunca en la URL: un query
    string queda registrado en logs de servidor, historiales y proxies.
    """
    correo: EmailStr = Field(..., description="Correo electrónico registrado")
    contrasena: str = Field(..., min_length=1, max_length=128, description="Contraseña en texto plano")

    model_config = {
        "json_schema_extra": {
            "example": {
                "correo": "ana@example.com",
                "contrasena": "Password123*"
            }
        }
    }


class TokenResponse(BaseModel):
    """
    Respuesta del inicio de sesión: el token de acceso y el usuario autenticado.

    Se incluye el usuario para que el frontend no necesite una segunda petición
    solo para saber cómo se llama quien acaba de entrar. `UsuarioResponse` no
    expone el hash de la contraseña.
    """
    access_token: str = Field(..., description="JWT firmado que autentica las siguientes peticiones")
    token_type: str = Field(default="bearer", description="Esquema de autorización HTTP")
    expires_in: int = Field(..., description="Validez del token en segundos")
    usuario: UsuarioResponse = Field(..., description="Datos públicos del usuario autenticado")

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "usuario": {
                    "id_usuario": 1,
                    "nombre": "Ana Torres",
                    "correo": "ana@example.com",
                    "fecha_registro": "2026-08-26T17:00:00"
                }
            }
        }
    }
