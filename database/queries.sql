-- =============================================================================
-- Proyecto : Aplicación Web de Finanzas Personales
-- Archivo  : database/queries.sql
-- Fase     : 2 — Consultas de validación
-- Requiere : database/schema.sql y database/seed.sql ejecutados previamente.
-- Uso      : mysql -u <usuario> -p < database/queries.sql
--
-- Consultas de comprobación del modelo. Sirven además como referencia del SQL
-- que la capa de repositorios utilizará en fases posteriores; aquí llevan
-- valores literales, pero en la aplicación irán siempre parametrizadas (?)
-- para evitar inyección SQL.
-- =============================================================================

SET NAMES utf8mb4;

USE finanzas_personales;


-- -----------------------------------------------------------------------------
-- 1. Total de ingresos por usuario
-- -----------------------------------------------------------------------------
-- LEFT JOIN para que un usuario sin movimientos aparezca con total 0 en lugar
-- de desaparecer del resultado.

SELECT
    u.id_usuario,
    u.nombre,
    COALESCE(SUM(m.monto), 0) AS total_ingresos
FROM usuarios u
LEFT JOIN ingresos_gastos m
       ON m.id_usuario = u.id_usuario
      AND m.tipo = 'ingreso'
GROUP BY u.id_usuario, u.nombre
ORDER BY u.id_usuario;


-- -----------------------------------------------------------------------------
-- 2. Total de gastos por usuario
-- -----------------------------------------------------------------------------

SELECT
    u.id_usuario,
    u.nombre,
    COALESCE(SUM(m.monto), 0) AS total_gastos
FROM usuarios u
LEFT JOIN ingresos_gastos m
       ON m.id_usuario = u.id_usuario
      AND m.tipo = 'gasto'
GROUP BY u.id_usuario, u.nombre
ORDER BY u.id_usuario;


-- -----------------------------------------------------------------------------
-- 3. Balance por usuario (ingresos - gastos)
-- -----------------------------------------------------------------------------
-- Un solo recorrido de la tabla: se separan ingresos y gastos con SUM
-- condicional en lugar de unir dos subconsultas agregadas.

SELECT
    u.id_usuario,
    u.nombre,
    COALESCE(SUM(CASE WHEN m.tipo = 'ingreso' THEN m.monto END), 0) AS total_ingresos,
    COALESCE(SUM(CASE WHEN m.tipo = 'gasto'   THEN m.monto END), 0) AS total_gastos,
    COALESCE(SUM(CASE WHEN m.tipo = 'ingreso' THEN m.monto
                      ELSE -m.monto END), 0)                        AS balance
FROM usuarios u
LEFT JOIN ingresos_gastos m
       ON m.id_usuario = u.id_usuario
GROUP BY u.id_usuario, u.nombre
ORDER BY u.id_usuario;


-- -----------------------------------------------------------------------------
-- 4. Gastos agrupados por categoría (usuario 1)
-- -----------------------------------------------------------------------------
-- El nombre de la categoría se obtiene por JOIN, nunca duplicándolo en
-- ingresos_gastos: es exactamente lo que exige la 3FN.

SELECT
    c.id_categoria,
    c.nombre                      AS categoria,
    COUNT(*)                      AS num_movimientos,
    SUM(m.monto)                  AS total_gastado,
    ROUND(AVG(m.monto), 2)        AS gasto_medio
FROM ingresos_gastos m
INNER JOIN categorias c
        ON c.id_categoria = m.id_categoria
WHERE m.id_usuario = 1
  AND m.tipo = 'gasto'
GROUP BY c.id_categoria, c.nombre
ORDER BY total_gastado DESC;


-- -----------------------------------------------------------------------------
-- 5. Gastos agrupados por mes (usuario 1) — base de la tendencia mensual
-- -----------------------------------------------------------------------------
-- Serie temporal que alimentará la regresión lineal en una fase posterior.

SELECT
    DATE_FORMAT(m.fecha, '%Y-%m') AS mes,
    COUNT(*)                      AS num_movimientos,
    SUM(m.monto)                  AS total_gastos
FROM ingresos_gastos m
WHERE m.id_usuario = 1
  AND m.tipo = 'gasto'
GROUP BY mes
ORDER BY mes;


-- -----------------------------------------------------------------------------
-- 6. Movimientos filtrados por rango de fechas (usuario 1, primer trimestre 2026)
-- -----------------------------------------------------------------------------
-- Rango cerrado por ambos extremos sobre una columna DATE. La condición deja
-- `fecha` sin envolver en ninguna función, de modo que idx_mov_usuario_fecha
-- puede resolver el filtro por índice.

SELECT
    m.id_movimiento,
    m.fecha,
    m.tipo,
    c.nombre       AS categoria,
    m.monto,
    m.descripcion
FROM ingresos_gastos m
INNER JOIN categorias c
        ON c.id_categoria = m.id_categoria
WHERE m.id_usuario = 1
  AND m.fecha BETWEEN '2026-01-01' AND '2026-03-31'
ORDER BY m.fecha, m.id_movimiento;


-- -----------------------------------------------------------------------------
-- 7. Comprobación del dato atípico (base del futuro Z-Score)
-- -----------------------------------------------------------------------------
-- No implementa el algoritmo — eso corresponde a una fase posterior — solo
-- verifica que el juego de datos contiene una anomalía lo bastante marcada.
-- Z = (monto - media) / desviación típica, sobre los gastos del usuario.

SELECT
    m.id_movimiento,
    m.fecha,
    c.nombre     AS categoria,
    m.monto,
    m.descripcion,
    ROUND((m.monto - e.media) / e.desviacion, 2) AS z_score
FROM ingresos_gastos m
INNER JOIN categorias c
        ON c.id_categoria = m.id_categoria
CROSS JOIN (
    SELECT AVG(monto) AS media, STDDEV_SAMP(monto) AS desviacion
    FROM ingresos_gastos
    WHERE id_usuario = 1
      AND tipo = 'gasto'
) AS e
WHERE m.id_usuario = 1
  AND m.tipo = 'gasto'
  AND ABS((m.monto - e.media) / e.desviacion) > 3
ORDER BY z_score DESC;
