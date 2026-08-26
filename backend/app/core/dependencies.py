from typing import Generator
import pymysql

from app.database.connection import create_connection
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.categoria_repository import CategoriaRepository
from app.services.usuario_service import UsuarioService
from app.services.categoria_service import CategoriaService


def get_db_connection() -> Generator[pymysql.Connection, None, None]:
    """Inyector de conexión a MySQL."""
    conn = create_connection()
    try:
        yield conn
    finally:
        conn.close()


def get_usuario_service() -> UsuarioService:
    """Inyector del servicio de usuarios."""
    repo = UsuarioRepository()
    return UsuarioService(usuario_repository=repo)


def get_categoria_service() -> CategoriaService:
    """Inyector del servicio de categorías."""
    cat_repo = CategoriaRepository()
    usr_repo = UsuarioRepository()
    return CategoriaService(categoria_repository=cat_repo, usuario_repository=usr_repo)
