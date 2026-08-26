import logging
from contextlib import contextmanager
from typing import Generator, Any, Optional
import pymysql
import pymysql.cursors

from app.core.config import settings
from app.core.exceptions import DatabaseException

logger = logging.getLogger(__name__)


def create_connection(custom_config: Optional[dict] = None) -> pymysql.Connection:
    """
    Crea una nueva conexión a MySQL usando la configuración centralizada.
    """
    config = custom_config or settings.get_db_config()
    try:
        connection = pymysql.connect(
            host=config["host"],
            port=config["port"],
            user=config["user"],
            password=config["password"],
            database=config["database"],
            charset=config.get("charset", "utf8mb4"),
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )
        return connection
    except pymysql.MySQLError as err:
        logger.error("Fallo al conectar con la base de datos MySQL: %s", str(err))
        raise DatabaseException("No fue posible establecer conexión con la base de datos.") from err


@contextmanager
def get_db_cursor(connection: Optional[pymysql.Connection] = None) -> Generator[pymysql.cursors.DictCursor, None, None]:
    """
    Context manager para manejo seguro de transacciones y cursores con diccionario.
    Realiza commit automático al finalizar con éxito y rollback si ocurre una excepción.
    """
    owns_connection = connection is None
    conn = connection or create_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as exc:
        conn.rollback()
        logger.error("Error durante transacción de base de datos: %s", str(exc))
        if isinstance(exc, DatabaseException):
            raise exc
        if isinstance(exc, pymysql.MySQLError):
            raise DatabaseException(f"Error de base de datos: {exc.args[1] if len(exc.args) > 1 else str(exc)}") from exc
        raise exc
    finally:
        cursor.close()
        if owns_connection:
            conn.close()


def get_db() -> Generator[pymysql.Connection, None, None]:
    """
    Generador para inyección de dependencias de FastAPI (yield connection).
    """
    conn = create_connection()
    try:
        yield conn
    finally:
        conn.close()
