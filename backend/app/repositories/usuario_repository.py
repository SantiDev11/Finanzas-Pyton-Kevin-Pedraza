from typing import Optional, Dict, Any
import pymysql

from app.database.connection import get_db_cursor


class UsuarioRepository:
    """
    Repositorio de persistencia para la entidad Usuarios.
    Encapsula consultas SQL puras y parametrizadas sobre MySQL.
    """

    def __init__(self, connection: Optional[pymysql.Connection] = None):
        self._connection = connection

    def create(self, nombre: str, correo: str, contrasena_hash: str) -> Dict[str, Any]:
        """
        Inserta un nuevo registro de usuario en la base de datos.
        """
        sql = """
            INSERT INTO usuarios (nombre, correo, contrasena_hash)
            VALUES (%s, %s, %s)
        """
        with get_db_cursor(self._connection) as cursor:
            cursor.execute(sql, (nombre, correo, contrasena_hash))
            new_id = cursor.lastrowid

            # Consultar el registro recién insertado para retornar fecha_registro generada por MySQL
            cursor.execute(
                "SELECT id_usuario, nombre, correo, fecha_registro FROM usuarios WHERE id_usuario = %s",
                (new_id,)
            )
            return cursor.fetchone()

    def get_by_id(self, id_usuario: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un usuario por su identificador primario.
        """
        sql = """
            SELECT id_usuario, nombre, correo, contrasena_hash, fecha_registro
            FROM usuarios
            WHERE id_usuario = %s
        """
        with get_db_cursor(self._connection) as cursor:
            cursor.execute(sql, (id_usuario,))
            return cursor.fetchone()

    def get_by_email(self, correo: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un usuario por su correo electrónico.
        """
        sql = """
            SELECT id_usuario, nombre, correo, contrasena_hash, fecha_registro
            FROM usuarios
            WHERE correo = %s
        """
        with get_db_cursor(self._connection) as cursor:
            cursor.execute(sql, (correo,))
            return cursor.fetchone()

    def exists_by_email(self, correo: str) -> bool:
        """
        Verifica de manera eficiente si existe un usuario con el correo dado.
        """
        sql = "SELECT 1 FROM usuarios WHERE correo = %s LIMIT 1"
        with get_db_cursor(self._connection) as cursor:
            cursor.execute(sql, (correo,))
            return cursor.fetchone() is not None

    def exists_by_id(self, id_usuario: int) -> bool:
        """
        Verifica si existe un usuario con el id_usuario dado.
        """
        sql = "SELECT 1 FROM usuarios WHERE id_usuario = %s LIMIT 1"
        with get_db_cursor(self._connection) as cursor:
            cursor.execute(sql, (id_usuario,))
            return cursor.fetchone() is not None
