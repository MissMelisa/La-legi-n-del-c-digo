import os
import numpy as np
import pandas as pd
from sqlalchemy import create_engine


# ==========================================
# 1. CONEXIÓN A MYSQL
# ==========================================

host = os.getenv("MYSQL_HOST", "localhost")
port = os.getenv("MYSQL_PORT", "3306")
user = os.getenv("MYSQL_USER", "root")
password = os.getenv("MYSQL_PASSWORD", "")
database = os.getenv("MYSQL_DATABASE", "datos_comercios")

conexion = create_engine(
    f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
)


# ==========================================
# 2. CARGAR DATOS DESDE MYSQL
# ==========================================

consulta = """
SELECT
    pr.precio,
    p.id AS producto_id,
    p.nombre AS producto,
    p.marca,
    p.categoria_1,
    s.id AS sucursal_id,
    s.comercio_razon_social AS comercio,
    s.localidad,
    s.sucursal_tipo
FROM precios pr
INNER JOIN productos p
    ON pr.producto_id = p.id
INNER JOIN sucursales s
    ON pr.sucursal_id = s.id
"""

df = pd.read_sql(consulta, conexion)

print("\n===== DATOS CARGADOS =====")
print("Cantidad de filas:", len(df))
print("Cantidad de columnas:", len(df.columns))
print("\nPrimeras filas:")
print(df.head())


# ==========================================
# 3. ESTADÍSTICAS DESCRIPTIVAS
# ==========================================

print("\n===== ESTADÍSTICAS DE PRECIOS =====")

print(df["precio"].describe())


# ==========================================
# 4. FILTROS
# ==========================================

print("\n===== FILTROS =====")

# Filtro 1: productos de la categoría Almacén
almacen = df[df["categoria_1"] == "Almacén"]

print("\nProductos de categoría Almacén:")
print(almacen.head())

# Filtro 2: productos con precio mayor a la mediana
mediana = df["precio"].median()

precios_altos = df[df["precio"] > mediana]

print("\nProductos con precio mayor a la mediana:")
print(precios_altos.head())


# ==========================================
# 5. GROUPBY
# ==========================================

print("\n===== PRECIO PROMEDIO POR COMERCIO =====")

promedio_comercio = df.groupby("comercio")["precio"].mean()

print(promedio_comercio)


print("\n===== PRECIO PROMEDIO POR CATEGORÍA =====")

promedio_categoria = df.groupby("categoria_1")["precio"].mean()

print(promedio_categoria)


# ==========================================
# 6. NUMPY
# ==========================================

print("\n===== OPERACIONES CON NUMPY =====")

precios = df["precio"].to_numpy()

promedio = np.mean(precios)
maximo = np.max(precios)
minimo = np.min(precios)

print("Precio promedio:", promedio)
print("Precio máximo:", maximo)
print("Precio mínimo:", minimo)

# Percentil 50 = mediana
percentil_50 = np.percentile(precios, 50)

print("Percentil 50:", percentil_50)


# ==========================================
# 7. PREGUNTA 1
# ==========================================

print("\n===== PREGUNTA 1 =====")
print("¿Cuál es el precio promedio de los productos según cada comercio?")

pregunta_1 = (
    df.groupby("comercio")["precio"]
    .mean()
    .sort_values(ascending=False)
)

print(pregunta_1)


# ==========================================
# 8. PREGUNTA 2
# ==========================================

print("\n===== PREGUNTA 2 =====")
print("¿Cuál es el precio máximo registrado para cada categoría?")

pregunta_2 = (
    df.groupby("categoria_1")["precio"]
    .max()
    .sort_values(ascending=False)
)

print(pregunta_2)


# ==========================================
# 9. PREGUNTA 3
# ==========================================

print("\n===== PREGUNTA 3 =====")
print("¿Cuál es el precio mínimo de cada producto?")

pregunta_3 = (
    df.groupby("producto")["precio"]
    .min()
    .sort_values()
)

print(pregunta_3.head(20))


# ==========================================
# 10. PREGUNTA 4
# ==========================================

print("\n===== PREGUNTA 4 =====")
print("¿Cuánto suman los precios de los productos de cada comercio?")

pregunta_4 = (
    df.groupby("comercio")["precio"]
    .sum()
    .sort_values(ascending=False)
)

print(pregunta_4)


# ==========================================
# 11. PREGUNTA 5
# ==========================================

print("\n===== PREGUNTA 5 =====")
print("¿Cuál es la diferencia entre el precio máximo y mínimo de cada producto?")

maximo_producto = df.groupby("producto")["precio"].max()
minimo_producto = df.groupby("producto")["precio"].min()

pregunta_5 = maximo_producto - minimo_producto

pregunta_5 = pregunta_5.sort_values(ascending=False)

print(pregunta_5.head(20))
