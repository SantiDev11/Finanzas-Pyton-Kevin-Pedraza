from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Optional

from app.core.exceptions import EntityNotFoundException
from app.core.periodo import PeriodoMensual, parse_periodo_mensual
from app.repositories.movimiento_repository import MovimientoRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.resumen import ResumenFinancieroResponse

# Precisión monetaria de la respuesta, coherente con DECIMAL(12,2) del esquema.
_DOS_DECIMALES = Decimal("0.01")
_CERO = Decimal("0.00")


class ResumenService:
    """
    Servicio de dominio para el cálculo del resumen financiero mensual.

    El backend es la única fuente de verdad del balance: los totales se agregan
    en la base de datos y la resta se realiza aquí con aritmética Decimal exacta.
    Ningún valor procede del cliente salvo los identificadores de la consulta.
    """

    def __init__(
        self,
        movimiento_repository: Optional[MovimientoRepository] = None,
        usuario_repository: Optional[UsuarioRepository] = None,
    ):
        self._movimiento_repo = movimiento_repository or MovimientoRepository()
        self._usuario_repo = usuario_repository or UsuarioRepository()

    def obtener_resumen_mensual(self, id_usuario: int, mes: str) -> ResumenFinancieroResponse:
        """
        Calcula el resumen financiero de un usuario para un periodo mensual.

        El orden de validación es intencionado: primero el periodo, que es una
        comprobación pura sin acceso a datos, y después la existencia del usuario.
        Así una petición con el mes mal formado se rechaza sin consultar la base
        de datos, y un usuario inexistente se detecta antes de agregar nada.
        """
        # 1. Validar el periodo solicitado (400 si es inválido)
        periodo = parse_periodo_mensual(mes)

        # 2. Validar la existencia del usuario (404 si no existe)
        self._validar_usuario_existente(id_usuario)

        # 3. Obtener los totales agregados por la base de datos
        totales = self._movimiento_repo.get_totales_por_periodo(
            id_usuario=id_usuario,
            inicio=periodo.inicio,
            fin_exclusivo=periodo.fin_exclusivo,
        )

        # 4. Construir la respuesta
        return self._construir_resumen(id_usuario=id_usuario, periodo=periodo, totales=totales)

    def _validar_usuario_existente(self, id_usuario: int) -> None:
        """Verifica que el usuario exista antes de realizar cálculo alguno."""
        if not self._usuario_repo.exists_by_id(id_usuario):
            raise EntityNotFoundException(f"El usuario con ID {id_usuario} no existe.")

    def _construir_resumen(
        self,
        id_usuario: int,
        periodo: PeriodoMensual,
        totales: Optional[dict],
    ) -> ResumenFinancieroResponse:
        """
        Normaliza los totales agregados y calcula el balance del periodo.

        Un periodo sin movimientos no es un error: la agregación devuelve ceros y
        el resumen se emite con total_ingresos, total_gastos y balance en 0.00.
        """
        fila = totales or {}
        total_ingresos = _a_decimal_monetario(fila.get("total_ingresos"))
        total_gastos = _a_decimal_monetario(fila.get("total_gastos"))

        # El balance puede ser negativo cuando los gastos superan a los ingresos.
        balance = total_ingresos - total_gastos

        return ResumenFinancieroResponse(
            id_usuario=id_usuario,
            mes=periodo.mes,
            total_ingresos=total_ingresos,
            total_gastos=total_gastos,
            balance=balance,
        )


def _a_decimal_monetario(valor: Any) -> Decimal:
    """
    Convierte un valor agregado por MySQL en un Decimal con dos decimales.

    Se pasa por str() en lugar de float() para no introducir el error de
    representación binaria que precisamente se quiere evitar en importes.
    """
    if valor is None:
        return _CERO
    decimal_valor = valor if isinstance(valor, Decimal) else Decimal(str(valor))
    return decimal_valor.quantize(_DOS_DECIMALES, rounding=ROUND_HALF_UP)
