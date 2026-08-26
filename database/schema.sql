-- =============================================================================
-- Proyecto : Aplicación Web de Finanzas Personales
-- Archivo  : database/schema.sql
-- Fase     : 2 — Diseño e implementación de la base de datos
-- Motor    : MySQL 8.0 o superior (InnoDB)
-- Objetivo : Crear desde cero la estructura relacional normalizada a 3FN.
-- Uso      : mysql -u <usuario> -p < database/schema.sql
--
-- El script es idempotente: puede ejecutarse varias veces sobre la misma
-- instancia. Elimina y vuelve a crear las tablas, por lo que descarta los
-- datos existentes.
-- =============================================================================

SET NAMES utf8mb4;


-- =============================================================================
-- 1. CREACIÓN DE LA BASE DE DATOS
-- =============================================================================
-- utf8mb4 es el único juego de caracteres de MySQL que cubre Unicode completo,
-- necesario para almacenar tildes y eñes (á, é, í, ó, ú, ñ) sin pérdida.
-- La intercalación por defecto (ai_ci) es insensible a mayúsculas y a acentos,
-- lo que evita categorías duplicadas del tipo "Alimentación" / "alimentacion".

CREATE DATABASE IF NOT EXISTS finanzas_personales
    CHARACTER SET utf8mb4
    COLLATE       utf8mb4_0900_ai_ci;


-- =============================================================================
-- 2. SELECCIÓN DE LA BASE DE DATOS
-- =============================================================================

USE finanzas_personales;


-- =============================================================================
-- 3. LIMPIEZA PREVIA
-- =============================================================================
-- Orden inverso al de dependencias: primero la tabla hija, después las padre.

DROP TABLE IF EXISTS ingresos_gastos;
DROP TABLE IF EXISTS categorias;
DROP TABLE IF EXISTS usuarios;


-- =============================================================================
-- 4. CREACIÓN DE TABLAS Y RESTRICCIONES
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 4.1 usuarios - entidad raíz del modelo
-- -----------------------------------------------------------------------------
CREATE TABLE usuarios (
    id_usuario      INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    nombre          VARCHAR(100)  NOT NULL,
    -- El correo se compara sin distinguir mayúsculas pero SÍ distinguiendo
    -- acentos (as_ci), que es la semántica correcta para una dirección de
    -- correo electrónico.
    correo          VARCHAR(150)  CHARACTER SET utf8mb4
                                  COLLATE utf8mb4_0900_as_ci NOT NULL,
    -- Longitud holgada para no atarse a un algoritmo concreto: bcrypt ocupa
    -- 60 caracteres, argon2id supera los 90. Nunca almacena texto plano.
    contrasena_hash VARCHAR(255)  NOT NULL,
    fecha_registro  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id_usuario),

    CONSTRAINT uq_usuarios_correo  UNIQUE (correo),
    CONSTRAINT chk_usuarios_nombre CHECK (CHAR_LENGTH(TRIM(nombre)) >= 2),
    CONSTRAINT chk_usuarios_correo CHECK (correo LIKE '_%@_%._%')
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE         = utf8mb4_0900_ai_ci
  COMMENT         = 'Usuarios registrados en la aplicación';


-- -----------------------------------------------------------------------------
-- 4.2 categorias - clasificación de movimientos, privada de cada usuario
-- -----------------------------------------------------------------------------
CREATE TABLE categorias (
    id_categoria INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nombre       VARCHAR(60)  NOT NULL,
    tipo         ENUM('ingreso', 'gasto') NOT NULL,
    id_usuario   INT UNSIGNED NOT NULL,

    PRIMARY KEY (id_categoria),

    -- Un usuario no puede repetir el nombre de una categoría dentro del mismo
    -- tipo, pero sí puede tener "Otros" como ingreso y como gasto.
    -- Este índice sirve además de soporte a fk_categorias_usuario.
    CONSTRAINT uq_categorias_usuario_tipo_nombre
        UNIQUE (id_usuario, tipo, nombre),

    -- Clave candidata referenciada por la clave foránea compuesta de
    -- ingresos_gastos. Es trivialmente única porque contiene la clave primaria.
    CONSTRAINT uq_categorias_referencia
        UNIQUE (id_usuario, id_categoria, tipo),

    CONSTRAINT chk_categorias_nombre CHECK (CHAR_LENGTH(TRIM(nombre)) >= 2),

    -- ON DELETE RESTRICT: eliminar un usuario que todavía conserva categorías
    -- queda bloqueado. La baja de una cuenta es una operación deliberada que la
    -- aplicación ejecuta en una transacción ordenada (véase la nota de la
    -- sección 6). Un CASCADE aquí entraría en conflicto irresoluble con el
    -- RESTRICT de fk_movimientos_categoria.
    CONSTRAINT fk_categorias_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuarios (id_usuario)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE         = utf8mb4_0900_ai_ci
  COMMENT         = 'Categorías de ingreso o gasto pertenecientes a un usuario';


-- -----------------------------------------------------------------------------
-- 4.3 ingresos_gastos - libro de movimientos financieros
-- -----------------------------------------------------------------------------
CREATE TABLE ingresos_gastos (
    id_movimiento  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    id_usuario     INT UNSIGNED    NOT NULL,
    id_categoria   INT UNSIGNED    NOT NULL,
    tipo           ENUM('ingreso', 'gasto') NOT NULL,
    -- DECIMAL almacena el importe en base 10 con precisión exacta. FLOAT o
    -- DOUBLE son binarios y arrastran error de redondeo, inaceptable en dinero.
    monto          DECIMAL(12, 2)  NOT NULL,
    -- fecha = fecha contable del movimiento (la introduce el usuario).
    fecha          DATE            NOT NULL,
    descripcion    VARCHAR(255)    NULL,
    -- fecha_creacion = marca de auditoría de cuándo se registró la fila.
    fecha_creacion DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id_movimiento),

    -- Índice de soporte de fk_movimientos_categoria. Se declara aquí, y no en
    -- la sección 5, porque InnoDB exige que exista en el momento de crear la
    -- clave foránea; si no se declara, el motor genera uno anónimo duplicado.
    -- Su prefijo (id_usuario) da también soporte a fk_movimientos_usuario.
    KEY idx_mov_usuario_categoria_tipo (id_usuario, id_categoria, tipo),

    CONSTRAINT chk_mov_monto CHECK (monto > 0),
    CONSTRAINT chk_mov_fecha CHECK (fecha >= '2000-01-01'),

    CONSTRAINT fk_movimientos_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuarios (id_usuario)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    -- Clave foránea compuesta hacia categorias. Al incluir id_usuario y tipo
    -- garantiza, a nivel de motor, dos invariantes que una clave foránea
    -- simple sobre id_categoria no podría cubrir:
    --   1) la categoría del movimiento pertenece al mismo usuario;
    --   2) el tipo del movimiento coincide con el tipo de su categoría.
    -- RESTRICT impide borrar una categoría que aún tenga movimientos.
    CONSTRAINT fk_movimientos_categoria
        FOREIGN KEY (id_usuario, id_categoria, tipo)
        REFERENCES categorias (id_usuario, id_categoria, tipo)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE         = utf8mb4_0900_ai_ci
  COMMENT         = 'Movimientos de ingreso y gasto registrados por los usuarios';


-- =============================================================================
-- 5. ÍNDICES
-- =============================================================================

-- Consulta dominante de la aplicación: los movimientos de UN usuario dentro de
-- un rango de fechas (balance, tendencia mensual, listados paginados). El
-- prefijo id_usuario acota el usuario y el sufijo fecha resuelve el rango
-- devolviendo las filas ya ordenadas, lo que evita un ordenamiento posterior.
CREATE INDEX idx_mov_usuario_fecha
    ON ingresos_gastos (id_usuario, fecha);

-- Soporta la agrupación de gastos por categoría y, sobre todo, la comprobación
-- de integridad referencial al eliminar o modificar una categoría: sin él,
-- cada DELETE sobre categorias exigiría recorrer la tabla de movimientos.
CREATE INDEX idx_mov_categoria
    ON ingresos_gastos (id_categoria);


-- =============================================================================
-- 6. NOTA SOBRE LA POLÍTICA DE BORRADO
-- =============================================================================
-- Las tres claves foráneas usan ON DELETE RESTRICT. Es una decisión deliberada:
-- ningún borrado destruye información financiera de forma implícita.
--
-- La combinación "intuitiva" —CASCADE desde usuarios y RESTRICT desde
-- categorias— es inviable en InnoDB: al borrar un usuario, el motor propaga el
-- CASCADE hacia categorias y, al eliminar cada categoría, dispara el RESTRICT
-- de sus movimientos, abortando la operación con el error 1451. El borrado de
-- un usuario quedaría permanentemente bloqueado de forma no evidente.
--
-- Con RESTRICT uniforme el comportamiento es explícito y predecible:
--   * borrar una categoría con movimientos  -> error 1451 (historial protegido);
--   * borrar un usuario con datos           -> error 1451.
--
-- La baja de una cuenta la ejecuta la aplicación como transacción ordenada:
--
--   START TRANSACTION;
--     DELETE FROM ingresos_gastos WHERE id_usuario = ?;
--     DELETE FROM categorias      WHERE id_usuario = ?;
--     DELETE FROM usuarios        WHERE id_usuario = ?;
--   COMMIT;
--
-- ON UPDATE CASCADE sí es funcional: las claves primarias son subrogadas y no
-- cambian nunca, pero la columna `tipo` forma parte de fk_movimientos_categoria
-- y sí puede cambiar. Si un usuario reclasifica una categoría de gasto a
-- ingreso, el motor propaga el nuevo tipo a todos sus movimientos y el modelo
-- permanece coherente sin intervención de la aplicación.
