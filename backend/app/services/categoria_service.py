from typing import Optional, List

from app.core.exceptions import EntityNotFoundException, DuplicateEntityException, ValidationException
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.categoria import CategoriaCreate, CategoriaResponse


class CategoriaService:
    """
    Servicio de dominio para la gestión y reglas de negocio de Categorías.
    """

    def __init__(
        self,
        categoria_repository: Optional[CategoriaRepository] = None,
        usuario_repository: Optional[UsuarioRepository] = None
    ):
        self._categoria_repo = categoria_repository or CategoriaRepository()
        self._usuario_repo = usuario_repository or UsuarioRepository()

    def crear_categoria(self, data: CategoriaCreate) -> CategoriaResponse:
        """
        Crea una categoría verificando la existencia previa del usuario y la no duplicidad.
        """
        # Validar que el usuario exista
        if not self._usuario_repo.exists_by_id(data.id_usuario):
            raise EntityNotFoundException(f"No se puede crear la categoría: El usuario con ID {data.id_usuario} no existe.")

        # Validar tipo válido
        if data.tipo not in ("ingreso", "gasto"):
            raise ValidationException("El tipo de categoría debe ser exclusivamente 'ingreso' o 'gasto'.")

        # Validar unicidad (id_usuario, tipo, nombre)
        if self._categoria_repo.exists_by_user_type_name(data.id_usuario, data.tipo, data.nombre):
            raise DuplicateEntityException(
                f"Ya existe una categoría '{data.nombre}' de tipo '{data.tipo}' para el usuario {data.id_usuario}."
            )

        # Persistir
        nueva = self._categoria_repo.create(
            nombre=data.nombre,
            tipo=data.tipo,
            id_usuario=data.id_usuario
        )

        return CategoriaResponse(
            id_categoria=nueva["id_categoria"],
            nombre=nueva["nombre"],
            tipo=nueva["tipo"],
            id_usuario=nueva["id_usuario"]
        )

    def listar_por_usuario(self, id_usuario: int) -> List[CategoriaResponse]:
        """
        Retorna la lista de categorías del usuario tras validar su existencia.
        """
        if id_usuario <= 0:
            raise ValidationException("El id_usuario debe ser un entero positivo mayor a 0.")

        if not self._usuario_repo.exists_by_id(id_usuario):
            raise EntityNotFoundException(f"El usuario con ID {id_usuario} no existe.")

        items = self._categoria_repo.list_by_user(id_usuario)
        return [
            CategoriaResponse(
                id_categoria=item["id_categoria"],
                nombre=item["nombre"],
                tipo=item["tipo"],
                id_usuario=item["id_usuario"]
            )
            for item in items
        ]
