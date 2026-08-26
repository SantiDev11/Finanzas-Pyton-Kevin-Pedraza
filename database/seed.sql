-- =============================================================================
-- Proyecto : Aplicación Web de Finanzas Personales
-- Archivo  : database/seed.sql
-- Fase     : 2 — Datos de prueba
-- Requiere : database/schema.sql ejecutado previamente.
-- Uso      : mysql -u <usuario> -p < database/seed.sql
--
-- El script es idempotente: vacía las tablas antes de insertar, por lo que
-- puede reejecutarse sin duplicar filas.
--
-- Los identificadores son explícitos para que las relaciones sean legibles y
-- para que las consultas de validación devuelvan siempre el mismo resultado.
-- =============================================================================

SET NAMES utf8mb4;

USE finanzas_personales;


-- -----------------------------------------------------------------------------
-- Limpieza (orden inverso al de dependencias)
-- -----------------------------------------------------------------------------

DELETE FROM ingresos_gastos;
DELETE FROM categorias;
DELETE FROM usuarios;

ALTER TABLE ingresos_gastos AUTO_INCREMENT = 1;
ALTER TABLE categorias      AUTO_INCREMENT = 1;
ALTER TABLE usuarios        AUTO_INCREMENT = 1;


-- =============================================================================
-- 1. USUARIOS
-- =============================================================================
-- ATENCIÓN: los valores de contrasena_hash son cadenas FICTICIAS con el
-- formato de bcrypt. No corresponden a ninguna contraseña real y no deben
-- usarse fuera de este juego de datos. El backend generará los hashes
-- auténticos en una fase posterior.
--
-- Los nombres incluyen tildes y eñes a propósito, para comprobar que el
-- almacenamiento en utf8mb4 es correcto de extremo a extremo.

INSERT INTO usuarios (id_usuario, nombre, correo, contrasena_hash, fecha_registro) VALUES
    (1, 'Ana María Rodríguez', 'ana.rodriguez@example.com',
        '$2b$12$SemillaDePruebaNoEsUnHashRealAnaMariaRodriguez0000001', '2025-08-28 09:14:00'),
    (2, 'José Antonio Muñoz',  'jose.munoz@example.com',
        '$2b$12$SemillaDePruebaNoEsUnHashRealJoseAntonioMunoz00000002', '2026-02-19 18:42:00'),
    (3, 'Lucía Fernández Ávila', 'lucia.fernandez@example.com',
        '$2b$12$SemillaDePruebaNoEsUnHashRealLuciaFernandezAvila000003', '2026-08-05 11:07:00');


-- =============================================================================
-- 2. CATEGORÍAS
-- =============================================================================
-- Cada categoría pertenece a un único usuario. Los nombres pueden repetirse
-- entre usuarios distintos, pero no dentro del mismo usuario y tipo.

INSERT INTO categorias (id_categoria, nombre, tipo, id_usuario) VALUES
    -- Usuario 1 — Ana María Rodríguez
    ( 1, 'Salario',        'ingreso', 1),
    ( 2, 'Freelance',      'ingreso', 1),
    ( 3, 'Vivienda',       'gasto',   1),
    ( 4, 'Alimentación',   'gasto',   1),
    ( 5, 'Transporte',     'gasto',   1),
    ( 6, 'Servicios',      'gasto',   1),
    ( 7, 'Entretenimiento','gasto',   1),
    ( 8, 'Salud',          'gasto',   1),
    -- Usuario 2 — José Antonio Muñoz
    ( 9, 'Salario',        'ingreso', 2),
    (10, 'Ventas',         'ingreso', 2),
    (11, 'Alimentación',   'gasto',   2),
    (12, 'Transporte',     'gasto',   2),
    (13, 'Educación',      'gasto',   2),
    (14, 'Hogar',          'gasto',   2),
    -- Usuario 3 — Lucía Fernández Ávila (alta reciente, historial mínimo)
    (15, 'Salario',        'ingreso', 3),
    (16, 'Alimentación',   'gasto',   3);


-- =============================================================================
-- 3. MOVIMIENTOS (ingresos y gastos)
-- =============================================================================
-- `tipo` se rellena de forma coherente con el tipo de la categoría: la clave
-- foránea compuesta fk_movimientos_categoria rechazaría cualquier otra cosa.
--
-- `fecha_creacion` se deja a su valor por defecto (CURRENT_TIMESTAMP): es una
-- marca de auditoría de la inserción, distinta de la fecha contable.
--
-- Volumen y cobertura del juego de datos:
--   * Usuario 1: 12 meses consecutivos (2025-09 .. 2026-08). Serie larga y
--     regular, pensada para la regresión lineal y la tendencia mensual.
--   * Usuario 2:  6 meses (2026-03 .. 2026-08). Serie corta.
--   * Usuario 3:  1 mes. Caso límite: datos insuficientes para predecir.
--   * Incluye un gasto deliberadamente atípico (usuario 1, 2026-03) para
--     comprobar más adelante la detección de anomalías por Z-Score.

INSERT INTO ingresos_gastos (id_usuario, id_categoria, tipo, monto, fecha, descripcion) VALUES

    -- ============ Usuario 1 — Ana María Rodríguez ============
    -- Septiembre 2025
    (1,  3, 'gasto',      950.00, '2025-09-03', 'Alquiler del piso'),
    (1,  4, 'gasto',      233.87, '2025-09-06', 'Compra semanal del supermercado'),
    (1,  5, 'gasto',       65.08, '2025-09-09', 'Abono de transporte'),
    (1,  6, 'gasto',       92.60, '2025-09-12', 'Internet y móvil'),
    (1,  2, 'ingreso',    429.79, '2025-09-14', 'Diseño de landing page'),
    (1,  4, 'gasto',      190.66, '2025-09-19', 'Compra quincenal'),
    (1,  7, 'gasto',       30.37, '2025-09-22', 'Cine y cena'),
    (1,  1, 'ingreso',   2850.00, '2025-09-28', 'Nómina mensual'),
    -- Octubre 2025
    (1,  3, 'gasto',      950.00, '2025-10-03', 'Alquiler del piso'),
    (1,  4, 'gasto',      218.96, '2025-10-06', 'Compra semanal del supermercado'),
    (1,  5, 'gasto',       63.45, '2025-10-09', 'Abono de transporte'),
    (1,  6, 'gasto',       87.66, '2025-10-12', 'Internet y móvil'),
    (1,  8, 'gasto',       88.67, '2025-10-16', 'Consulta médica y farmacia'),
    (1,  4, 'gasto',      152.94, '2025-10-19', 'Compra quincenal'),
    (1,  7, 'gasto',       56.19, '2025-10-22', 'Cine y cena'),
    (1,  1, 'ingreso',   2868.00, '2025-10-28', 'Nómina mensual'),
    -- Noviembre 2025
    (1,  3, 'gasto',      950.00, '2025-11-03', 'Alquiler del piso'),
    (1,  4, 'gasto',      212.48, '2025-11-06', 'Compra semanal del supermercado'),
    (1,  5, 'gasto',       95.95, '2025-11-09', 'Bono de metro'),
    (1,  6, 'gasto',       89.02, '2025-11-12', 'Luz y agua'),
    (1,  2, 'ingreso',    638.41, '2025-11-16', 'Maquetación de boletín'),
    (1,  4, 'gasto',      157.96, '2025-11-19', 'Compra quincenal'),
    (1,  1, 'ingreso',   2886.00, '2025-11-28', 'Nómina mensual'),
    -- Diciembre 2025
    (1,  3, 'gasto',      950.00, '2025-12-03', 'Alquiler del piso'),
    (1,  4, 'gasto',      222.18, '2025-12-06', 'Compra semanal del supermercado'),
    (1,  5, 'gasto',      101.80, '2025-12-09', 'Bono de metro'),
    (1,  6, 'gasto',      100.82, '2025-12-12', 'Suministros del hogar'),
    (1,  2, 'ingreso',    530.76, '2025-12-17', 'Consultoría puntual'),
    (1,  4, 'gasto',      156.64, '2025-12-19', 'Compra quincenal'),
    (1,  7, 'gasto',       72.60, '2025-12-22', 'Suscripción de streaming'),
    (1,  1, 'ingreso',   2904.00, '2025-12-28', 'Nómina mensual'),
    -- Enero 2026
    (1,  3, 'gasto',      950.00, '2026-01-03', 'Alquiler del piso'),
    (1,  4, 'gasto',      198.90, '2026-01-06', 'Compra semanal del supermercado'),
    (1,  5, 'gasto',       82.09, '2026-01-09', 'Gasolina'),
    (1,  6, 'gasto',      105.39, '2026-01-12', 'Luz y agua'),
    (1,  4, 'gasto',      172.67, '2026-01-19', 'Compra quincenal'),
    (1,  7, 'gasto',       75.22, '2026-01-22', 'Suscripción de streaming'),
    (1,  1, 'ingreso',   2922.00, '2026-01-28', 'Nómina mensual'),
    -- Febrero 2026
    (1,  3, 'gasto',      950.00, '2026-02-03', 'Alquiler del piso'),
    (1,  4, 'gasto',      209.36, '2026-02-06', 'Compra semanal del supermercado'),
    (1,  5, 'gasto',       80.23, '2026-02-09', 'Gasolina'),
    (1,  6, 'gasto',       91.71, '2026-02-12', 'Internet y móvil'),
    (1,  2, 'ingreso',    410.60, '2026-02-14', 'Mantenimiento web mensual'),
    (1,  8, 'gasto',       73.65, '2026-02-16', 'Consulta médica y farmacia'),
    (1,  4, 'gasto',      176.73, '2026-02-19', 'Compra quincenal'),
    (1,  7, 'gasto',       84.82, '2026-02-22', 'Cine y cena'),
    (1,  1, 'ingreso',   2940.00, '2026-02-28', 'Nómina mensual'),
    -- Marzo 2026
    (1,  3, 'gasto',      950.00, '2026-03-03', 'Alquiler del piso'),
    (1,  4, 'gasto',      244.98, '2026-03-06', 'Compra semanal del supermercado'),
    (1,  5, 'gasto',       92.84, '2026-03-09', 'Bono de metro'),
    (1,  6, 'gasto',       87.18, '2026-03-12', 'Suministros del hogar'),
    (1,  2, 'ingreso',    384.93, '2026-03-15', 'Maquetación de boletín'),
    (1,  8, 'gasto',     4850.00, '2026-03-17', 'Cirugía dental de urgencia (gasto atípico)'),
    (1,  4, 'gasto',      196.85, '2026-03-19', 'Compra quincenal'),
    (1,  1, 'ingreso',   2958.00, '2026-03-28', 'Nómina mensual'),
    -- Abril 2026
    (1,  3, 'gasto',      950.00, '2026-04-03', 'Alquiler del piso'),
    (1,  4, 'gasto',      210.58, '2026-04-06', 'Compra semanal del supermercado'),
    (1,  5, 'gasto',       93.75, '2026-04-09', 'Abono de transporte'),
    (1,  6, 'gasto',       94.91, '2026-04-12', 'Suministros del hogar'),
    (1,  4, 'gasto',      169.35, '2026-04-19', 'Compra quincenal'),
    (1,  7, 'gasto',       39.58, '2026-04-22', 'Libros'),
    (1,  1, 'ingreso',   3156.00, '2026-04-28', 'Nómina mensual'),
    -- Mayo 2026
    (1,  3, 'gasto',      950.00, '2026-05-03', 'Alquiler del piso'),
    (1,  4, 'gasto',      221.87, '2026-05-06', 'Compra semanal del supermercado'),
    (1,  5, 'gasto',       93.88, '2026-05-09', 'Abono de transporte'),
    (1,  6, 'gasto',      122.10, '2026-05-12', 'Internet y móvil'),
    (1,  2, 'ingreso',    429.99, '2026-05-17', 'Mantenimiento web mensual'),
    (1,  4, 'gasto',      202.92, '2026-05-19', 'Compra quincenal'),
    (1,  7, 'gasto',       65.09, '2026-05-22', 'Concierto'),
    (1,  1, 'ingreso',   3174.00, '2026-05-28', 'Nómina mensual'),
    -- Junio 2026
    (1,  3, 'gasto',      950.00, '2026-06-03', 'Alquiler del piso'),
    (1,  4, 'gasto',      241.41, '2026-06-06', 'Compra semanal del supermercado'),
    (1,  5, 'gasto',       65.96, '2026-06-09', 'Bono de metro'),
    (1,  6, 'gasto',       94.16, '2026-06-12', 'Internet y móvil'),
    (1,  8, 'gasto',       62.87, '2026-06-16', 'Consulta médica y farmacia'),
    (1,  2, 'ingreso',    481.37, '2026-06-18', 'Consultoría puntual'),
    (1,  4, 'gasto',      157.19, '2026-06-19', 'Compra quincenal'),
    (1,  7, 'gasto',       66.71, '2026-06-22', 'Cine y cena'),
    (1,  1, 'ingreso',   3192.00, '2026-06-28', 'Nómina mensual'),
    -- Julio 2026
    (1,  3, 'gasto',      950.00, '2026-07-03', 'Alquiler del piso'),
    (1,  4, 'gasto',      219.93, '2026-07-06', 'Compra semanal del supermercado'),
    (1,  5, 'gasto',       71.16, '2026-07-09', 'Abono de transporte'),
    (1,  6, 'gasto',      130.03, '2026-07-12', 'Internet y móvil'),
    (1,  4, 'gasto',      186.44, '2026-07-19', 'Compra quincenal'),
    (1,  1, 'ingreso',   3210.00, '2026-07-28', 'Nómina mensual'),
    -- Agosto 2026
    (1,  3, 'gasto',      950.00, '2026-08-03', 'Alquiler del piso'),
    (1,  4, 'gasto',      203.91, '2026-08-06', 'Compra semanal del supermercado'),
    (1,  5, 'gasto',       84.84, '2026-08-09', 'Gasolina'),
    (1,  6, 'gasto',       86.83, '2026-08-12', 'Internet y móvil'),
    (1,  2, 'ingreso',    521.87, '2026-08-15', 'Diseño de landing page'),
    (1,  4, 'gasto',      200.89, '2026-08-19', 'Compra quincenal'),
    (1,  7, 'gasto',       32.22, '2026-08-22', 'Concierto'),
    (1,  1, 'ingreso',   3228.00, '2026-08-28', 'Nómina mensual'),

    -- ============ Usuario 2 — José Antonio Muñoz ============
    -- Marzo 2026
    (2, 11, 'gasto',      237.24, '2026-03-05', 'Compra del mes'),
    (2, 12, 'gasto',       45.02, '2026-03-08', 'Gasolina'),
    (2, 10, 'ingreso',    499.70, '2026-03-11', 'Encargo particular'),
    (2, 13, 'gasto',      172.66, '2026-03-14', 'Curso de formación online'),
    (2, 14, 'gasto',       71.22, '2026-03-21', 'Menaje del hogar'),
    (2,  9, 'ingreso',   2100.00, '2026-03-30', 'Nómina mensual'),
    -- Abril 2026
    (2, 11, 'gasto',      285.37, '2026-04-05', 'Compra del mes'),
    (2, 12, 'gasto',       56.53, '2026-04-08', 'Gasolina'),
    (2, 13, 'gasto',      152.12, '2026-04-14', 'Curso de formación online'),
    (2, 14, 'gasto',      162.16, '2026-04-21', 'Menaje del hogar'),
    (2,  9, 'ingreso',   2112.00, '2026-04-30', 'Nómina mensual'),
    -- Mayo 2026
    (2, 11, 'gasto',      232.14, '2026-05-05', 'Compra del mes'),
    (2, 12, 'gasto',       65.67, '2026-05-08', 'Gasolina'),
    (2, 10, 'ingreso',    650.47, '2026-05-11', 'Encargo particular'),
    (2, 13, 'gasto',      126.08, '2026-05-14', 'Curso de formación online'),
    (2,  9, 'ingreso',   2124.00, '2026-05-30', 'Nómina mensual'),
    -- Junio 2026
    (2, 11, 'gasto',      245.85, '2026-06-05', 'Compra del mes'),
    (2, 12, 'gasto',       46.04, '2026-06-08', 'Gasolina'),
    (2, 13, 'gasto',      146.02, '2026-06-14', 'Curso de formación online'),
    (2, 14, 'gasto',      137.13, '2026-06-21', 'Menaje del hogar'),
    (2,  9, 'ingreso',   2136.00, '2026-06-30', 'Nómina mensual'),
    -- Julio 2026
    (2, 11, 'gasto',      210.95, '2026-07-05', 'Compra del mes'),
    (2, 12, 'gasto',       57.63, '2026-07-08', 'Gasolina'),
    (2, 10, 'ingreso',    431.14, '2026-07-11', 'Encargo particular'),
    (2, 13, 'gasto',      149.81, '2026-07-14', 'Curso de formación online'),
    (2, 14, 'gasto',      194.11, '2026-07-21', 'Menaje del hogar'),
    (2,  9, 'ingreso',   2148.00, '2026-07-30', 'Nómina mensual'),
    -- Agosto 2026
    (2, 11, 'gasto',      236.02, '2026-08-05', 'Compra del mes'),
    (2, 12, 'gasto',       79.32, '2026-08-08', 'Gasolina'),
    (2, 13, 'gasto',      132.80, '2026-08-14', 'Curso de formación online'),
    (2,  9, 'ingreso',   2160.00, '2026-08-30', 'Nómina mensual'),

    -- ============ Usuario 3 — Lucía Fernández Ávila ============
    -- Agosto 2026
    (3, 15, 'ingreso',   1750.00, '2026-08-05', 'Nómina mensual'),
    (3, 16, 'gasto',      132.40, '2026-08-09', 'Compra del supermercado'),
    (3, 16, 'gasto',       96.75, '2026-08-21', 'Compra quincenal');

