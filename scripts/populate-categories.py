import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from categorizador import clasificar


# ==================================================
# RUTAS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset"
OUTPUT_DIR = DATASET_DIR / "outputs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ==================================================
# ARCHIVOS
# ==================================================

archivo_entrada = DATASET_DIR / "productos.csv"
archivo_salida = OUTPUT_DIR / "productos_limpios.csv"


# ==================================================
# LEER PRODUCTOS
# ==================================================

df = pd.read_csv(
    archivo_entrada,
    encoding="utf-8",
    dtype={"id": str},
    low_memory=False
)

productos_originales = len(df)


# ==================================================
# LIMPIAR NOMBRES DE COLUMNAS
# ==================================================

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
)


# ==================================================
# CORREGIR NOMBRES DE CATEGORÍAS
# ==================================================

df = df.rename(
    columns={
        "categoria1": "categoria_1",
        "categoria2": "categoria_2",
        "categoria3": "categoria_3"
    }
)


# ==================================================
# VERIFICAR COLUMNAS
# ==================================================

columnas_categorias = [
    "categoria_1",
    "categoria_2",
    "categoria_3"
]

for columna in columnas_categorias:
    if columna not in df.columns:
        raise ValueError(
            f"No se encontró la columna '{columna}'.\n"
            f"Columnas disponibles: {df.columns.tolist()}"
        )


# ==================================================
# NORMALIZAR CATEGORÍAS
# ==================================================

for columna in columnas_categorias:
    df[columna] = (
        df[columna]
        .fillna("")
        .astype(str)
        .str.strip()
    )


# ==================================================
# COMPLETAR CATEGORÍAS QUE FALTAN
# ==================================================
#
# La gran mayoría de los productos vienen sin categoria_1/2/3 en el
# csv original, así que tratamos de adivinarla por palabras clave
# del nombre/marca (scripts/categorizador.py). Si el producto ya
# tenía categoría cargada la dejamos como está; si no hay forma de
# adivinarla, queda sin clasificar y se descarta más abajo.

sin_categoria = (
    (df["categoria_1"] == "") &
    (df["categoria_2"] == "") &
    (df["categoria_3"] == "")
)

df["categoria_origen"] = "original"
df.loc[sin_categoria, "categoria_origen"] = "sin clasificar"

inferidas = 0

for idx in df.index[sin_categoria]:
    cat1, cat2, cat3 = clasificar(
        df.at[idx, "nombre"],
        df.at[idx, "marca"],
    )
    if cat1 is not None:
        df.at[idx, "categoria_1"] = cat1
        df.at[idx, "categoria_2"] = cat2
        df.at[idx, "categoria_3"] = cat3
        df.at[idx, "categoria_origen"] = "inferida"
        inferidas += 1


# ==================================================
# IDENTIFICAR PRODUCTOS SIN CLASIFICAR
# ==================================================

sin_clasificar = df["categoria_origen"] == "sin clasificar"


# ==================================================
# ELIMINAR PRODUCTOS SIN CLASIFICAR
# ==================================================

productos_eliminados = sin_clasificar.sum()

df_limpio = df[~sin_clasificar].copy()


# ==================================================
# GUARDAR PRODUCTOS LIMPIOS
# ==================================================

df_limpio.to_csv(
    archivo_salida,
    index=False,
    encoding="utf-8"
)


# ==================================================
# RESULTADOS
# ==================================================

print("\n========================================")
print("PROCESAMIENTO DE PRODUCTOS FINALIZADO")
print("========================================")

print(
    f"Productos originales: {productos_originales}"
)

print(
    f"Ya venían clasificados: "
    f"{(df['categoria_origen'] == 'original').sum()}"
)

print(
    f"Clasificados por palabras clave (heurístico): {inferidas}"
)

print(
    f"Productos eliminados sin clasificar: "
    f"{productos_eliminados}"
)

print(
    f"Productos restantes: {len(df_limpio)}"
)

print("\nColumnas finales:")
print(df_limpio.columns.tolist())

print(
    f"\nArchivo generado:\n{archivo_salida}"
)
