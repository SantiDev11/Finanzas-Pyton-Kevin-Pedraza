from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_auth_service, get_current_user
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.usuario import UsuarioResponse
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/api/auth",
    tags=["Autenticación"]
)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión y obtener un token de acceso",
    description=(
        "Verifica el correo y la contraseña contra el hash bcrypt almacenado. "
        "Si son correctos devuelve un JWT firmado con su tiempo de validez y "
        "los datos públicos del usuario. Unas credenciales incorrectas "
        "devuelven 401 con un mensaje genérico, idéntico tanto si el correo no "
        "existe como si la contraseña no coincide."
    ),
    responses={401: {"description": "Credenciales inválidas"}},
)
def iniciar_sesion(
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """
    Endpoint de inicio de sesión.
    """
    return service.autenticar(correo=payload.correo, contrasena=payload.contrasena)


@router.get(
    "/me",
    response_model=UsuarioResponse,
    status_code=status.HTTP_200_OK,
    summary="Datos del usuario autenticado",
    description=(
        "Devuelve el usuario correspondiente al token enviado. El frontend lo "
        "usa al abrir el panel para comprobar que la sesión sigue siendo "
        "válida antes de mostrar nada."
    ),
    responses={401: {"description": "Token ausente, inválido o expirado"}},
)
def usuario_actual(
    usuario: UsuarioResponse = Depends(get_current_user),
) -> UsuarioResponse:
    """
    Endpoint de verificación de sesión.
    """
    return usuario
