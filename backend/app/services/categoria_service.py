from typing import Optional, List

from app.core.exceptions import EntityNotFoundException, DuplicateEntityException, ValidationException
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate, CategoriaResponse


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

    def crear_categoria(self, data: CategoriaCreate, id_usuario: int) -> CategoriaResponse:
        """
        Crea una categoría para el usuario autenticado, comprobando la no duplicidad.

        `id_usuario` procede siempre del token de acceso, no del cuerpo de la
        petición: es la única forma de garantizar que nadie crea categorías en
        la cuenta de otra persona.
        """
        # Validar que el usuario exista
        if not self._usuario_repo.exists_by_id(id_usuario):
            raise EntityNotFoundException(f"No se puede crear la categoría: El usuario con ID {id_usuario} no existe.")

        # Validar tipo válido
        if data.tipo not in ("ingreso", "gasto"):
            raise ValidationException("El tipo de categoría debe ser exclusivamente 'ingreso' o 'gasto'.")

        # Validar unicidad (id_usuario, tipo, nombre)
        if self._categoria_repo.exists_by_user_type_name(id_usuario, data.tipo, data.nombre):
            raise DuplicateEntityException(
                f"Ya existe una categoría '{data.nombre}' de tipo '{data.tipo}' en tu cuenta."
            )

        # Persistir
        nueva = self._categoria_repo.create(
            nombre=data.nombre,
            tipo=data.tipo,
            id_usuario=id_usuario
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

    def actualizar_categoria(
        self, id_categoria: int, data: CategoriaUpdate, id_usuario: int
    ) -> CategoriaResponse:
        """
        Actualiza una categoría del usuario autenticado.
        Comprueba existencia, pertenencia del recurso y no duplicidad.
        """
        # 1. Validar existencia de la categoría
        categoria_actual = self._categoria_repo.get_by_id(id_categoria)
        if not categoria_actual:
            raise EntityNotFoundException(f"La categoría con ID {id_categoria} no existe.")

        # 2. Validar pertenencia de la categoría al usuario autenticado
        if categoria_actual["id_usuario"] != id_usuario:
            raise ValidationException("No tiene permisos para modificar una categoría que pertenece a otro usuario.")

        # 3. Validar tipo válido
        if data.tipo not in ("ingreso", "gasto"):
            raise ValidationException("El tipo de categoría debe ser exclusivamente 'ingreso' o 'gasto'.")

        # 4. Validar unicidad de nombre excluyendo la misma categoría
        if self._categoria_repo.exists_by_user_type_name_excluding_id(
            id_usuario=id_usuario,
            tipo=data.tipo,
            nombre=data.nombre,
            exclude_id=id_categoria
        ):
            raise DuplicateEntityException(
                f"Ya existe una categoría '{data.nombre}' de tipo '{data.tipo}' en tu cuenta."
            )

        # 5. Persistir cambios
        actualizada = self._categoria_repo.update(
            id_categoria=id_categoria,
            nombre=data.nombre,
            tipo=data.tipo
        )

        return CategoriaResponse(
            id_categoria=actualizada["id_categoria"],
            nombre=actualizada["nombre"],
            tipo=actualizada["tipo"],
            id_usuario=actualizada["id_usuario"]
        )

    def eliminar_categoria(self, id_categoria: int, id_usuario: int) -> None:
        """
        Elimina una categoría del usuario autenticado, previa validación de integridad referencial.
        """
        # 1. Validar existencia de la categoría
        categoria_actual = self._categoria_repo.get_by_id(id_categoria)
        if not categoria_actual:
            raise EntityNotFoundException(f"La categoría con ID {id_categoria} no existe.")

        # 2. Validar pertenencia de la categoría al usuario autenticado
        if categoria_actual["id_usuario"] != id_usuario:
            raise ValidationException("No tiene permisos para eliminar una categoría que pertenece a otro usuario.")

        # 3. Validar integridad referencial (no tener movimientos asociados)
        if self._categoria_repo.has_movimientos(id_categoria):
            raise ValidationException(
                "No se puede eliminar la categoría porque tiene movimientos financieros asociados. "
                "Elimine o reclasifique primero sus movimientos."
            )

        # 4. Eliminar
        self._categoria_repo.delete(id_categoria)

