"""
Carga los CSV de dataset/outputs/ a MySQL para poder correr
los scripts de sql/.

Uso:
    python scripts/load-to-mysql.py
    python scripts/load-to-mysql.py --skip-schema
    python scripts/load-to-mysql.py --no-truncate

Configuración (variables de entorno o archivo .env en la raíz
del proyecto):
    MYSQL_HOST      (default: localhost)
    MYSQL_PORT      (default: 3306)
    MYSQL_USER      (default: root)
    MYSQL_PASSWORD  (default: "")
    MYSQL_DATABASE  (default: datos_comercios)
"""

import argparse
import os
import re
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

sys.path.insert(0, str(Path(__file__).resolve().parent))
from categorizador import clasificar

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ==================================================
# RUTAS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset"
OUTPUT_DIR = DATASET_DIR / "outputs"
SQL_DIR = BASE_DIR / "sql"

SCHEMA_SQL = SQL_DIR / "00_crear_base_datos.sql"


# ==================================================
# CONEXIÓN
# ==================================================

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "datos_comercios")


def build_engine(database=None):
    from urllib.parse import quote_plus

    url = (
        f"mysql+pymysql://{MYSQL_USER}:{quote_plus(MYSQL_PASSWORD)}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}"
    )
    if database:
        url += f"/{database}"

    return create_engine(url)


# ==================================================
# 1. CREAR BASE DE DATOS Y TABLAS
# ==================================================

def crear_schema():
    if not SCHEMA_SQL.exists():
        raise FileNotFoundError(f"No se encontró: {SCHEMA_SQL}")

    print(f"Ejecutando {SCHEMA_SQL.name}...")

    sql_text = SCHEMA_SQL.read_text(encoding="utf-8")

    # Quitar comentarios de línea antes de separar por ';'
    sql_text = re.sub(r"--.*", "", sql_text)

    statements = [
        s.strip() for s in sql_text.split(";") if s.strip()
    ]

    engine = build_engine()
    with engine.begin() as conn:
        for statement in statements:
            # SHOW TABLES es solo informativo, no hace falta acá
            if statement.upper().startswith("SHOW"):
                continue
            conn.execute(text(statement))

    print("Base de datos y tablas listas.\n")


# ==================================================
# 2. LECTURA DE CSVs
# ==================================================

# Columnas que deben leerse como texto para no perder ceros
# a la izquierda (ej: "0000000221184") ni comas de miles.
ID_COLUMNS = {
    "id",
    "producto_id",
    "sucursal_id",
    "comercioid",
    "banderaid",
}


def leer_csv(path, columnas_esperadas):
    if not path.exists():
        raise FileNotFoundError(f"No se encontró: {path}")

    df = pd.read_csv(
        path,
        encoding="utf-8",
        dtype={col: str for col in ID_COLUMNS},
        low_memory=False,
    )

    df.columns = df.columns.str.strip().str.lower()

    faltantes = set(columnas_esperadas) - set(df.columns)
    if faltantes:
        raise ValueError(
            f"{path.name}: faltan columnas {faltantes}. "
            f"Columnas disponibles: {df.columns.tolist()}"
        )

    return df


def cargar_productos():
    # Cargamos el productos.csv completo, no el productos_limpios.csv
    # filtrado, porque si no un montón de producto_id de
    # precios_cordoba.csv no iban a encontrar su producto (foreign
    # key) y se caían esos precios: productos_limpios.csv descarta
    # justamente los productos que no se pudieron categorizar.
    columnas = [
        "id", "marca", "nombre", "presentacion",
        "categoria_1", "categoria_2", "categoria_3",
    ]

    df = pd.read_csv(
        DATASET_DIR / "productos.csv",
        encoding="utf-8",
        dtype={col: str for col in ID_COLUMNS},
        low_memory=False,
    )
    df.columns = df.columns.str.strip().str.lower()
    df = df.rename(columns={
        "categoria1": "categoria_1",
        "categoria2": "categoria_2",
        "categoria3": "categoria_3",
    })

    faltantes = set(columnas) - set(df.columns)
    if faltantes:
        raise ValueError(
            f"productos.csv: faltan columnas {faltantes}. "
            f"Columnas disponibles: {df.columns.tolist()}"
        )

    for columna in ("categoria_1", "categoria_2", "categoria_3"):
        df[columna] = df[columna].fillna("").astype(str).str.strip()

    # Completamos las categorías que falten con el mismo
    # clasificador de scripts/populate-categories.py, pero acá no
    # descartamos a los que no se puedan clasificar: los necesitamos
    # cargados igual para que las foreign keys de precios cierren.
    sin_categoria = (
        (df["categoria_1"] == "") &
        (df["categoria_2"] == "") &
        (df["categoria_3"] == "")
    )
    inferidas = 0
    for idx in df.index[sin_categoria]:
        cat1, cat2, cat3 = clasificar(
            df.at[idx, "nombre"], df.at[idx, "marca"]
        )
        if cat1 is not None:
            df.at[idx, "categoria_1"] = cat1
            df.at[idx, "categoria_2"] = cat2
            df.at[idx, "categoria_3"] = cat3
            inferidas += 1

    print(
        f"  Categorías completadas por palabras clave: {inferidas} "
        f"de {sin_categoria.sum()} productos sin categoría."
    )

    return df[columnas]


def cargar_sucursales():
    # sucursales_cordoba.csv todavía puede tener los nombres
    # de columna "crudos" (sin normalizar a snake_case).
    columnas_crudas = {
        "comercioid": "comercio_id",
        "banderaid": "bandera_id",
        "banderadescripcion": "bandera_descripcion",
        "comerciorazonsocial": "comercio_razon_social",
        "sucursalnombre": "sucursal_nombre",
        "sucursaltipo": "sucursal_tipo",
    }

    df = pd.read_csv(
        OUTPUT_DIR / "sucursales_cordoba.csv",
        encoding="utf-8",
        dtype={col: str for col in ID_COLUMNS},
        low_memory=False,
    )
    df.columns = df.columns.str.strip().str.lower()
    df = df.rename(columns=columnas_crudas)

    columnas = [
        "id", "comercio_id", "bandera_id", "bandera_descripcion",
        "comercio_razon_social", "provincia", "localidad",
        "direccion", "lat", "lng", "sucursal_nombre", "sucursal_tipo",
    ]

    faltantes = set(columnas) - set(df.columns)
    if faltantes:
        raise ValueError(
            f"sucursales_cordoba.csv: faltan columnas {faltantes}. "
            f"Columnas disponibles: {df.columns.tolist()}"
        )

    df["comercio_id"] = pd.to_numeric(df["comercio_id"], errors="coerce")
    df["bandera_id"] = pd.to_numeric(df["bandera_id"], errors="coerce")

    return df[columnas]


def cargar_precios(productos_ids=None, sucursales_ids=None):
    columnas = ["precio", "producto_id", "sucursal_id"]
    df = leer_csv(OUTPUT_DIR / "precios_cordoba.csv", columnas)
    df["precio"] = pd.to_numeric(df["precio"], errors="coerce")
    df = df[columnas]

    total = len(df)

    # A veces precios_cordoba.csv trae un producto_id o sucursal_id
    # que no existe en lo que ya cargamos, y eso rompe la foreign
    # key de `precios`. Los filtramos acá antes de insertar y
    # avisamos cuántos fueron para que no quede algo silencioso.
    if productos_ids is not None:
        df = df[df["producto_id"].isin(productos_ids)]
    if sucursales_ids is not None:
        df = df[df["sucursal_id"].isin(sucursales_ids)]

    descartados = total - len(df)
    if descartados:
        print(
            f"  Aviso: se descartaron {descartados} de {total} "
            "filas de precios_cordoba.csv por no tener un "
            "producto_id/sucursal_id existente en productos "
            "o sucursales (foreign key)."
        )

    return df


# ==================================================
# 3. CARGA A MYSQL
# ==================================================

def truncar_tablas(engine):
    print("Vaciando tablas existentes...")
    with engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        for tabla in ("precios", "sucursales", "productos"):
            conn.execute(text(f"TRUNCATE TABLE {tabla}"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))


def cargar_tabla(engine, df, tabla):
    df.to_sql(
        tabla,
        engine,
        if_exists="append",
        index=False,
        chunksize=5000,
        method="multi",
    )
    print(f"  {tabla}: {len(df)} filas cargadas")


# ==================================================
# MAIN
# ==================================================

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Carga los CSV de dataset/outputs/ a MySQL "
            f"(base de datos '{MYSQL_DATABASE}')."
        )
    )
    parser.add_argument(
        "--skip-schema",
        action="store_true",
        help="No ejecutar sql/00_crear_base_datos.sql antes de cargar.",
    )
    parser.add_argument(
        "--no-truncate",
        action="store_true",
        help="No vaciar las tablas antes de cargar (hace INSERT/append).",
    )
    args = parser.parse_args()

    if not args.skip_schema:
        crear_schema()

    print("Leyendo CSVs de dataset/outputs/...")
    df_productos = cargar_productos()
    df_sucursales = cargar_sucursales()
    df_precios = cargar_precios(
        productos_ids=set(df_productos["id"]),
        sucursales_ids=set(df_sucursales["id"]),
    )

    engine = build_engine(MYSQL_DATABASE)

    if not args.no_truncate:
        truncar_tablas(engine)

    print("\nCargando datos:")
    cargar_tabla(engine, df_productos, "productos")
    cargar_tabla(engine, df_sucursales, "sucursales")
    cargar_tabla(engine, df_precios, "precios")

    print("\n========================================")
    print("CARGA A MYSQL FINALIZADA")
    print("========================================")
    print(f"Base de datos: {MYSQL_DATABASE}")
    print("Ya podés correr los scripts de sql/ (01, 02, 03, ...).")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nError: {exc}", file=sys.stderr)
        sys.exit(1)
