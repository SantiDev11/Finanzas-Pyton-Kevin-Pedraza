from datetime import datetime
from typing import Dict, List, Optional, Any
import pytest
from fastapi.testclient import TestClient

from app.core.dependencies import get_usuario_service, get_categoria_service
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.categoria_repository import CategoriaRepository
from app.services.usuario_service import UsuarioService
from app.services.categoria_service import CategoriaService
from main import app


class InMemoryUsuarioRepository(UsuarioRepository):
    """Repositorio en memoria para tests aislados y deterministas."""

    def __init__(self):
        super().__init__(connection=None)
        self.usuarios: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1

    def create(self, nombre: str, correo: str, contrasena_hash: str) -> Dict[str, Any]:
        user_id = self._next_id
        self._next_id += 1
        record = {
            "id_usuario": user_id,
            "nombre": nombre,
            "correo": correo,
            "contrasena_hash": contrasena_hash,
            "fecha_registro": datetime.now()
        }
        self.usuarios[user_id] = record
        return record

    def get_by_id(self, id_usuario: int) -> Optional[Dict[str, Any]]:
        return self.usuarios.get(id_usuario)

    def get_by_email(self, correo: str) -> Optional[Dict[str, Any]]:
        for user in self.usuarios.values():
            if user["correo"].lower() == correo.lower():
                return user
        return None

    def exists_by_email(self, correo: str) -> bool:
        return self.get_by_email(correo) is not None

    def exists_by_id(self, id_usuario: int) -> bool:
        return id_usuario in self.usuarios


class InMemoryCategoriaRepository(CategoriaRepository):
    """Repositorio en memoria para categorías en tests aislados."""

    def __init__(self):
        super().__init__(connection=None)
        self.categorias: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1

    def create(self, nombre: str, tipo: str, id_usuario: int) -> Dict[str, Any]:
        cat_id = self._next_id
        self._next_id += 1
        record = {
            "id_categoria": cat_id,
            "nombre": nombre,
            "tipo": tipo,
            "id_usuario": id_usuario
        }
        self.categorias[cat_id] = record
        return record

    def get_by_id(self, id_categoria: int) -> Optional[Dict[str, Any]]:
        return self.categorias.get(id_categoria)

    def list_by_user(self, id_usuario: int) -> List[Dict[str, Any]]:
        return [cat for cat in self.categorias.values() if cat["id_usuario"] == id_usuario]

    def exists_by_user_type_name(self, id_usuario: int, tipo: str, nombre: str) -> bool:
        for cat in self.categorias.values():
            if (cat["id_usuario"] == id_usuario and
                cat["tipo"] == tipo and
                cat["nombre"].lower() == nombre.lower()):
                return True
        return False


@pytest.fixture
def fake_usuario_repo() -> InMemoryUsuarioRepository:
    repo = InMemoryUsuarioRepository()
    # Sembrar un usuario inicial para tests de categorías
    repo.create(
        nombre="Usuario Prueba",
        correo="test@example.com",
        contrasena_hash="$2b$12$eImiTXuWVxfM37uY4JANjOL.88T9qqQadO03p863/H021.282."
    )
    return repo


@pytest.fixture
def fake_categoria_repo() -> InMemoryCategoriaRepository:
    return InMemoryCategoriaRepository()


@pytest.fixture
def usuario_service(fake_usuario_repo) -> UsuarioService:
    return UsuarioService(usuario_repository=fake_usuario_repo)


@pytest.fixture
def categoria_service(fake_categoria_repo, fake_usuario_repo) -> CategoriaService:
    return CategoriaService(
        categoria_repository=fake_categoria_repo,
        usuario_repository=fake_usuario_repo
    )


@pytest.fixture
def client(usuario_service, categoria_service) -> TestClient:
    """Cliente HTTP con dependencias sobreescritas para pruebas de integración aisladas."""
    app.dependency_overrides[get_usuario_service] = lambda: usuario_service
    app.dependency_overrides[get_categoria_service] = lambda: categoria_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
