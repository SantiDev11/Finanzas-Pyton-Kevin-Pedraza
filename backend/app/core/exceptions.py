class AppException(Exception):
    """Excepción base para errores de la aplicación."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class EntityNotFoundException(AppException):
    """Excepción lanzada cuando un recurso no existe (404)."""
    def __init__(self, message: str = "Recurso no encontrado"):
        super().__init__(message=message, status_code=404)


class DuplicateEntityException(AppException):
    """Excepción lanzada ante conflictos de unicidad (409 Conflict)."""
    def __init__(self, message: str = "El recurso ya existe o entra en conflicto"):
        super().__init__(message=message, status_code=409)


class ValidationException(AppException):
    """Excepción lanzada ante datos de negocio inválidos (400 Bad Request)."""
    def __init__(self, message: str = "Datos de solicitud inválidos"):
        super().__init__(message=message, status_code=400)


class DatabaseException(AppException):
    """Excepción lanzada ante fallos en la capa de persistencia (500)."""
    def __init__(self, message: str = "Error interno de base de datos"):
        super().__init__(message=message, status_code=500)


class AuthenticationException(AppException):
    """
    Excepción base para fallos de autenticación (401 Unauthorized).

    El mensaje por defecto es deliberadamente genérico: distinguir entre
    "el correo no existe" y "la contraseña es incorrecta" permitiría enumerar
    las cuentas registradas.
    """
    def __init__(self, message: str = "Credenciales inválidas"):
        super().__init__(message=message, status_code=401)


class TokenInvalidoException(AuthenticationException):
    """Token ausente, malformado o con firma no válida (401)."""
    def __init__(self, message: str = "Token de acceso inválido o ausente"):
        super().__init__(message=message)


class TokenExpiradoException(AuthenticationException):
    """Token correctamente firmado pero caducado (401)."""
    def __init__(self, message: str = "La sesión ha expirado. Vuelve a iniciar sesión."):
        super().__init__(message=message)
