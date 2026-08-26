from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Usuario:
    """Entidad de dominio que representa a un Usuario registrado."""
    id_usuario: Optional[int]
    nombre: str
    correo: str
    contrasena_hash: str
    fecha_registro: Optional[datetime] = None


@dataclass
class Categoria:
    """Entidad de dominio que representa una Categoría de ingresos o gastos."""
    id_categoria: Optional[int]
    nombre: str
    tipo: str  # 'ingreso' | 'gasto'
    id_usuario: int
