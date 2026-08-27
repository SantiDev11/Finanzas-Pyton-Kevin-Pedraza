from typing import Optional, List, Dict, Any
import pymysql

from app.database.connection import get_db_cursor


class CategoriaRepository:
    """
    Repositorio de persistencia para la entidad Categorías.
    Maneja las operaciones CRUD sobre la tabla categorias mediante SQL parametrizado.
    """

    def __init__(self, connection: Optional[pymysql.Connection] = None):
        self._connection = connection

    def create(self, nombre: str, tipo: str, id_usuario: int) -> Dict[str, Any]:
        """
        Inserta una nueva categoría asociada a un usuario.
        """
        sql = """
            INSERT INTO categorias (nombre, tipo, id_usuario)
            VALUES (%s, %s, %s)
        """
        with get_db_cursor(self._connection) as cursor:
            cursor.execute(sql, (nombre, tipo, id_usuario))
            new_id = cursor.lastrowid
            return {
                "id_categoria": new_id,
                "nombre": nombre,
                "tipo": tipo,
                "id_usuario": id_usuario
            }

    def get_by_id(self, id_categoria: int) -> Optional[Dict[str, Any]]:
        """
        Consulta una categoría por su identificador primario.
        """
        sql = """
            SELECT id_categoria, nombre, tipo, id_usuario
            FROM categorias
            WHERE id_categoria = %s
        """
        with get_db_cursor(self._connection) as cursor:
            cursor.execute(sql, (id_categoria,))
            return cursor.fetchone()

    def list_by_user(self, id_usuario: int) -> List[Dict[str, Any]]:
        """
        Lista todas las categorías pertenecientes a un usuario específico.
        """
        sql = """
            SELECT id_categoria, nombre, tipo, id_usuario
            FROM categorias
            WHERE id_usuario = %s
            ORDER BY tipo DESC, nombre ASC
        """
        with get_db_cursor(self._connection) as cursor:
            cursor.execute(sql, (id_usuario,))
            return cursor.fetchall()

    def exists_by_user_type_name(self, id_usuario: int, tipo: str, nombre: str) -> bool:
        """
        Comprueba si ya existe una categoría con el mismo nombre y tipo para el usuario dado.
        """
        sql = """
            SELECT 1 FROM categorias
            WHERE id_usuario = %s AND tipo = %s AND nombre = %s
            LIMIT 1
        """
        with get_db_cursor(self._connection) as cursor:
            cursor.execute(sql, (id_usuario, tipo, nombre))
            return cursor.fetchone() is not None

    def exists_by_user_type_name_excluding_id(
        self, id_usuario: int, tipo: str, nombre: str, exclude_id: int
    ) -> bool:
        """
        Comprueba si ya existe otra categoría con el mismo nombre y tipo para el usuario,
        excluyendo la categoría con el ID indicado (útil para validación en edición).
        """
        sql = """
            SELECT 1 FROM categorias
            WHERE id_usuario = %s AND tipo = %s AND nombre = %s AND id_categoria != %s
            LIMIT 1
        """
        with get_db_cursor(self._connection) as cursor:
            cursor.execute(sql, (id_usuario, tipo, nombre, exclude_id))
            return cursor.fetchone() is not None

    def update(self, id_categoria: int, nombre: str, tipo: str) -> Dict[str, Any]:
        """
        Actualiza los datos de una categoría existente.
        """
        sql_update = """
            UPDATE categorias
            SET nombre = %s, tipo = %s
            WHERE id_categoria = %s
        """
        with get_db_cursor(self._connection) as cursor:
            cursor.execute(sql_update, (nombre, tipo, id_categoria))
            sql_select = "SELECT id_categoria, nombre, tipo, id_usuario FROM categorias WHERE id_categoria = %s"
            cursor.execute(sql_select, (id_categoria,))
            return cursor.fetchone()

    def delete(self, id_categoria: int) -> bool:
        """
        Elimina una categoría por su identificador primario.
        """
        sql = "DELETE FROM categorias WHERE id_categoria = %s"
        with get_db_cursor(self._connection) as cursor:
            cursor.execute(sql, (id_categoria,))
            return cursor.rowcount > 0

    def has_movimientos(self, id_categoria: int) -> bool:
        """
        Verifica si existen movimientos asociados a la categoría.
        """
        sql = "SELECT 1 FROM ingresos_gastos WHERE id_categoria = %s LIMIT 1"
        with get_db_cursor(self._connection) as cursor:
            cursor.execute(sql, (id_categoria,))
            return cursor.fetchone() is not None

