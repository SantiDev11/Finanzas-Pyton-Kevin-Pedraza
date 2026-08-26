import pytest
from app.core.exceptions import DuplicateEntityException
from app.core.security import verify_password
from app.schemas.usuario import UsuarioCreate
from app.services.usuario_service import UsuarioService


def test_service_crear_usuario_exitoso(usuario_service: UsuarioService, fake_usuario_repo):
    data = UsuarioCreate(
        nombre="Carlos Ruiz",
        correo="carlos@example.com",
        contrasena="Password123*"
    )
    res = usuario_service.registrar_usuario(data)

    assert res.id_usuario > 0
    assert res.nombre == "Carlos Ruiz"
    assert res.correo == "carlos@example.com"
    assert not hasattr(res, "contrasena")
    assert not hasattr(res, "contrasena_hash")

    # Verificar que en el repositorio el hash guardado sea válido con bcrypt
    guardado = fake_usuario_repo.get_by_id(res.id_usuario)
    assert guardado is not None
    assert guardado["contrasena_hash"] != "Password123*"
    assert verify_password("Password123*", guardado["contrasena_hash"]) is True


def test_service_crear_usuario_correo_duplicado(usuario_service: UsuarioService):
    data = UsuarioCreate(
        nombre="Usuario Repetido",
        correo="test@example.com",  # Ya existe en el fake repo
        contrasena="Password123*"
    )
    with pytest.raises(DuplicateEntityException) as exc_info:
        usuario_service.registrar_usuario(data)

    assert "ya se encuentra registrado" in str(exc_info.value.message)
