from typing import Optional

from app.core.exceptions import DuplicateEntityException
from app.core.security import hash_password
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario import UsuarioCreate, UsuarioResponse


class UsuarioService:
    """
    Servicio de dominio para la gestión y reglas de negocio de Usuarios.
    """

    def __init__(self, usuario_repository: Optional[UsuarioRepository] = None):
        self._repository = usuario_repository or UsuarioRepository()

    def registrar_usuario(self, data: UsuarioCreate) -> UsuarioResponse:
        """
        Aplica validaciones de negocio y registra un nuevo usuario con contraseña hasheada.
        """
        # Validación de unicidad de correo
        if self._repository.exists_by_email(data.correo):
            raise DuplicateEntityException(f"El correo '{data.correo}' ya se encuentra registrado.")

        # Hashing seguro con bcrypt
        contrasena_hash = hash_password(data.contrasena)

        # Persistencia
        nuevo_usuario = self._repository.create(
            nombre=data.nombre,
            correo=data.correo,
            contrasena_hash=contrasena_hash
        )

        return UsuarioResponse(
            id_usuario=nuevo_usuario["id_usuario"],
            nombre=nuevo_usuario["nombre"],
            correo=nuevo_usuario["correo"],
            fecha_registro=nuevo_usuario.get("fecha_registro")
        )

    def obtener_por_id(self, id_usuario: int) -> Optional[UsuarioResponse]:
        """
        Consulta un usuario por ID sin exponer credenciales.
        """
        usuario = self._repository.get_by_id(id_usuario)
        if not usuario:
            return None
        return UsuarioResponse(
            id_usuario=usuario["id_usuario"],
            nombre=usuario["nombre"],
            correo=usuario["correo"],
            fecha_registro=usuario.get("fecha_registro")
        )
