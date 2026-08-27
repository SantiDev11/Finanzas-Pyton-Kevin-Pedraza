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
