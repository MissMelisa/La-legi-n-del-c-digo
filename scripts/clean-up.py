import pandas as pd
from pathlib import Path

dataset_path = Path("dataset")

archivo_original = dataset_path / "sucursales.csv"

df = pd.read_csv(archivo_original, encoding="utf-8")

# limpiar nombres de columnas
df.columns = df.columns.str.strip().str.lower()

# ver qué provincias hay
print("Provincias encontradas:")
print(df["provincia"].value_counts(dropna=False))

# conservar solamente Córdoba
df_cordoba = df[df["provincia"].astype(str).str.strip() == "AR-X"]

# guardar resultado
df_cordoba.to_csv(
    "dataset/outputs/sucursales_cordoba.csv",
    index=False,
    encoding="utf-8"
)

print(f"\nRegistros originales: {len(df)}")
print(f"Registros de Córdoba: {len(df_cordoba)}")

archivos_precios = list(dataset_path.glob("precios_*.csv"))

df_precios = pd.concat(
    [pd.read_csv(archivo, encoding="utf-8") for archivo in archivos_precios],
    ignore_index=True
)

df_precios.to_csv(
    dataset_path / "outputs/precios.csv",
    index=False,
    encoding="utf-8"
)

print(f"\nArchivos de precios unidos: {len(archivos_precios)}")
print(f"Registros totales de precios: {len(df_precios)}")
