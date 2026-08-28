# La Legión del Código

Proyecto de análisis de precios y comercios de Córdoba desarrollado para la **Tecnicatura Superior en Ciencias de Datos e Inteligencia Artificial**.

## Descripción

El proyecto utiliza archivos CSV con información sobre productos, precios y sucursales comerciales de Córdoba.

Los datos son procesados, limpiados y almacenados en una base de datos MySQL para realizar diferentes consultas y análisis mediante SQL.

## Tecnologías utilizadas

- Python
- Pandas
- MySQL
- MySQL Workbench
- SQL
- CSV

## Estructura del proyecto

```text
.
├── scripts/
│   ├── clean-up.py
│   ├── update-columns.py
│   ├── categorizador.py
│   ├── populate-categories.py
│   └── load-to-mysql.py
├── sql/
│   ├── 00_crear_base_datos.sql
│   ├── 01_promedio_por_comercio.sql
│   ├── 02_maximo_por_categoria.sql
│   ├── 03_minimo_por_producto.sql
│   ├── 04_suma_por_comercio.sql
│   └── 05_diferencia_por_producto.sql
├── requirements.txt
├── .env.example
└── README.md
```

## Cargar los datos a MySQL

1. Copiá `.env.example` a `.env` y completá los datos de conexión a tu MySQL local.
2. Instalá las dependencias: `pip install -r requirements.txt`
3. Corré `python scripts/load-to-mysql.py`

El script crea la base de datos y las tablas (`sql/00_crear_base_datos.sql`), vacía las tablas existentes y carga `dataset/productos.csv` y los CSV de `dataset/outputs/` (`sucursales_cordoba.csv`, `precios_cordoba.csv`). Filas de precios que no tengan un producto o sucursal correspondiente se descartan y se informan por consola.

La mayoría de los productos del dataset original no traen `categoria_1/2/3` cargada. Antes de insertarlos, el loader completa las categorías faltantes con un clasificador por palabras clave (`scripts/categorizador.py`) que usa la taxonomía real de [SEPA / Precios Claros](https://www.preciosclaros.gob.ar/#!/productos-informados). Es un heurístico basado en el nombre y la marca del producto, no viene del dataset original, así que puede tener errores u omisiones — se puede seguir ajustando agregando palabras clave a `categorizador.py`.

`scripts/populate-categories.py` corre el mismo clasificador de forma independiente y guarda el resultado (solo los productos que quedaron con alguna categoría) en `dataset/outputs/productos_limpios.csv`, con una columna extra `categoria_origen` (`original` / `inferida`) para poder distinguir qué categorías vienen del dataset y cuáles fueron inferidas.

Con la base ya cargada, podés correr cualquiera de los scripts de `sql/` (por ejemplo `mysql -u root datos_comercios < sql/01_promedio_por_comercio.sql`).

## Documentación

El diseño y la estructura de la base de datos se encuentran documentados en:

[Diseño de la base de datos](docs/diseno_base_datos.md)