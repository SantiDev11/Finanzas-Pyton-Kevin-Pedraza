from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional
import pymysql

from app.database.connection import get_db_cursor


class MovimientoRepository:
    """
    Repositorio de persistencia para la entidad ingresos_gastos.
    Ejecuta consultas SQL puras y parametrizadas para la gestión de transacciones.
    """

    def __init__(self, connection: Optional[pymysql.Connection] = None):
        self._connection = connection

    def create(
        self,
        id_usuario: int,
        id_categoria: int,
        tipo: str,
        monto: Decimal,
        fecha: date,
        descripcion: Optional[str]
    ) -> Dict[str, Any]:
        """
        Inserta un nuevo movimiento financiero en la tabla ingresos_gastos.
        """
        sql_insert = """
            INSERT INTO ingresos_gastos (id_usuario, id_categoria, tipo, monto, fecha, descripcion)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        with get_db_cursor(self._connection) as cursor:
            cursor.execute(sql_insert, (id_usuario, id_categoria, tipo, monto, fecha, descripcion))
            new_id = cursor.lastrowid

            # Consultar el movimiento con el nombre de su categoría asociada
            sql_select = """
                SELECT 
                    m.id_movimiento,
                    m.id_usuario,
                    m.id_categoria,
                    c.nombre AS categoria,
                    m.tipo,
                    m.monto,
                    m.fecha,
                    m.descripcion,
                    m.fecha_creacion
                FROM ingresos_gastos m
                INNER JOIN categorias c ON m.id_categoria = c.id_categoria
                WHERE m.id_movimiento = %s
            """
            cursor.execute(sql_select, (new_id,))
            return cursor.fetchone()

    def get_by_id(self, id_movimiento: int) -> Optional[Dict[str, Any]]:
        """
        Consulta un movimiento por su ID primario, incluyendo el nombre de la categoría.
        """
        sql = """
            SELECT 
                m.id_movimiento,
                m.id_usuario,
                m.id_categoria,
                c.nombre AS categoria,
                m.tipo,
                m.monto,
                m.fecha,
                m.descripcion,
                m.fecha_creacion
            FROM ingresos_gastos m
            INNER JOIN categorias c ON m.id_categoria = c.id_categoria
            WHERE m.id_movimiento = %s
        """
        with get_db_cursor(self._connection) as cursor:
            cursor.execute(sql, (id_movimiento,))
            return cursor.fetchone()

    def list_by_filters(
        self,
        id_usuario: int,
        desde: Optional[date] = None,
        hasta: Optional[date] = None,
        id_categoria: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Lista los movimientos de un usuario aplicando filtros opcionales de fecha y categoría.
        Ordenamiento consistente: fecha DESC, id_movimiento DESC.
        """
        sql = """
            SELECT 
                m.id_movimiento,
                m.id_usuario,
                m.id_categoria,
                c.nombre AS categoria,
                m.tipo,
                m.monto,
                m.fecha,
                m.descripcion,
                m.fecha_creacion
            FROM ingresos_gastos m
            INNER JOIN categorias c ON m.id_categoria = c.id_categoria
            WHERE m.id_usuario = %s
        """
        params: List[Any] = [id_usuario]

        if desde is not None:
            sql += " AND m.fecha >= %s"
            params.append(desde)

        if hasta is not None:
            sql += " AND m.fecha <= %s"
            params.append(hasta)

        if id_categoria is not None:
            sql += " AND m.id_categoria = %s"
            params.append(id_categoria)

        sql += " ORDER BY m.fecha DESC, m.id_movimiento DESC"

        with get_db_cursor(self._connection) as cursor:
            cursor.execute(sql, tuple(params))
            return cursor.fetchall()

    def update(
        self,
        id_movimiento: int,
        id_categoria: int,
        tipo: str,
        monto: Decimal,
        fecha: date,
        descripcion: Optional[str]
    ) -> Dict[str, Any]:
        """
        Actualiza los datos de un movimiento existente y retorna el registro actualizado.
        """
        sql_update = """
            UPDATE ingresos_gastos
            SET id_categoria = %s, tipo = %s, monto = %s, fecha = %s, descripcion = %s
            WHERE id_movimiento = %s
        """
        with get_db_cursor(self._connection) as cursor:
            cursor.execute(sql_update, (id_categoria, tipo, monto, fecha, descripcion, id_movimiento))

            sql_select = """
                SELECT 
                    m.id_movimiento,
                    m.id_usuario,
                    m.id_categoria,
                    c.nombre AS categoria,
                    m.tipo,
                    m.monto,
                    m.fecha,
                    m.descripcion,
                    m.fecha_creacion
                FROM ingresos_gastos m
                INNER JOIN categorias c ON m.id_categoria = c.id_categoria
                WHERE m.id_movimiento = %s
            """
            cursor.execute(sql_select, (id_movimiento,))
            return cursor.fetchone()

    def delete(self, id_movimiento: int) -> bool:
        """
        Elimina un movimiento por su ID primario. Retorna True si se eliminó alguna fila.
        """
        sql = "DELETE FROM ingresos_gastos WHERE id_movimiento = %s"
        with get_db_cursor(self._connection) as cursor:
            cursor.execute(sql, (id_movimiento,))
            return cursor.rowcount > 0

    def get_totales_por_periodo(
        self,
        id_usuario: int,
        inicio: date,
        fin_exclusivo: date
    ) -> Dict[str, Any]:
        """
        Agrega los totales de ingresos y gastos de un usuario dentro de un periodo.

        La agregación se resuelve íntegramente en MySQL con una única consulta que
        devuelve una sola fila: no se transfieren los movimientos individuales a
        Python ni se realizan consultas adicionales por tipo (evita N+1).

        El filtro de fechas usa el rango semiabierto [inicio, fin_exclusivo). Se
        compara la columna `fecha` directamente, sin DATE_FORMAT() ni YEAR()/MONTH(),
        porque envolverla en una función impediría al optimizador usar el índice
        idx_mov_usuario_fecha y forzaría un recorrido completo de la tabla.

        Si no hay movimientos, la consulta devuelve igualmente una fila con ceros
        gracias a COALESCE, de modo que la capa superior no necesita casos especiales.
        """
        sql = """
            SELECT
                COALESCE(SUM(CASE WHEN tipo = 'ingreso' THEN monto END), 0) AS total_ingresos,
                COALESCE(SUM(CASE WHEN tipo = 'gasto'   THEN monto END), 0) AS total_gastos
            FROM ingresos_gastos
            WHERE id_usuario = %s
              AND fecha >= %s
              AND fecha <  %s
        """
        with get_db_cursor(self._connection) as cursor:
            cursor.execute(sql, (id_usuario, inicio, fin_exclusivo))
            return cursor.fetchone()

    def list_gastos_por_usuario(self, id_usuario: int) -> List[Dict[str, Any]]:
        """
        Obtiene todos los gastos de un usuario para análisis estadístico.

        Devuelve únicamente los campos necesarios para predicción y anomalías,
        evitando transferir datos innecesarios. Solo gastos (tipo='gasto').
        """
        sql = """
            SELECT
                m.id_movimiento,
                m.fecha,
                m.monto,
                m.id_categoria,
                m.descripcion
            FROM ingresos_gastos m
            WHERE m.id_usuario = %s
              AND m.tipo = 'gasto'
            ORDER BY m.fecha ASC
        """
        with get_db_cursor(self._connection) as cursor:
            cursor.execute(sql, (id_usuario,))
            return cursor.fetchall()

    def get_categoria_mas_costosa_periodo(
        self, id_usuario: int, inicio: date, fin_exclusivo: date
    ) -> Optional[str]:
        """
        Devuelve el nombre de la categoría con mayor gasto dentro de un periodo.
        Si no hay gastos en el periodo, devuelve None.
        """
        sql = """
            SELECT c.nombre
            FROM ingresos_gastos m
            INNER JOIN categorias c ON m.id_categoria = c.id_categoria
            WHERE m.id_usuario = %s
              AND m.tipo = 'gasto'
              AND m.fecha >= %s
              AND m.fecha < %s
            GROUP BY c.id_categoria, c.nombre
            ORDER BY SUM(m.monto) DESC, c.nombre ASC
            LIMIT 1
        """
        with get_db_cursor(self._connection) as cursor:
            cursor.execute(sql, (id_usuario, inicio, fin_exclusivo))
            row = cursor.fetchone()
            return row["nombre"] if row else None

    def get_categoria_mas_costosa_historico(self, id_usuario: int) -> Optional[str]:
        """
        Devuelve el nombre de la categoría con mayor gasto en todo el histórico del usuario.
        Si no hay gastos, devuelve None.
        """
        sql = """
            SELECT c.nombre
            FROM ingresos_gastos m
            INNER JOIN categorias c ON m.id_categoria = c.id_categoria
            WHERE m.id_usuario = %s
              AND m.tipo = 'gasto'
            GROUP BY c.id_categoria, c.nombre
            ORDER BY SUM(m.monto) DESC, c.nombre ASC
            LIMIT 1
        """
        with get_db_cursor(self._connection) as cursor:
            cursor.execute(sql, (id_usuario,))
            row = cursor.fetchone()
            return row["nombre"] if row else None


