import pandas as pd
from pathlib import Path


# ==================================================
# RUTAS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset"
OUTPUT_DIR = DATASET_DIR / "outputs"


# ==================================================
# ARCHIVO
# ==================================================

file_path = OUTPUT_DIR / "precios_cordoba.csv"


# ==================================================
# VERIFICAR ARCHIVO
# ==================================================

if not file_path.exists():
    raise FileNotFoundError(
        f"No se encontró el archivo: {file_path}"
    )


# ==================================================
# LEER CSV
# ==================================================

df = pd.read_csv(
    file_path,
    encoding="utf-8",
    low_memory=False
)


# ==================================================
# NORMALIZAR NOMBRES DE COLUMNAS
# ==================================================

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
)


# ==================================================
# MOSTRAR COLUMNAS
# ==================================================

print("\nColumnas encontradas:")
print(df.columns.tolist())


# ==================================================
# RENOMBRAR COLUMNAS A SNAKE_CASE
# ==================================================

df = df.rename(
    columns={
        "producto_id": "producto_id",
        "sucursal_id": "sucursal_id"
    }
)


# ==================================================
# GUARDAR
# ==================================================

df.to_csv(
    file_path,
    index=False,
    encoding="utf-8"
)


# ==================================================
# RESULTADO
# ==================================================

print("\n========================================")
print("ACTUALIZACIÓN FINALIZADA")
print("========================================")

print(
    f"Registros procesados: {len(df)}"
)

print(
    f"Archivo actualizado:\n{file_path}"
)

print("\nColumnas finales:")
print(df.columns.tolist())
