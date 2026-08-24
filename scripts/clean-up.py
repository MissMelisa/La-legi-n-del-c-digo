import pandas as pd

archivo_original = "/Users/riosmelisa/Desktop/dataset/sucursales.csv"

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
    "/Users/riosmelisa/Desktop/dataset/sucursales_cordoba.csv",
    index=False,
    encoding="utf-8"
)

print(f"\nRegistros originales: {len(df)}")
print(f"Registros de Córdoba: {len(df_cordoba)}")

