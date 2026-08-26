from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_usuario_service
from app.schemas.usuario import UsuarioCreate, UsuarioResponse
from app.services.usuario_service import UsuarioService

router = APIRouter(
    prefix="/api/usuarios",
    tags=["Usuarios"]
)


@router.post(
    "",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
    description="Crea un nuevo usuario con contraseña cifrada mediante bcrypt. No expone hashes en la respuesta."
)
def registrar_usuario(
    payload: UsuarioCreate,
    service: UsuarioService = Depends(get_usuario_service)
) -> UsuarioResponse:
    """
    Endpoint para el registro básico de usuarios (RF01).
    """
    return service.registrar_usuario(payload)
