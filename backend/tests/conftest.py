from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
import pytest
from fastapi.testclient import TestClient

from app.core.dependencies import (
    get_categoria_service,
    get_movimiento_service,
    get_usuario_service,
)
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.movimiento_repository import MovimientoRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.services.categoria_service import CategoriaService
from app.services.movimiento_service import MovimientoService
from app.services.usuario_service import UsuarioService
from main import app


class InMemoryUsuarioRepository(UsuarioRepository):
    """Repositorio en memoria para usuarios en tests aislados."""

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
            "fecha_registro": datetime.now(),
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
            "id_usuario": id_usuario,
        }
        self.categorias[cat_id] = record
        return record

    def get_by_id(self, id_categoria: int) -> Optional[Dict[str, Any]]:
        return self.categorias.get(id_categoria)

    def list_by_user(self, id_usuario: int) -> List[Dict[str, Any]]:
        return [cat for cat in self.categorias.values() if cat["id_usuario"] == id_usuario]

    def exists_by_user_type_name(self, id_usuario: int, tipo: str, nombre: str) -> bool:
        for cat in self.categorias.values():
            if (
                cat["id_usuario"] == id_usuario
                and cat["tipo"] == tipo
                and cat["nombre"].lower() == nombre.lower()
            ):
                return True
        return False


class InMemoryMovimientoRepository(MovimientoRepository):
    """Repositorio en memoria para movimientos en tests aislados."""

    def __init__(self, categoria_repo: Optional[InMemoryCategoriaRepository] = None):
        super().__init__(connection=None)
        self.movimientos: Dict[int, Dict[str, Any]] = {}
        self.categoria_repo = categoria_repo
        self._next_id = 1

    def create(
        self,
        id_usuario: int,
        id_categoria: int,
        tipo: str,
        monto: Decimal,
        fecha: date,
        descripcion: Optional[str],
    ) -> Dict[str, Any]:
        mov_id = self._next_id
        self._next_id += 1
        cat_nombre = "Categoría"
        if self.categoria_repo:
            cat = self.categoria_repo.get_by_id(id_categoria)
            if cat:
                cat_nombre = cat["nombre"]

        record = {
            "id_movimiento": mov_id,
            "id_usuario": id_usuario,
            "id_categoria": id_categoria,
            "categoria": cat_nombre,
            "tipo": tipo,
            "monto": monto,
            "fecha": fecha,
            "descripcion": descripcion,
            "fecha_creacion": datetime.now(),
        }
        self.movimientos[mov_id] = record
        return record

    def get_by_id(self, id_movimiento: int) -> Optional[Dict[str, Any]]:
        return self.movimientos.get(id_movimiento)

    def list_by_filters(
        self,
        id_usuario: int,
        desde: Optional[date] = None,
        hasta: Optional[date] = None,
        id_categoria: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        res = [
            m for m in self.movimientos.values() if m["id_usuario"] == id_usuario
        ]
        if desde is not None:
            res = [m for m in res if m["fecha"] >= desde]
        if hasta is not None:
            res = [m for m in res if m["fecha"] <= hasta]
        if id_categoria is not None:
            res = [m for m in res if m["id_categoria"] == id_categoria]

        # Ordenar por fecha DESC, id_movimiento DESC
        res.sort(key=lambda x: (x["fecha"], x["id_movimiento"]), reverse=True)
        return res

    def update(
        self,
        id_movimiento: int,
        id_categoria: int,
        tipo: str,
        monto: Decimal,
        fecha: date,
        descripcion: Optional[str],
    ) -> Dict[str, Any]:
        if id_movimiento not in self.movimientos:
            raise KeyError("Movimiento no encontrado")

        cat_nombre = self.movimientos[id_movimiento]["categoria"]
        if self.categoria_repo:
            cat = self.categoria_repo.get_by_id(id_categoria)
            if cat:
                cat_nombre = cat["nombre"]

        self.movimientos[id_movimiento].update({
            "id_categoria": id_categoria,
            "categoria": cat_nombre,
            "tipo": tipo,
            "monto": monto,
            "fecha": fecha,
            "descripcion": descripcion,
        })
        return self.movimientos[id_movimiento]

    def delete(self, id_movimiento: int) -> bool:
        if id_movimiento in self.movimientos:
            del self.movimientos[id_movimiento]
            return True
        return False


@pytest.fixture
def fake_usuario_repo() -> InMemoryUsuarioRepository:
    repo = InMemoryUsuarioRepository()
    repo.create(
        nombre="Usuario Prueba",
        correo="test@example.com",
        contrasena_hash="$2b$12$eImiTXuWVxfM37uY4JANjOL.88T9qqQadO03p863/H021.282.",
    )
    return repo


@pytest.fixture
def fake_categoria_repo() -> InMemoryCategoriaRepository:
    return InMemoryCategoriaRepository()


@pytest.fixture
def fake_movimiento_repo(fake_categoria_repo) -> InMemoryMovimientoRepository:
    return InMemoryMovimientoRepository(categoria_repo=fake_categoria_repo)


@pytest.fixture
def usuario_service(fake_usuario_repo) -> UsuarioService:
    return UsuarioService(usuario_repository=fake_usuario_repo)


@pytest.fixture
def categoria_service(fake_categoria_repo, fake_usuario_repo) -> CategoriaService:
    return CategoriaService(
        categoria_repository=fake_categoria_repo,
        usuario_repository=fake_usuario_repo,
    )


@pytest.fixture
def movimiento_service(
    fake_movimiento_repo, fake_usuario_repo, fake_categoria_repo
) -> MovimientoService:
    # Sembrar categorías base para las pruebas de movimientos si no existen
    if not fake_categoria_repo.exists_by_user_type_name(1, "ingreso", "Salario"):
        fake_categoria_repo.create(nombre="Salario", tipo="ingreso", id_usuario=1)
    if not fake_categoria_repo.exists_by_user_type_name(1, "gasto", "Alimentación"):
        fake_categoria_repo.create(nombre="Alimentación", tipo="gasto", id_usuario=1)

    return MovimientoService(
        movimiento_repository=fake_movimiento_repo,
        usuario_repository=fake_usuario_repo,
        categoria_repository=fake_categoria_repo,
    )


@pytest.fixture
def client(usuario_service, categoria_service, movimiento_service) -> TestClient:
    """Cliente HTTP con dependencias sobreescritas para pruebas de integración aisladas."""
    app.dependency_overrides[get_usuario_service] = lambda: usuario_service
    app.dependency_overrides[get_categoria_service] = lambda: categoria_service
    app.dependency_overrides[get_movimiento_service] = lambda: movimiento_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
