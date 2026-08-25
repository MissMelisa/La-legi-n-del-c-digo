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
│   └── update-columns.py
├── sql/
│   ├── 00_crear_base_datos.sql
│   ├── 01_promedio_por_comercio.sql
│   ├── 02_maximo_por_categoria.sql
│   ├── 03_minimo_por_producto.sql
│   ├── 04_suma_por_comercio.sql
│   └── 05_diferencia_por_producto.sql
├── requirements.txt
└── README.md

## Documentación

El diseño y la estructura de la base de datos se encuentran documentados en:

[Diseño de la base de datos](docs/diseno_base_datos.md)