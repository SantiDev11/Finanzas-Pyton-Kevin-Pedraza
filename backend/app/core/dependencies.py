from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.movimiento_repository import MovimientoRepository
from app.services.usuario_service import UsuarioService
from app.services.categoria_service import CategoriaService
from app.services.movimiento_service import MovimientoService
from app.services.resumen_service import ResumenService
from app.services.analitica_service import AnaliticaService


def get_usuario_service() -> UsuarioService:
    """Inyector del servicio de usuarios."""
    repo = UsuarioRepository()
    return UsuarioService(usuario_repository=repo)


def get_categoria_service() -> CategoriaService:
    """Inyector del servicio de categorías."""
    cat_repo = CategoriaRepository()
    usr_repo = UsuarioRepository()
    return CategoriaService(categoria_repository=cat_repo, usuario_repository=usr_repo)


def get_movimiento_service() -> MovimientoService:
    """Inyector del servicio de movimientos financieros."""
    mov_repo = MovimientoRepository()
    usr_repo = UsuarioRepository()
    cat_repo = CategoriaRepository()
    return MovimientoService(
        movimiento_repository=mov_repo,
        usuario_repository=usr_repo,
        categoria_repository=cat_repo
    )


def get_resumen_service() -> ResumenService:
    """Inyector del servicio de resumen financiero."""
    mov_repo = MovimientoRepository()
    usr_repo = UsuarioRepository()
    return ResumenService(
        movimiento_repository=mov_repo,
        usuario_repository=usr_repo
    )


def get_analitica_service() -> AnaliticaService:
    """Inyector del servicio de analítica financiera."""
    mov_repo = MovimientoRepository()
    usr_repo = UsuarioRepository()
    return AnaliticaService(
        movimiento_repository=mov_repo,
        usuario_repository=usr_repo
    )

