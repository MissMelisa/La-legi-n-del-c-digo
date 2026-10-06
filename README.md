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
├── dataset/
│   ├── productos.csv
│   ├── sucursales.csv
│   ├── precios_20200412_20200413.csv
│   ├── precios_20200419_20200419.csv
│   ├── precios_20200426_20200426.csv
│   ├── precios_20200502_20200503.csv
│   ├── precios_20200518_20200518.csv
│   └── outputs/
│       ├── sucursales_cordoba.csv
│       ├── precios_cordoba.csv
│       ├── productos_limpios.csv
│       └── productos_categorizados.csv
├── scripts/
│   ├── clean-up.py
│   ├── update-columns.py
│   ├── categorizador.py
│   ├── populate-categories.py
│   ├── load-to-mysql.py
│   ├── conexion.py
│   ├── menu.py
│   ├── analisis-pandas-numpy.py
│   └── producto/
│       ├── producto.py
│       ├── sucursal.py
│       ├── precio.py
│       └── productoCRUD.py
├── sql/
│   ├── 00_crear_base_datos.sql
│   ├── 01_promedio_por_comercio.sql
│   ├── 02_maximo_por_categoria.sql
│   ├── 03_minimo_por_producto.sql
│   ├── 04_suma_por_comercio.sql
│   ├── 05_diferencia_por_producto.sql
│   ├── 06_vista_precios_detalle.sql
│   ├── fullscript.sql
│   └── docs/
│       └── diseño_base_datos.md
├── .github/
│   └── pull_request_template.md
├── docker-compose.yml
├── load-data.sh
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

- `dataset/` — CSV originales del dataset SEPA y, en `outputs/`, los archivos generados por los scripts de limpieza y categorización.
- `scripts/` — pipeline de datos (`clean-up.py`, `update-columns.py`, `categorizador.py`, `populate-categories.py`, `load-to-mysql.py`), la conexión a MySQL (`conexion.py`) y la aplicación interactiva (`menu.py` + `producto/` con las clases `Producto`, `Sucursal` y `Precio`, y el acceso a datos `ProductoCRUD`).
- `sql/` — script de creación de la base (`00_crear_base_datos.sql`), las consultas de análisis numeradas, `fullscript.sql` con todo junto y la documentación del diseño en `docs/`.
- `docker-compose.yml` — levanta un MySQL 8.4 local para desarrollo.
- `load-data.sh` — corre el pipeline completo: limpieza y carga a MySQL.

## Cargar los datos a MySQL

1. Copiá `.env.example` a `.env` y completá los datos de conexión a tu MySQL local.
2. Instalá las dependencias: `pip install -r requirements.txt`
3. Corré `python scripts/load-to-mysql.py`

El script crea la base de datos y las tablas (`sql/00_crear_base_datos.sql`), vacía las tablas existentes y carga `dataset/productos.csv` y los CSV de `dataset/outputs/` (`sucursales_cordoba.csv`, `precios_cordoba.csv`). Filas de precios que no tengan un producto o sucursal correspondiente se descartan y se informan por consola.

`precios` tiene clave primaria compuesta `(producto_id, sucursal_id)`: un mismo producto vendido en la misma sucursal aparece en varios de los CSV semanales de `dataset/precios_*.csv`, así que `scripts/clean-up.py` deduplica quedándose con el precio del snapshot más reciente antes de generar `precios_cordoba.csv` (de 174.414 filas originales de Córdoba quedan 99.681 pares producto+sucursal únicos). También descarta filas con precio nulo, cero o negativo. `scripts/load-to-mysql.py` repite esta deduplicación como red de seguridad antes de insertar.

`scripts/clean-up.py` además imprime un diagnóstico de calidad de datos (nulos, duplicados, tipos de datos, productos sin categoría, precios no numéricos) sobre `productos.csv`, `sucursales.csv` y los `precios_*.csv` crudos, antes de filtrar/limpiar.

La mayoría de los productos del dataset original no traen `categoria_1/2/3` cargada. Antes de insertarlos, el loader completa las categorías faltantes con un clasificador por palabras clave (`scripts/categorizador.py`) que usa la taxonomía real de [SEPA / Precios Claros](https://www.preciosclaros.gob.ar/#!/productos-informados). Es un heurístico basado en el nombre y la marca del producto, no viene del dataset original, así que puede tener errores u omisiones — se puede seguir ajustando agregando palabras clave a `categorizador.py`.

`scripts/populate-categories.py` corre el mismo clasificador de forma independiente y guarda el resultado (solo los productos que quedaron con alguna categoría) en `dataset/outputs/productos_limpios.csv`, con una columna extra `categoria_origen` (`original` / `inferida`) para poder distinguir qué categorías vienen del dataset y cuáles fueron inferidas.

Con la base ya cargada, podés correr cualquiera de los scripts de `sql/` (por ejemplo `mysql -u root datos_comercios < sql/01_promedio_por_comercio.sql`).

## Menú interactivo

Con la base ya cargada, `scripts/menu.py` ofrece una aplicación de consola para gestionar productos sin escribir SQL a mano:

```bash
python scripts/menu.py
```

Opciones disponibles:

1. Alta de producto (valida el formato del ID —código de barras o código interno— y que no exista; permite cargar opcionalmente un precio en una sucursal).
2. Baja de producto (elimina el producto y sus precios asociados en una única transacción).
3. Modificación de producto.
4. Búsqueda de productos por nombre.
5. Búsqueda de productos por categoría (busca en `categoria_1`, `categoria_2` y `categoria_3`).
6. Vista de precios por producto y sucursal (usa `vista_precios_detalle`, ver `sql/06_vista_precios_detalle.sql`).

Cuando una búsqueda devuelve más resultados de los que se muestran, el menú lo aclara explícitamente ("hay más; refiná la búsqueda") en vez de imprimir un "Total: 50" que se pueda confundir con el total real.

## Análisis con Pandas y NumPy

Con la base ya cargada, `scripts/analisis-pandas-numpy.py` carga los precios desde MySQL a un DataFrame de Pandas y responde las 5 preguntas de análisis de negocio:

```bash
python scripts/analisis-pandas-numpy.py            # imprime resultados y genera gráficos
python scripts/analisis-pandas-numpy.py --sin-graficos
```

Incluye estadísticas descriptivas (`describe()`), filtros y agrupamientos (`groupby`), operaciones con NumPy (percentiles, atípicos por IQR, índice de precio relativo por producto) y guarda los gráficos en `dataset/outputs/graficos/`.

## Modelo de clases (POO)

`scripts/producto/` contiene las clases del modelo, separadas por responsabilidad:

**Entidades** (representan una fila de una tabla, sin acceder a la base de datos):

- `Producto` — tabla `productos`.
- `Sucursal` — tabla `sucursales`.
- `Precio` — tabla `precios` (la asociativa entre productos y sucursales).

**Infraestructura y acceso a datos** (no son entidades del modelo relacional):

- `ConexionBD` (`scripts/conexion.py`) — administra la conexión a MySQL y expone `ejecutar_consulta()`, `ejecutar_accion()` y `ejecutar_transaccion()` (esta última ejecuta varias acciones como una única transacción, con rollback automático si alguna falla).
- `ProductoCRUD` (`scripts/producto/productoCRUD.py`) — es la única clase que accede a la base de datos: CRUD de productos, búsquedas, alta de precios y consulta de sucursales/vista de precios. Las entidades no se importan entre sí ni acceden a `ConexionBD` directamente, evitando la dependencia circular Producto ⇄ ProductoCRUD.

La baja de un producto (`ProductoCRUD.eliminar`) borra sus precios y el producto en una sola transacción: si el segundo `DELETE` fallara, el primero se revierte, evitando dejar precios huérfanos eliminados sin haber borrado el producto.

## Documentación

El diseño y la estructura de la base de datos se encuentran documentados en:

[Diseño de la base de datos](sql/docs/diseño_base_datos.md)