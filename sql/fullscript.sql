```sql
-- =========================================================
-- BASE DE DATOS: datos_comercios
-- Proyecto: La Legión del Código
-- FULL SCRIPT
-- =========================================================


-- =========================================================
-- 1. CREACIÓN DE LA BASE DE DATOS
-- =========================================================

CREATE DATABASE IF NOT EXISTS datos_comercios
CHARACTER SET utf8mb4
COLLATE utf8mb4_0900_ai_ci;

USE datos_comercios;


-- =========================================================
-- 2. TABLA: productos
-- =========================================================

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


-- =========================================================
-- 3. TABLA: sucursales
-- =========================================================

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


-- =========================================================
-- 4. TABLA: precios
-- =========================================================
--
-- No se agrega un ID propio.
-- Cada registro queda identificado por:
--
--   producto_id
--   sucursal_id
--
-- =========================================================

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


-- =========================================================
-- 5. VERIFICACIÓN DE ESTRUCTURA
-- =========================================================

SHOW TABLES;


-- =========================================================
-- 6. CARGA DE DATOS
-- =========================================================
--
-- La preparación y limpieza de los CSV se realiza mediante
-- los scripts Python del proyecto:
--
--   scripts/clean-up.py
--   scripts/load-to-mysql.py
--
-- El proceso Python:
--
--   1. Filtra las sucursales de Córdoba (AR-X).
--   2. Une los archivos precios_*.csv.
--   3. Filtra los precios correspondientes a Córdoba.
--   4. Normaliza las columnas.
--   5. Completa categorías mediante categorización heurística.
--   6. Carga los datos respetando las claves foráneas.
--
-- Archivos generados:
--
--   dataset/outputs/sucursales_cordoba.csv
--   dataset/outputs/precios_cordoba.csv
--
-- Los productos se toman de:
--
--   dataset/productos.csv
--
-- No se utiliza productos_limpios.csv para la carga final,
-- ya que dicho archivo elimina productos sin clasificación
-- y esos productos pueden estar referenciados por precios.
--
-- =========================================================


-- =========================================================
-- 7. VERIFICACIÓN DE CANTIDAD DE REGISTROS
-- =========================================================

SELECT
    'productos' AS tabla,
    COUNT(*) AS cantidad
FROM productos

UNION ALL

SELECT
    'sucursales' AS tabla,
    COUNT(*) AS cantidad
FROM sucursales

UNION ALL

SELECT
    'precios' AS tabla,
    COUNT(*) AS cantidad
FROM precios;


-- =========================================================
-- 8. VERIFICAR INTEGRIDAD: PRECIOS SIN PRODUCTO
-- =========================================================

SELECT
    COUNT(*) AS precios_sin_producto
FROM precios p
LEFT JOIN productos pr
    ON p.producto_id = pr.id
WHERE pr.id IS NULL;


-- =========================================================
-- 9. VERIFICAR INTEGRIDAD: PRECIOS SIN SUCURSAL
-- =========================================================

SELECT
    COUNT(*) AS precios_sin_sucursal
FROM precios p
LEFT JOIN sucursales s
    ON p.sucursal_id = s.id
WHERE s.id IS NULL;


-- =========================================================
-- 10. CAMPO CALCULADO: DIFERENCIA DE PRECIOS
-- =========================================================
--
-- Indica la diferencia entre el precio máximo y mínimo
-- de cada producto entre las sucursales.
--
-- Fórmula:
--
--   MAX(precio) - MIN(precio)
--
-- =========================================================

ALTER TABLE productos
ADD COLUMN IF NOT EXISTS diferencia_precios DECIMAL(12,2);


UPDATE productos p
LEFT JOIN (
    SELECT
        producto_id,
        MAX(precio) - MIN(precio) AS diferencia_precios
    FROM precios
    GROUP BY producto_id
) pr
    ON p.id = pr.producto_id
SET p.diferencia_precios = pr.diferencia_precios;


-- =========================================================
-- 11. CAMPO CALCULADO: VARIACIÓN PORCENTUAL
-- =========================================================
--
-- Indica cuánto representa la diferencia de precios
-- respecto del precio mínimo.
--
-- Fórmula:
--
--   ((MAX(precio) - MIN(precio)) / MIN(precio)) * 100
--
-- Si el precio mínimo es 0, se devuelve NULL para evitar
-- una división por cero.
--
-- =========================================================

ALTER TABLE productos
ADD COLUMN IF NOT EXISTS variacion_porcentual DECIMAL(12,2);


UPDATE productos p
LEFT JOIN (
    SELECT
        producto_id,
        CASE
            WHEN MIN(precio) > 0 THEN
                (
                    (MAX(precio) - MIN(precio))
                    / MIN(precio)
                ) * 100
            ELSE NULL
        END AS variacion_porcentual
    FROM precios
    GROUP BY producto_id
) pr
    ON p.id = pr.producto_id
SET p.variacion_porcentual = pr.variacion_porcentual;


-- =========================================================
-- 12. VERIFICACIÓN DE CAMPOS CALCULADOS
-- =========================================================

SELECT
    id,
    marca,
    nombre,
    presentacion,
    categoria_1,
    categoria_2,
    categoria_3,
    diferencia_precios,
    variacion_porcentual
FROM productos
ORDER BY variacion_porcentual DESC
LIMIT 20;


-- =========================================================
-- 13. PRODUCTOS CON MAYOR DIFERENCIA DE PRECIO
-- =========================================================

SELECT
    p.id AS producto_id,
    p.nombre AS producto,
    p.marca,
    p.diferencia_precios,
    p.variacion_porcentual
FROM productos p
WHERE p.diferencia_precios IS NOT NULL
ORDER BY p.diferencia_precios DESC
LIMIT 20;


-- =========================================================
-- 14. CONSULTA FINAL
-- =========================================================
--
-- Muestra información del producto junto con su precio,
-- sucursal y localidad.
--
-- =========================================================

SELECT
    p.id AS producto_id,
    p.nombre AS producto,
    p.marca,
    p.presentacion,
    p.categoria_1,
    p.categoria_2,
    p.categoria_3,
    pr.precio,
    s.id AS sucursal_id,
    s.sucursal_nombre,
    s.localidad,
    s.provincia
FROM precios pr
INNER JOIN productos p
    ON pr.producto_id = p.id
INNER JOIN sucursales s
    ON pr.sucursal_id = s.id
LIMIT 50;


-- =========================================================
-- 15. RESUMEN FINAL
-- =========================================================

SELECT
    COUNT(*) AS cantidad_productos
FROM productos;

SELECT
    COUNT(*) AS cantidad_sucursales
FROM sucursales;

SELECT
    COUNT(*) AS cantidad_precios
FROM precios;


-- =========================================================
-- FIN DEL FULL SCRIPT
-- =========================================================
```
