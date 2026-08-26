import bcrypt


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
