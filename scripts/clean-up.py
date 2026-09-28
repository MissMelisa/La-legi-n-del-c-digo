
import re

import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset"
OUTPUT_DIR = DATASET_DIR / "outputs"

# Crear carpeta outputs si no existe
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ==================================================
# DIAGNÓSTICO DE CALIDAD DE DATOS
# ==================================================
# Se corre sobre los datos crudos (antes de limpiar/filtrar) para
# dejar evidencia real de los problemas detectados: nulos, duplicados,
# tipos de datos, espacios y formatos inconsistentes.

def diagnostico_calidad(df, nombre):
    print(f"\n---- Diagnóstico de calidad: {nombre} ----")
    print(f"Filas: {len(df)} | Columnas: {list(df.columns)}")

    print("\nTipos de datos:")
    print(df.dtypes)

    nulos = df.isna().sum()
    nulos = nulos[nulos > 0]
    print("\nValores nulos por columna:")
    print(nulos if len(nulos) else "(sin valores nulos)")

    duplicados = df.duplicated().sum()
    print(f"\nRegistros duplicados (fila completa): {duplicados}")


def normalizar_texto(serie):
    """Recorta espacios al inicio/final y colapsa espacios internos
    repetidos (ej: 'Super   MAMI ' -> 'Super MAMI')."""
    return (
        serie.astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )


# ==================================================
# 0. DIAGNÓSTICO DE PRODUCTOS (solo lectura)
# ==================================================
# productos.csv no se filtra ni se reescribe acá (eso lo hace
# load-to-mysql.py al momento de cargarlo, completando categorías
# faltantes con el clasificador). Este bloque solo deja evidencia
# real de su calidad de datos.

archivo_productos = DATASET_DIR / "productos.csv"

df_productos_diag = pd.read_csv(
    archivo_productos,
    encoding="utf-8",
    dtype={"id": str},
    low_memory=False,
)
df_productos_diag.columns = df_productos_diag.columns.str.strip().str.lower()

diagnostico_calidad(df_productos_diag, "productos.csv (crudo)")

for columna in ("categoria_1", "categoria_2", "categoria_3"):
    if columna in df_productos_diag.columns:
        df_productos_diag[columna] = (
            df_productos_diag[columna].fillna("").astype(str).str.strip()
        )

sin_categoria = (
    (df_productos_diag.get("categoria_1", "") == "")
    & (df_productos_diag.get("categoria_2", "") == "")
    & (df_productos_diag.get("categoria_3", "") == "")
)
print(f"\nProductos sin ninguna categoría asignada: {sin_categoria.sum()} de {len(df_productos_diag)}")

ids_duplicados = df_productos_diag["id"].duplicated().sum()
print(f"IDs de producto duplicados: {ids_duplicados}")


# ==================================================
# 1. FILTRAR SUCURSALES DE CÓRDOBA
# ==================================================

archivo_sucursales = DATASET_DIR / "sucursales.csv"

df_sucursales = pd.read_csv(
    archivo_sucursales,
    encoding="utf-8"
)

# Limpiar nombres de columnas
df_sucursales.columns = (
    df_sucursales.columns
    .str.strip()
    .str.lower()
)

diagnostico_calidad(df_sucursales, "sucursales.csv (crudo)")

print("\nProvincias encontradas:")
print(
    df_sucursales["provincia"]
    .value_counts(dropna=False)
)

# Filtrar Córdoba (AR-X)
df_sucursales_cordoba = df_sucursales[
    df_sucursales["provincia"]
    .astype(str)
    .str.strip()
    == "AR-X"
].copy()

# Normalizar IDs
df_sucursales_cordoba["id"] = (
    df_sucursales_cordoba["id"]
    .astype(str)
    .str.strip()
)

# Normalizar textos: recorta espacios innecesarios y colapsa espacios
# internos en las columnas de nombre/dirección (no resuelve
# diferencias de escritura más profundas -p. ej. mayúsculas o
# abreviaturas distintas para el mismo comercio-, pero reduce
# duplicados triviales por espacios).
columnas_texto_sucursales = [
    "banderadescripcion", "comerciorazonsocial",
    "localidad", "direccion", "sucursalnombre", "sucursaltipo",
]
for columna in columnas_texto_sucursales:
    if columna in df_sucursales_cordoba.columns:
        df_sucursales_cordoba[columna] = normalizar_texto(
            df_sucursales_cordoba[columna]
        )

# Guardar sucursales de Córdoba
archivo_salida_sucursales = (
    OUTPUT_DIR / "sucursales_cordoba.csv"
)

df_sucursales_cordoba.to_csv(
    archivo_salida_sucursales,
    index=False,
    encoding="utf-8"
)

print(f"\nSucursales originales: {len(df_sucursales)}")
print(
    f"Sucursales de Córdoba: "
    f"{len(df_sucursales_cordoba)}"
)


# ==================================================
# 2. UNIR ARCHIVOS DE PRECIOS
# ==================================================

archivos_precios = list(
    DATASET_DIR.glob("precios_*.csv")
)

if not archivos_precios:
    raise FileNotFoundError(
        "No se encontraron archivos precios_*.csv "
        "en la carpeta dataset."
    )


def fecha_de_archivo(path):
    """Extrae la fecha del nombre del archivo (precios_YYYYMMDD_...)
    para poder ordenar los snapshots semanales cronológicamente."""
    coincidencia = re.search(r"precios_(\d{8})", path.stem)
    return coincidencia.group(1) if coincidencia else "00000000"


# Orden cronológico: lo necesitamos para, más abajo, quedarnos con el
# precio más reciente cuando un mismo producto+sucursal aparece en más
# de un archivo semanal.
archivos_precios.sort(key=fecha_de_archivo)

dataframes_precios = []
for archivo in archivos_precios:
    df_archivo = pd.read_csv(
        archivo,
        encoding="utf-8",
        # producto_id debe leerse como texto: si no, pandas infiere
        # int64 y se pierden los ceros a la izquierda del código de
        # barras (ej: "0000000221184" -> 221184), lo que rompe el
        # cruce con productos.id.
        dtype={"producto_id": str, "sucursal_id": str},
    )
    df_archivo["_archivo_fecha"] = fecha_de_archivo(archivo)
    dataframes_precios.append(df_archivo)

df_precios = pd.concat(dataframes_precios, ignore_index=True)

# Limpiar nombres de columnas
df_precios.columns = (
    df_precios.columns
    .str.strip()
    .str.lower()
)
# _archivo_fecha se pierde el lower() porque ya estaba en minúsculas,
# no hace falta volver a asignarla.

# Normalizar sucursal_id / producto_id
df_precios["sucursal_id"] = df_precios["sucursal_id"].astype(str).str.strip()
df_precios["producto_id"] = df_precios["producto_id"].astype(str).str.strip()

diagnostico_calidad(
    df_precios.drop(columns=["_archivo_fecha"]),
    "precios_*.csv (crudo, todas las semanas unidas)",
)

precios_no_numericos = pd.to_numeric(
    df_precios["precio"], errors="coerce"
).isna().sum()
print(
    f"\nFilas con precio no numérico (texto/ilegible): "
    f"{precios_no_numericos}"
)

precios_invalidos_crudo = (
    pd.to_numeric(df_precios["precio"], errors="coerce") <= 0
).sum()
print(f"Filas con precio <= 0 (crudo, antes de filtrar): {precios_invalidos_crudo}")

print(
    f"\nArchivos de precios unidos: "
    f"{len(archivos_precios)}"
)

print(
    f"Precios originales: "
    f"{len(df_precios)}"
)


# ==================================================
# 3. FILTRAR PRECIOS DE CÓRDOBA
# ==================================================

ids_sucursales_cordoba = set(
    df_sucursales_cordoba["id"]
)

df_precios_cordoba = df_precios[
    df_precios["sucursal_id"].isin(
        ids_sucursales_cordoba
    )
].copy()

precios_cordoba_antes_dedupe = len(df_precios_cordoba)

# ==================================================
# 3.1 DEDUPLICAR: mismo producto + misma sucursal aparece en varios
# archivos semanales. La tabla `precios` guarda un único precio
# vigente por (producto_id, sucursal_id) -no un historial-, así que
# nos quedamos con el precio del snapshot más reciente.
# ==================================================

df_precios_cordoba = df_precios_cordoba.sort_values("_archivo_fecha")

duplicados_producto_sucursal = df_precios_cordoba.duplicated(
    subset=["producto_id", "sucursal_id"], keep="last"
).sum()

df_precios_cordoba = df_precios_cordoba.drop_duplicates(
    subset=["producto_id", "sucursal_id"], keep="last"
)

print(
    f"\nRegistros duplicados por producto_id+sucursal_id entre "
    f"archivos semanales (se conserva el precio del snapshot más "
    f"reciente): {duplicados_producto_sucursal}"
)

# ==================================================
# 3.2 DESCARTAR PRECIOS INVÁLIDOS (nulos, cero o negativos)
# ==================================================

df_precios_cordoba["precio"] = pd.to_numeric(
    df_precios_cordoba["precio"], errors="coerce"
)

precios_invalidos_cordoba = (
    df_precios_cordoba["precio"].isna() | (df_precios_cordoba["precio"] <= 0)
).sum()

df_precios_cordoba = df_precios_cordoba[
    df_precios_cordoba["precio"] > 0
]

print(
    f"Precios de Córdoba nulos/cero/negativos descartados: "
    f"{precios_invalidos_cordoba}"
)

# Columnas finales (se descarta la columna auxiliar _archivo_fecha)
df_precios_cordoba = df_precios_cordoba[["precio", "producto_id", "sucursal_id"]]

# Guardar precios filtrados
archivo_salida_precios = (
    OUTPUT_DIR / "precios_cordoba.csv"
)

df_precios_cordoba.to_csv(
    archivo_salida_precios,
    index=False,
    encoding="utf-8"
)

print(
    f"\nPrecios de Córdoba (antes de deduplicar/filtrar): "
    f"{precios_cordoba_antes_dedupe}"
)
print(
    f"Precios de Córdoba (final, un precio por producto+sucursal): "
    f"{len(df_precios_cordoba)}"
)

print(
    f"Precios descartados (fuera de Córdoba): "
    f"{len(df_precios) - precios_cordoba_antes_dedupe}"
)


# ==================================================
# FINAL
# ==================================================

print("\n========================================")
print("PROCESAMIENTO FINALIZADO")
print("========================================")

print(
    f"Sucursales: "
    f"{archivo_salida_sucursales}"
)

print(
    f"Precios: "
    f"{archivo_salida_precios}"
)
