-- =========================================================
-- FULLSCRIPT: crea la base, carga los CSV y agrega las columnas
-- calculadas. Todo en un solo script SQL, sin Python.
-- Proyecto: La Legión del Código
-- =========================================================
--
-- Antes de correr esto:
--   1. Generar los CSV de dataset/outputs/ corriendo, en orden:
--        python scripts/clean-up.py
--        python scripts/populate-categories.py
--      (esto deja listos productos_categorizados.csv,
--      sucursales_cordoba.csv y precios_cordoba.csv)
--   2. Correr este script desde la raíz del proyecto, porque las
--      rutas de LOAD DATA son relativas a esa carpeta:
--        mysql --local-infile=1 -u root < sql/fullscript.sql
--      (el servidor necesita local_infile=ON, que es lo normal
--      en una instalación default de MySQL)
--
-- Es idempotente: se puede volver a correr las veces que haga
-- falta, vacía las tablas antes de cargar de nuevo.


-- =========================================================
-- BASE DE DATOS Y TABLAS
-- =========================================================

CREATE DATABASE IF NOT EXISTS datos_comercios
CHARACTER SET utf8mb4
COLLATE utf8mb4_0900_ai_ci;

USE datos_comercios;

CREATE TABLE IF NOT EXISTS productos (
    id VARCHAR(50) NOT NULL,
    marca VARCHAR(150),
    nombre VARCHAR(255),
    presentacion VARCHAR(100),
    categoria_1 VARCHAR(150),
    categoria_2 VARCHAR(150),
    categoria_3 VARCHAR(150),

    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS sucursales (
    id VARCHAR(50) NOT NULL,
    comercio_id BIGINT,
    bandera_id BIGINT,
    bandera_descripcion VARCHAR(255),
    comercio_razon_social VARCHAR(255),
    provincia VARCHAR(10),
    localidad VARCHAR(255),
    direccion VARCHAR(500),
    lat DECIMAL(10,7),
    lng DECIMAL(10,7),
    sucursal_nombre VARCHAR(255),
    sucursal_tipo VARCHAR(100),

    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS precios (
    precio DECIMAL(12,2),
    producto_id VARCHAR(50),
    sucursal_id VARCHAR(50),

    INDEX idx_precios_producto (producto_id),
    INDEX idx_precios_sucursal (sucursal_id),

    CONSTRAINT fk_precios_producto
        FOREIGN KEY (producto_id)
        REFERENCES productos(id),

    CONSTRAINT fk_precios_sucursal
        FOREIGN KEY (sucursal_id)
        REFERENCES sucursales(id)
);

-- Si ya habíamos cargado datos antes, los vaciamos para que el
-- script se pueda correr de nuevo sin chocar con la PRIMARY KEY.
-- Se desactivan las foreign keys nada más que para poder truncar
-- en cualquier orden.

SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE precios;
TRUNCATE TABLE sucursales;
TRUNCATE TABLE productos;
SET FOREIGN_KEY_CHECKS = 1;


-- =========================================================
-- CARGA DE LOS CSV
-- =========================================================
--
-- Los CSV los genera pandas (LF, sin \r), y solo va entre
-- comillas el campo que las necesita, por eso OPTIONALLY
-- ENCLOSED BY en vez de ENCLOSED BY a secas.
--
-- productos primero y sucursales después porque precios tiene
-- foreign key a las dos.

LOAD DATA LOCAL INFILE 'dataset/outputs/productos_categorizados.csv'
INTO TABLE productos
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, marca, nombre, presentacion, categoria_1, categoria_2, categoria_3, @categoria_origen);

-- sucursales_cordoba.csv todavía trae los nombres de columna
-- "crudos" (comercioid, banderaid, etc.), pero el orden coincide
-- con las columnas de la tabla, así que alcanza con listarlas acá.

LOAD DATA LOCAL INFILE 'dataset/outputs/sucursales_cordoba.csv'
INTO TABLE sucursales
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, comercio_id, bandera_id, bandera_descripcion, comercio_razon_social,
 provincia, localidad, direccion, lat, lng, sucursal_nombre, sucursal_tipo);

LOAD DATA LOCAL INFILE 'dataset/outputs/precios_cordoba.csv'
INTO TABLE precios
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(precio, producto_id, sucursal_id);


-- =========================================================
-- COLUMNAS CALCULADAS
-- =========================================================

-- Diferencia entre el precio más caro y el más barato de cada
-- producto (entre todas las sucursales de Córdoba).

ALTER TABLE productos ADD COLUMN diferencia_precios DECIMAL(12,2);

UPDATE productos p
JOIN (
    SELECT producto_id, MAX(precio) - MIN(precio) AS diferencia_precios
    FROM precios
    GROUP BY producto_id
) pr ON p.id = pr.producto_id
SET p.diferencia_precios = pr.diferencia_precios;

-- Esa misma diferencia pero como porcentaje del precio más barato.
-- El NULLIF es para no reventar con división por cero si el precio
-- mínimo de algún producto quedó en 0.

ALTER TABLE productos ADD COLUMN variacion_porcentual DECIMAL(12,2);

UPDATE productos p
JOIN (
    SELECT
        producto_id,
        ((MAX(precio) - MIN(precio)) / NULLIF(MIN(precio), 0)) * 100
            AS variacion_porcentual
    FROM precios
    GROUP BY producto_id
) pr ON p.id = pr.producto_id
SET p.variacion_porcentual = pr.variacion_porcentual;


-- =========================================================
-- VERIFICACIÓN
-- =========================================================

SHOW TABLES;

SELECT
    (SELECT COUNT(*) FROM productos) AS productos,
    (SELECT COUNT(*) FROM sucursales) AS sucursales,
    (SELECT COUNT(*) FROM precios) AS precios;
