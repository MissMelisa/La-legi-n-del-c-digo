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

-- =========================================================
-- Renombrar columnas de archivo productos
-- =========================================================

import pandas as pd
from pathlib import Path


dataset_path = Path("dataset")
output_path = dataset_path / "outputs"

column_mappings = {
    "productos.csv": {
        "id": "id",
        "marca": "marca",
        "nombre": "nombre",
        "presentacion": "presentacion",
        "categoria1": "categoria_1",
        "categoria2": "categoria_2",
        "categoria3": "categoria_3",
    },
    "outputs/precios.csv": {
        "precio": "precio",
        "producto_id": "producto_id",
        "sucursal_id": "sucursal_id",
    },
    "outputs/sucursales_cordoba.csv": {
        "id": "id",
        "comercioid": "comercio_id",
        "banderaid": "bandera_id",
        "banderadescripcion": "bandera_descripcion",
        "comerciorazonsocial": "comercio_razon_social",
        "provincia": "provincia",
        "localidad": "localidad",
        "direccion": "direccion",
        "lat": "lat",
        "lng": "lng",
        "sucursalnombre": "sucursal_nombre",
        "sucursaltipo": "sucursal_tipo",
    },
}

for file_name, mapping in column_mappings.items():
    file_path = dataset_path / file_name

    df = pd.read_csv(file_path, encoding="utf-8")

    df.rename(columns=mapping, inplace=True)

    df.to_csv(
        file_path,
        index=False,
        encoding="utf-8",
    )

    print(f"{file_name}:")
    print(df.columns.tolist())
    print()


-- =========================================================
-- Scripts de limpieza y filtrado 
-- =========================================================


import pandas as pd
from pathlib import Path

dataset_path = Path("dataset")

archivo_original = dataset_path / "sucursales.csv"

# Leer sucursales
df = pd.read_csv(archivo_original, encoding="utf-8")

# Limpiar nombres de columnas
df.columns = df.columns.str.strip().str.lower()

# Ver qué provincias hay
print("Provincias encontradas:")
print(df["provincia"].value_counts(dropna=False))

# Conservar solamente Córdoba
df_cordoba = df[
    df["provincia"].astype(str).str.strip() == "AR-X"
]

# Guardar sucursales de Córdoba
df_cordoba.to_csv(
    dataset_path / "outputs/sucursales_cordoba.csv",
    index=False,
    encoding="utf-8"
)

print(f"\nRegistros originales: {len(df)}")
print(f"Registros de Córdoba: {len(df_cordoba)}")


# --------------------------------------------------
# UNIR ARCHIVOS DE PRECIOS
# --------------------------------------------------

archivos_precios = list(dataset_path.glob("precios_*.csv"))

df_precios = pd.concat(
    [
        pd.read_csv(archivo, encoding="utf-8")
        for archivo in archivos_precios
    ],
    ignore_index=True
)

print(f"\nArchivos de precios unidos: {len(archivos_precios)}")
print(f"Registros totales de precios: {len(df_precios)}")


# --------------------------------------------------
# FILTRAR PRECIOS DE SUCURSALES DE CÓRDOBA
# --------------------------------------------------

# Limpiar nombres de columnas
df_precios.columns = df_precios.columns.str.strip().str.lower()

# Asegurar que los IDs tengan el mismo tipo
df_cordoba["id"] = df_cordoba["id"].astype(str).str.strip()
df_precios["sucursal_id"] = (
    df_precios["sucursal_id"].astype(str).str.strip()
)

# Obtener unicamente los precios cuyas sucursales
# pertenecen a Córdoba
df_precios_cordoba = df_precios[
    df_precios["sucursal_id"].isin(df_cordoba["id"])
]

# Guardar precios de Cordoba
df_precios_cordoba.to_csv(
    dataset_path / "outputs/precios_cordoba.csv",
    index=False,
    encoding="utf-8"
)

print(f"Precios originales: {len(df_precios)}")
print(f"Precios de Cordoba: {len(df_precios_cordoba)}")
print(
    f"Precios eliminados por no pertenecer a Cordoba: "
    f"{len(df_precios) - len(df_precios_cordoba)}"
)

-- =========================================================
-- CARGA FINAL DE LA BASE DE DATOS
-- =========================================================

LOAD DATA LOCAL INFILE 'dataset/outputs/precios_cordoba.csv'
INTO TABLE precios
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE 'dataset/outputs/sucursales_cordoba.csv'
INTO TABLE precios
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE 'dataset/productos.csv'
INTO TABLE precios
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS;


-- =========================================================
-- SCRIPTS PARA CREAR CAMPOS CALCULADOS
-- =========================================================

-- Creacion de campo diferencia de precios: diferencia_precios e insercion en DB

ALTER TABLE productos ADD COLUMN diferencia_precios DECIMAL(12,2);

UPDATE productos p 
JOIN (
    SELECT producto_id, MAX(precio) - MIN(precio) as diferencia_precios
    FROM precios
    GROUP BY producto_id
) pr ON p.id = pr.producto_id
SET p.diferencia_precios = pr.diferencia_precios;

-- Creacion de campo variacion porcentual: variacion_porcentual e insercion en DB

ALTER TABLE productos ADD COLUMN variacion_porcentual DECIMAL(12,2);

UPDATE productos p 
JOIN (
    SELECT producto_id, ((MAX(precio) - MIN(precio)) / MIN(precio)) * 100 as variacion_porcentual
    FROM precios
    GROUP BY producto_id
) pr ON p.id = pr.producto_id
SET p.variacion_porcentual = pr.variacion_porcentual;