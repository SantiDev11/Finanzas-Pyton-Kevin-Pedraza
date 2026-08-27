from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

import bcrypt
import jwt

from app.core.config import settings
from app.core.exceptions import TokenExpiradoException, TokenInvalidoException


def hash_password(password: str) -> str:
    """
    Genera un hash seguro mediante bcrypt con salt aleatorio (cost factor 12).
    Nunca retorna ni almacena contraseñas en texto plano.
    """
    if not password:
        raise ValueError("La contraseña no puede estar vacía.")
    
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Comprueba si una contraseña en texto plano coincide con el hash bcrypt almacenado.
    """
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


# =============================================================================
# TOKENS DE ACCESO JWT
# =============================================================================

def crear_token_acceso(
    id_usuario: int,
    correo: str,
    expira_en_minutos: Optional[int] = None,
) -> Tuple[str, int]:
    """
    Firma un JWT de acceso para el usuario indicado.

    El `sub` (subject) es el identificador del usuario, en cadena como exige el
    RFC 7519. Se incluyen `exp` (expiración) e `iat` (emisión) para que la
    validación de caducidad la haga la propia librería.

    El token NO contiene la contraseña ni el hash: solo identidad y tiempos.

    Retorna
    -------
    (token, segundos_de_validez)
    """
    minutos = expira_en_minutos or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    emitido = datetime.now(timezone.utc)
    expira = emitido + timedelta(minutes=minutos)

    payload = {
        "sub": str(id_usuario),
        "correo": correo,
        "iat": emitido,
        "exp": expira,
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, minutos * 60


def decodificar_token_acceso(token: str) -> int:
    """
    Valida firma y expiración de un JWT y devuelve el id_usuario que contiene.

    Lanza TokenInvalidoException (401) ante cualquier problema: firma alterada,
    token caducado, algoritmo distinto del configurado, `sub` ausente o no
    numérico. El mensaje nunca detalla el motivo criptográfico concreto.
    """
    if not token:
        raise TokenInvalidoException()

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise TokenExpiradoException() from exc
    except jwt.InvalidTokenError as exc:
        raise TokenInvalidoException() from exc

    sub = payload.get("sub")
    try:
        id_usuario = int(sub)
    except (TypeError, ValueError) as exc:
        raise TokenInvalidoException() from exc

    if id_usuario <= 0:
        raise TokenInvalidoException()

    return id_usuario
