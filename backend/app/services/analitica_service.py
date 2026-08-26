"""
Servicio de dominio para el módulo analítico.

Coordina:
  Repository  →  Analytics  →  Response Schemas

No contiene lógica de Pandas ni SQL directamente. Delega:
  - la obtención de datos al repositorio;
  - el procesamiento estadístico a analytics/prediction.py y analytics/anomalies.py;
  - la serialización a los schemas Pydantic.
"""

from typing import Optional

from app.analytics.anomalies import UMBRAL_Z_SCORE, detectar_anomalias
from app.analytics.prediction import predecir_gasto_proximo_mes
from app.core.exceptions import EntityNotFoundException
from app.repositories.movimiento_repository import MovimientoRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.analitica import (
    AnomaliaItem,
    AnomaliasResponse,
    PrediccionResponse,
)


class AnaliticaService:
    """
    Servicio que orquesta la ejecución de los algoritmos analíticos sobre datos
    reales del usuario, aplicando las validaciones de dominio necesarias.
    """

    def __init__(
        self,
        movimiento_repository: Optional[MovimientoRepository] = None,
        usuario_repository: Optional[UsuarioRepository] = None,
    ):
        self._movimiento_repo = movimiento_repository or MovimientoRepository()
        self._usuario_repo = usuario_repository or UsuarioRepository()

    def obtener_prediccion(self, id_usuario: int) -> PrediccionResponse:
        """
        Obtiene la predicción de gastos del próximo mes para un usuario.

        1. Valida existencia del usuario.
        2. Obtiene los gastos históricos del repositorio.
        3. Delega el análisis a analytics/prediction.py.
        4. Construye la respuesta tipada.
        """
        self._validar_usuario_existente(id_usuario)

        gastos = self._movimiento_repo.list_gastos_por_usuario(id_usuario)

        resultado = predecir_gasto_proximo_mes(gastos)

        return PrediccionResponse(
            id_usuario=id_usuario,
            mes_predicho=resultado["mes_predicho"],
            gasto_estimado=resultado["gasto_estimado"],
            confianza=resultado["confianza"],
            razon=resultado["razon"],
            meses_procesados=resultado["meses_procesados"],
        )

    def obtener_anomalias(self, id_usuario: int) -> AnomaliasResponse:
        """
        Detecta gastos atípicos para un usuario usando Z-Score por categoría.

        1. Valida existencia del usuario.
        2. Obtiene los gastos del repositorio.
        3. Delega la detección a analytics/anomalies.py.
        4. Construye la respuesta tipada.
        """
        self._validar_usuario_existente(id_usuario)

        gastos = self._movimiento_repo.list_gastos_por_usuario(id_usuario)

        anomalias_raw = detectar_anomalias(gastos)

        anomalias_items = [
            AnomaliaItem(
                id_movimiento=a["id_movimiento"],
                fecha=a["fecha"],
                monto=a["monto"],
                id_categoria=a["id_categoria"],
                promedio_categoria=a["promedio_categoria"],
                z_score=a["z_score"],
                descripcion=a.get("descripcion"),
            )
            for a in anomalias_raw
        ]

        return AnomaliasResponse(
            id_usuario=id_usuario,
            umbral_z_score=UMBRAL_Z_SCORE,
            total_gastos_analizados=len(gastos),
            total_anomalias=len(anomalias_items),
            anomalias=anomalias_items,
        )

    def _validar_usuario_existente(self, id_usuario: int) -> None:
        """Verifica que el usuario exista antes de ejecutar análisis."""
        if not self._usuario_repo.exists_by_id(id_usuario):
            raise EntityNotFoundException(
                f"El usuario con ID {id_usuario} no existe."
            )
