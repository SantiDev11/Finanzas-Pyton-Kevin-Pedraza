from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
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


@dataclass
class Movimiento:
    """Entidad de dominio que representa un Movimiento financiero (ingreso o gasto)."""
    id_movimiento: Optional[int]
    id_usuario: int
    id_categoria: int
    tipo: str  # 'ingreso' | 'gasto'
    monto: Decimal
    fecha: date
    descripcion: Optional[str] = None
    fecha_creacion: Optional[datetime] = None
