-- =========================================================
-- BASE DE DATOS: datos_comercios
-- Proyecto: La Legión del Código
-- =========================================================

-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS datos_comercios
CHARACTER SET utf8mb4
COLLATE utf8mb4_0900_ai_ci;

USE datos_comercios;


-- =========================================================
-- TABLA: productos
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
-- TABLA: sucursales
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
-- TABLA: precios
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
-- VERIFICACIÓN
-- =========================================================

SHOW TABLES;