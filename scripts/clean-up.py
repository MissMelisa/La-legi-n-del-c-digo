
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

