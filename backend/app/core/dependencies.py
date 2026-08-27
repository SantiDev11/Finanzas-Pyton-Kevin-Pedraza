from typing import Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import TokenInvalidoException
from app.core.security import decodificar_token_acceso
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.movimiento_repository import MovimientoRepository
from app.schemas.usuario import UsuarioResponse
from app.services.auth_service import AuthService
from app.services.usuario_service import UsuarioService
from app.services.categoria_service import CategoriaService
from app.services.movimiento_service import MovimientoService
from app.services.resumen_service import ResumenService
from app.services.analitica_service import AnaliticaService

# auto_error=False para poder responder con el formato de error propio de la
# aplicación cuando falta la cabecera, en lugar del 403 que devolvería
# HTTPBearer por defecto ante un Authorization ausente.
_esquema_bearer = HTTPBearer(auto_error=False, scheme_name="Bearer")


def get_auth_service() -> AuthService:
    """Inyector del servicio de autenticación."""
    return AuthService(usuario_repository=UsuarioRepository())


def get_current_user(
    credenciales: Optional[HTTPAuthorizationCredentials] = Depends(_esquema_bearer),
    auth_service: AuthService = Depends(get_auth_service),
) -> UsuarioResponse:
    """
    Dependencia de autenticación: resuelve el usuario dueño de la petición.

    Pasos:
      1. Lee la cabecera `Authorization: Bearer <token>`.
      2. Valida la firma del JWT y su expiración.
      3. Traduce el `sub` del token al usuario correspondiente.
      4. Rechaza con 401 cualquier token ausente, inválido o caducado.

    El identificador que devuelve es la ÚNICA fuente de verdad sobre la
    identidad: ninguna ruta debe aceptar un id_usuario enviado por el cliente.
    """
    if credenciales is None or not credenciales.credentials:
        raise TokenInvalidoException("Se requiere autenticación para acceder a este recurso.")

    id_usuario = decodificar_token_acceso(credenciales.credentials)
    return auth_service.obtener_usuario_autenticado(id_usuario)


def get_usuario_service() -> UsuarioService:
    """Inyector del servicio de usuarios."""
    repo = UsuarioRepository()
    return UsuarioService(usuario_repository=repo)


def get_categoria_service() -> CategoriaService:
    """Inyector del servicio de categorías."""
    cat_repo = CategoriaRepository()
    usr_repo = UsuarioRepository()
    return CategoriaService(categoria_repository=cat_repo, usuario_repository=usr_repo)


def get_movimiento_service() -> MovimientoService:
    """Inyector del servicio de movimientos financieros."""
    mov_repo = MovimientoRepository()
    usr_repo = UsuarioRepository()
    cat_repo = CategoriaRepository()
    return MovimientoService(
        movimiento_repository=mov_repo,
        usuario_repository=usr_repo,
        categoria_repository=cat_repo
    )


def get_resumen_service() -> ResumenService:
    """Inyector del servicio de resumen financiero."""
    mov_repo = MovimientoRepository()
    usr_repo = UsuarioRepository()
    return ResumenService(
        movimiento_repository=mov_repo,
        usuario_repository=usr_repo
    )


def get_analitica_service() -> AnaliticaService:
    """Inyector del servicio de analítica financiera."""
    mov_repo = MovimientoRepository()
    usr_repo = UsuarioRepository()
    return AnaliticaService(
        movimiento_repository=mov_repo,
        usuario_repository=usr_repo
    )

