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

La mayoría de los productos del dataset original no traen `categoria_1/2/3` cargada. `scripts/populate-categories.py` completa lo que puede con un clasificador por palabras clave (`scripts/categorizador.py`) que usa la taxonomía real de [SEPA / Precios Claros](https://www.preciosclaros.gob.ar/#!/productos-informados) — nombre y marca del producto, nada más. Es un heurístico: no viene del dataset original, así que puede tener errores u omisiones, y se puede seguir ajustando agregando palabras clave a `categorizador.py`. Genera dos archivos en `dataset/outputs/`:

- `productos_categorizados.csv`: todos los productos (72038), con `categoria_1/2/3` vacía en los que no se pudo clasificar. Es el que se usa para cargar la tabla `productos` — hacen falta todos, porque si faltara alguno sus precios no podrían insertarse (foreign key).
- `productos_limpios.csv`: solo los que quedaron con alguna categoría, como catálogo "prolijo" para mirar/analizar. Tiene una columna extra `categoria_origen` (`original` / `inferida`) para distinguir qué categorías vienen del dataset y cuáles fueron inferidas.

Hay dos formas de cargar la base, con el mismo resultado:

**Opción A — con Python (`scripts/load-to-mysql.py`)**

1. Copiá `.env.example` a `.env` y completá los datos de conexión a tu MySQL local.
2. Instalá las dependencias: `pip install -r requirements.txt`
3. Corré, en orden:
   ```
   python scripts/clean-up.py
   python scripts/populate-categories.py
   python scripts/load-to-mysql.py
   ```

El script crea la base de datos y las tablas (`sql/00_crear_base_datos.sql`), vacía las tablas existentes y carga `productos_categorizados.csv`, `sucursales_cordoba.csv` y `precios_cordoba.csv` desde `dataset/outputs/`. Filas de precios que no tengan un producto o sucursal correspondiente se descartan y se informan por consola.

**Opción B — un solo script SQL (`sql/fullscript.sql`)**

Después de generar los mismos CSV (pasos 1 y 2 de arriba), corré desde la raíz del proyecto:

```
mysql --local-infile=1 -u root < sql/fullscript.sql
```

Hace lo mismo que la Opción A pero todo en SQL (`LOAD DATA LOCAL INFILE`), sin pasar por Python, y también agrega las columnas calculadas `diferencia_precios` y `variacion_porcentual` a `productos`.

Con la base ya cargada (por cualquiera de las dos opciones), podés correr cualquiera de los scripts de `sql/` (por ejemplo `mysql -u root datos_comercios < sql/01_promedio_por_comercio.sql`).

## Documentación

El diseño y la estructura de la base de datos se encuentran documentados en:

[Diseño de la base de datos](docs/diseno_base_datos.md)