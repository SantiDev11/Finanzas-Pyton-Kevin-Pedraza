from datetime import date
from typing import List, Optional

from app.core.exceptions import EntityNotFoundException, ValidationException
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.movimiento_repository import MovimientoRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.movimiento import (
    MensajeResponse,
    MovimientoCreate,
    MovimientoResponse,
    MovimientoUpdate,
)


class MovimientoService:
    """
    Servicio de dominio para la gestión y validación de reglas de negocio de Movimientos Financieros.
    """

    def __init__(
        self,
        movimiento_repository: Optional[MovimientoRepository] = None,
        usuario_repository: Optional[UsuarioRepository] = None,
        categoria_repository: Optional[CategoriaRepository] = None,
    ):
        self._movimiento_repo = movimiento_repository or MovimientoRepository()
        self._usuario_repo = usuario_repository or UsuarioRepository()
        self._categoria_repo = categoria_repository or CategoriaRepository()

    def crear_movimiento(self, data: MovimientoCreate) -> MovimientoResponse:
        """
        Crea un nuevo movimiento tras validar usuario, categoría, pertenencia y coherencia de tipo.
        """
        # 1. Validar que el usuario exista
        if not self._usuario_repo.exists_by_id(data.id_usuario):
            raise EntityNotFoundException(f"El usuario con ID {data.id_usuario} no existe.")

        # 2. Validar que la categoría exista
        categoria = self._categoria_repo.get_by_id(data.id_categoria)
        if not categoria:
            raise EntityNotFoundException(f"La categoría con ID {data.id_categoria} no existe.")

        # 3. Validar pertenencia de la categoría al usuario
        if categoria["id_usuario"] != data.id_usuario:
            raise ValidationException("La categoría especificada no pertenece al usuario.")

        # 4. Validar coherencia entre tipo de movimiento y tipo de categoría
        if categoria["tipo"] != data.tipo:
            raise ValidationException(
                f"Incoherencia de tipo: La categoría '{categoria['nombre']}' es de tipo '{categoria['tipo']}', "
                f"pero el movimiento fue enviado como '{data.tipo}'."
            )

        # 5. Persistir movimiento
        nuevo = self._movimiento_repo.create(
            id_usuario=data.id_usuario,
            id_categoria=data.id_categoria,
            tipo=data.tipo,
            monto=data.monto,
            fecha=data.fecha,
            descripcion=data.descripcion,
        )

        return MovimientoResponse(
            id_movimiento=nuevo["id_movimiento"],
            id_usuario=nuevo["id_usuario"],
            id_categoria=nuevo["id_categoria"],
            categoria=nuevo["categoria"],
            tipo=nuevo["tipo"],
            monto=nuevo["monto"],
            fecha=nuevo["fecha"],
            descripcion=nuevo.get("descripcion"),
            fecha_creacion=nuevo.get("fecha_creacion"),
        )

    def listar_movimientos(
        self,
        id_usuario: int,
        desde: Optional[date] = None,
        hasta: Optional[date] = None,
        id_categoria: Optional[int] = None,
    ) -> List[MovimientoResponse]:
        """
        Lista los movimientos pertenecientes a un usuario con soporte para filtros de fecha y categoría.
        """
        # 1. Validar existencia del usuario
        if not self._usuario_repo.exists_by_id(id_usuario):
            raise EntityNotFoundException(f"El usuario con ID {id_usuario} no existe.")

        # 2. Validar rango de fechas si ambas están presentes
        if desde is not None and hasta is not None:
            if desde > hasta:
                raise ValidationException("El rango de fechas es inválido: 'desde' no puede ser posterior a 'hasta'.")

        # 3. Validar categoría de filtro si está presente
        if id_categoria is not None:
            categoria = self._categoria_repo.get_by_id(id_categoria)
            if not categoria:
                raise EntityNotFoundException(f"La categoría con ID {id_categoria} no existe.")
            if categoria["id_usuario"] != id_usuario:
                raise ValidationException("La categoría de filtro no pertenece al usuario solicitado.")

        # 4. Consultar repositorio
        registros = self._movimiento_repo.list_by_filters(
            id_usuario=id_usuario,
            desde=desde,
            hasta=hasta,
            id_categoria=id_categoria,
        )

        return [
            MovimientoResponse(
                id_movimiento=r["id_movimiento"],
                id_usuario=r["id_usuario"],
                id_categoria=r["id_categoria"],
                categoria=r["categoria"],
                tipo=r["tipo"],
                monto=r["monto"],
                fecha=r["fecha"],
                descripcion=r.get("descripcion"),
                fecha_creacion=r.get("fecha_creacion"),
            )
            for r in registros
        ]

    def actualizar_movimiento(
        self, id_movimiento: int, data: MovimientoUpdate
    ) -> MovimientoResponse:
        """
        Actualiza un movimiento existente verificando pertenencia del movimiento, usuario y categoría.
        """
        # 1. Validar existencia del movimiento a modificar
        movimiento_actual = self._movimiento_repo.get_by_id(id_movimiento)
        if not movimiento_actual:
            raise EntityNotFoundException(f"El movimiento con ID {id_movimiento} no existe.")

        # 2. Validar pertenencia del movimiento al usuario
        if movimiento_actual["id_usuario"] != data.id_usuario:
            raise ValidationException("No tiene permisos para modificar un movimiento que pertenece a otro usuario.")

        # 3. Validar existencia del usuario
        if not self._usuario_repo.exists_by_id(data.id_usuario):
            raise EntityNotFoundException(f"El usuario con ID {data.id_usuario} no existe.")

        # 4. Validar existencia de la categoría
        categoria = self._categoria_repo.get_by_id(data.id_categoria)
        if not categoria:
            raise EntityNotFoundException(f"La categoría con ID {data.id_categoria} no existe.")

        # 5. Validar pertenencia de la categoría al usuario
        if categoria["id_usuario"] != data.id_usuario:
            raise ValidationException("La categoría especificada no pertenece al usuario.")

        # 6. Validar coherencia tipo categoría/movimiento
        if categoria["tipo"] != data.tipo:
            raise ValidationException(
                f"Incoherencia de tipo: La categoría '{categoria['nombre']}' es de tipo '{categoria['tipo']}', "
                f"pero el movimiento fue enviado como '{data.tipo}'."
            )

        # 7. Ejecutar actualización
        actualizado = self._movimiento_repo.update(
            id_movimiento=id_movimiento,
            id_categoria=data.id_categoria,
            tipo=data.tipo,
            monto=data.monto,
            fecha=data.fecha,
            descripcion=data.descripcion,
        )

        return MovimientoResponse(
            id_movimiento=actualizado["id_movimiento"],
            id_usuario=actualizado["id_usuario"],
            id_categoria=actualizado["id_categoria"],
            categoria=actualizado["categoria"],
            tipo=actualizado["tipo"],
            monto=actualizado["monto"],
            fecha=actualizado["fecha"],
            descripcion=actualizado.get("descripcion"),
            fecha_creacion=actualizado.get("fecha_creacion"),
        )

    def eliminar_movimiento(
        self, id_movimiento: int, id_usuario: Optional[int] = None
    ) -> MensajeResponse:
        """
        Elimina un movimiento tras validar su existencia y su pertenencia.

        `id_usuario` es opcional para no romper el contrato ya aprobado del
        endpoint, pero cuando se envía se comprueba igual que en
        actualizar_movimiento: un usuario no puede borrar un movimiento ajeno.
        El frontend lo envía siempre.
        """
        movimiento = self._movimiento_repo.get_by_id(id_movimiento)
        if not movimiento:
            raise EntityNotFoundException(f"El movimiento con ID {id_movimiento} no existe.")

        # Validar pertenencia del movimiento al usuario que solicita el borrado.
        if id_usuario is not None and movimiento["id_usuario"] != id_usuario:
            raise ValidationException(
                "No tiene permisos para eliminar un movimiento que pertenece a otro usuario."
            )

        self._movimiento_repo.delete(id_movimiento)
        return MensajeResponse(mensaje="Movimiento eliminado con éxito")
