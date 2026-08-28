
import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset"
OUTPUT_DIR = DATASET_DIR / "outputs"

# Crear carpeta outputs si no existe
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


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

print("Provincias encontradas:")
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

df_precios = pd.concat(
    [
        pd.read_csv(
            archivo,
            encoding="utf-8"
        )
        for archivo in archivos_precios
    ],
    ignore_index=True
)

# Limpiar nombres de columnas
df_precios.columns = (
    df_precios.columns
    .str.strip()
    .str.lower()
)

# Normalizar sucursal_id
df_precios["sucursal_id"] = (
    df_precios["sucursal_id"]
    .astype(str)
    .str.strip()
)

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
    f"Precios de Córdoba: "
    f"{len(df_precios_cordoba)}"
)

print(
    f"Precios descartados: "
    f"{len(df_precios) - len(df_precios_cordoba)}"
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
