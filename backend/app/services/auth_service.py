"""
Servicio de autenticación.

Responsabilidades:
  - verificar credenciales contra el hash bcrypt almacenado;
  - emitir el token de acceso;
  - resolver el usuario que hay detrás de un token ya validado.

No conoce HTTP: las rutas traducen sus excepciones a respuestas.
"""

from typing import Any, Dict, Optional

from app.core.exceptions import AuthenticationException, TokenInvalidoException
from app.core.security import crear_token_acceso, verify_password
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.auth import TokenResponse
from app.schemas.usuario import UsuarioResponse

# Hash de descarte con el formato de bcrypt. Se usa para gastar el mismo tiempo
# de cómputo cuando el correo no existe que cuando sí existe: sin esto, una
# respuesta notablemente más rápida delataría qué correos están registrados.
_HASH_SENUELO = "$2b$12$" + "." * 53


class AuthService:
    """Servicio de dominio para el inicio de sesión y la identidad del usuario."""

    def __init__(self, usuario_repository: Optional[UsuarioRepository] = None):
        self._repository = usuario_repository or UsuarioRepository()

    def autenticar(self, correo: str, contrasena: str) -> TokenResponse:
        """
        Valida las credenciales y devuelve un token de acceso.

        Lanza AuthenticationException (401) tanto si el correo no existe como
        si la contraseña no coincide, y con el mismo mensaje en ambos casos:
        cualquier diferencia permitiría enumerar las cuentas registradas.
        """
        usuario = self._repository.get_by_email(correo)

        # Se verifica siempre, incluso sin usuario, para no filtrar por tiempo.
        hash_almacenado = usuario["contrasena_hash"] if usuario else _HASH_SENUELO
        contrasena_valida = verify_password(contrasena, hash_almacenado)

        if not usuario or not contrasena_valida:
            raise AuthenticationException("Correo electrónico o contraseña incorrectos.")

        token, expira_en = crear_token_acceso(
            id_usuario=usuario["id_usuario"],
            correo=usuario["correo"],
        )

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=expira_en,
            usuario=_a_usuario_response(usuario),
        )

    def obtener_usuario_autenticado(self, id_usuario: int) -> UsuarioResponse:
        """
        Resuelve el usuario de un token ya validado criptográficamente.

        Un token con firma correcta puede seguir apuntando a un usuario que ya
        no existe (cuenta eliminada). Ese caso se trata como token inválido,
        no como 404: para el cliente la sesión simplemente ya no sirve.
        """
        usuario = self._repository.get_by_id(id_usuario)
        if not usuario:
            raise TokenInvalidoException("La sesión ya no es válida.")
        return _a_usuario_response(usuario)


def _a_usuario_response(usuario: Dict[str, Any]) -> UsuarioResponse:
    """Proyecta la fila de usuario al DTO público, sin el hash de contraseña."""
    return UsuarioResponse(
        id_usuario=usuario["id_usuario"],
        nombre=usuario["nombre"],
        correo=usuario["correo"],
        fecha_registro=usuario.get("fecha_registro"),
    )
